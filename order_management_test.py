#!/usr/bin/env python3
"""
Backend API Testing for Order Management System with Order Numbers and Cooking Status
Tests comprehensive order management updates including order numbers, cooking status, and view orders functionality
"""

import requests
import json
import sys
import os
import re
from datetime import datetime

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading backend URL: {e}")
        return None

BASE_URL = get_backend_url()
if not BASE_URL:
    print("❌ Could not get backend URL from frontend/.env")
    sys.exit(1)

API_URL = f"{BASE_URL}/api"
print(f"🔗 Testing backend at: {API_URL}")

# Test data for order management system testing
SAMPLE_ORDER_DATA = {
    "customerName": "Order Number Test Customer",
    "items": [
        {"name": "Tea", "quantity": 2},
        {"name": "Coffee", "quantity": 1}
    ],
    "paymentMethod": "cash"
}

SAMPLE_ORDER_DATA_2 = {
    "customerName": "Cooking Status Test Customer",
    "items": [
        {"name": "Chicken Biryani", "quantity": 1},
        {"name": "Dosa", "quantity": 2}
    ],
    "paymentMethod": "zelle"
}

# Global variables for test data
auth_token = None
created_order_id = None
created_order_number = None
created_order_id_2 = None

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print('='*60)

def print_result(success, message):
    status = "✅" if success else "❌"
    print(f"{status} {message}")

def get_auth_token():
    """Get authentication token for protected endpoints"""
    global auth_token
    try:
        response = requests.post(f"{API_URL}/auth/login", json={
            "username": "admin",
            "password": "memfamous2025"
        })
        if response.status_code == 200:
            auth_token = response.json()["access_token"]
            print_result(True, "Authentication successful")
            return True
        else:
            print_result(False, f"Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Authentication error: {str(e)}")
        return False

def test_order_creation_with_order_numbers():
    """Test creating new orders generates unique order numbers (ORD-ABC123 format)"""
    print_test_header("Order Creation with Order Numbers")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.post(f"{API_URL}/orders/", json=SAMPLE_ORDER_DATA, headers=headers)
        
        if response.status_code == 201:
            order = response.json()
            
            # Verify order number exists and has correct format
            if "orderNumber" not in order:
                print_result(False, "Order missing orderNumber field")
                return False
            
            order_number = order["orderNumber"]
            # Check format: ORD-ABC123 (ORD- followed by 3 letters and 3 numbers)
            if not re.match(r'^ORD-[A-Z]{3}[0-9]{3}$', order_number):
                print_result(False, f"Order number format incorrect: {order_number} (expected ORD-ABC123)")
                return False
            
            print_result(True, f"Order created with valid order number: {order_number}")
            
            # Verify no phone number field (removed from system)
            if "phoneNumber" in order:
                print_result(False, f"Order should not have phoneNumber field, but found: {order.get('phoneNumber')}")
                return False
            
            print_result(True, "Order correctly has no phoneNumber field")
            
            # Verify items have cooking_status field defaulting to "not started"
            for i, item in enumerate(order["items"]):
                if "cooking_status" not in item:
                    print_result(False, f"Item {i+1} missing cooking_status field")
                    return False
                if item["cooking_status"] != "not started":
                    print_result(False, f"Item {i+1} cooking_status should default to 'not started', got '{item['cooking_status']}'")
                    return False
            
            print_result(True, "All items have cooking_status defaulting to 'not started'")
            
            # Verify pricing still works correctly
            expected_total = 7.00  # Tea: $2.00 x 2 + Coffee: $3.00 x 1
            if abs(order["totalAmount"] - expected_total) > 0.01:
                print_result(False, f"Total amount incorrect: expected ${expected_total:.2f}, got ${order['totalAmount']:.2f}")
                return False
            
            print_result(True, f"Pricing calculations correct: ${order['totalAmount']:.2f}")
            
            # Store order data for later tests
            global created_order_id, created_order_number
            created_order_id = order["id"]
            created_order_number = order_number
            
            return True
        else:
            print_result(False, f"Failed to create order: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error creating order: {str(e)}")
        return False

def test_order_number_lookup():
    """Test /api/orders/myorder/{order_number} endpoint works"""
    print_test_header("Order Number Lookup")
    
    if not created_order_number:
        print_result(False, "No order number available from previous test")
        return False
    
    try:
        # Test valid order number lookup
        response = requests.get(f"{API_URL}/orders/myorder/{created_order_number}")
        
        if response.status_code == 200:
            order = response.json()
            
            # Verify we got the correct order
            if order.get("orderNumber") != created_order_number:
                print_result(False, f"Retrieved wrong order: expected {created_order_number}, got {order.get('orderNumber')}")
                return False
            
            if order.get("id") != created_order_id:
                print_result(False, f"Retrieved wrong order ID: expected {created_order_id}, got {order.get('id')}")
                return False
            
            print_result(True, f"Successfully retrieved order by order number: {created_order_number}")
            
            # Test invalid order number format validation
            invalid_formats = ["ORD-ABC12", "ORD-AB123", "ABC-123456", "ORD-1234567"]
            
            for invalid_format in invalid_formats:
                invalid_response = requests.get(f"{API_URL}/orders/myorder/{invalid_format}")
                if invalid_response.status_code != 400:
                    print_result(False, f"Invalid format '{invalid_format}' should return 400, got {invalid_response.status_code}")
                    return False
            
            print_result(True, "Invalid order number formats correctly rejected with 400 status")
            
            # Test order not found scenario
            nonexistent_order = "ORD-ZZZ999"
            not_found_response = requests.get(f"{API_URL}/orders/myorder/{nonexistent_order}")
            if not_found_response.status_code != 404:
                print_result(False, f"Nonexistent order should return 404, got {not_found_response.status_code}")
                return False
            
            print_result(True, "Nonexistent order correctly returns 404 status")
            
            return True
        else:
            print_result(False, f"Order lookup failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing order lookup: {str(e)}")
        return False

def test_view_orders_by_item():
    """Test /api/orders/view-orders endpoint (requires authentication)"""
    print_test_header("View Orders by Item")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Create a second order for better testing
        response2 = requests.post(f"{API_URL}/orders/", json=SAMPLE_ORDER_DATA_2, headers=headers)
        if response2.status_code == 201:
            order2 = response2.json()
            global created_order_id_2
            created_order_id_2 = order2["id"]
            print_result(True, f"Created second test order: {order2['orderNumber']}")
        
        # Test view-orders endpoint
        response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if response.status_code == 200:
            item_orders = response.json()
            
            if not isinstance(item_orders, list):
                print_result(False, f"Expected list, got {type(item_orders)}")
                return False
            
            if len(item_orders) == 0:
                print_result(False, "No item orders returned")
                return False
            
            print_result(True, f"Retrieved {len(item_orders)} item groups")
            
            # Verify orders are grouped by menu items
            found_tea = False
            found_coffee = False
            found_biryani = False
            found_dosa = False
            
            for item_group in item_orders:
                if not isinstance(item_group, dict):
                    print_result(False, f"Item group should be dict, got {type(item_group)}")
                    return False
                
                required_fields = ["item_name", "total_quantity", "orders"]
                for field in required_fields:
                    if field not in item_group:
                        print_result(False, f"Item group missing field: {field}")
                        return False
                
                item_name = item_group["item_name"]
                orders = item_group["orders"]
                
                if item_name == "Tea":
                    found_tea = True
                elif item_name == "Coffee":
                    found_coffee = True
                elif item_name == "Chicken Biryani":
                    found_biryani = True
                elif item_name == "Dosa":
                    found_dosa = True
                
                # Verify each order in the group has required fields
                for order_info in orders:
                    required_order_fields = ["order_id", "orderNumber", "customerName", "quantity", "cooking_status", "orderTime"]
                    for field in required_order_fields:
                        if field not in order_info:
                            print_result(False, f"Order info missing field: {field}")
                            return False
                    
                    # Verify order number format
                    if not re.match(r'^ORD-[A-Z]{3}[0-9]{3}$', order_info["orderNumber"]):
                        print_result(False, f"Invalid order number in view-orders: {order_info['orderNumber']}")
                        return False
                    
                    # Verify cooking status
                    if order_info["cooking_status"] not in ["not started", "cooking", "finished"]:
                        print_result(False, f"Invalid cooking status: {order_info['cooking_status']}")
                        return False
            
            if found_tea and found_coffee:
                print_result(True, "Orders correctly grouped by menu items (Tea and Coffee found)")
            else:
                print_result(False, f"Expected Tea and Coffee items not found in groups")
                return False
            
            print_result(True, "All order info includes order numbers and cooking status")
            
            return True
        else:
            print_result(False, f"View orders failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing view orders: {str(e)}")
        return False

def test_cooking_status_updates():
    """Test /api/orders/cooking-status endpoint (requires authentication)"""
    print_test_header("Cooking Status Updates")
    
    if not auth_token or not created_order_id:
        print_result(False, "No auth token or order ID available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Test updating cooking status from "not started" to "cooking"
        update_data = {
            "order_id": created_order_id,
            "item_name": "Tea",
            "cooking_status": "cooking"
        }
        
        response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") != "cooking":
                print_result(False, f"Expected status 'cooking', got {result.get('status')}")
                return False
            
            print_result(True, "Successfully updated Tea cooking status to 'cooking'")
            
            # Verify the update was persisted by checking the order
            order_response = requests.get(f"{API_URL}/orders/{created_order_id}", headers=headers)
            if order_response.status_code == 200:
                order = order_response.json()
                tea_item = None
                for item in order["items"]:
                    if item["name"] == "Tea":
                        tea_item = item
                        break
                
                if not tea_item:
                    print_result(False, "Tea item not found in order")
                    return False
                
                if tea_item["cooking_status"] != "cooking":
                    print_result(False, f"Tea cooking status not persisted: expected 'cooking', got '{tea_item['cooking_status']}'")
                    return False
                
                print_result(True, "Cooking status update persisted correctly")
            else:
                print_result(False, f"Failed to verify order update: {order_response.status_code}")
                return False
            
            # Test updating to "finished"
            update_data["cooking_status"] = "finished"
            response2 = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
            
            if response2.status_code == 200:
                print_result(True, "Successfully updated Tea cooking status to 'finished'")
            else:
                print_result(False, f"Failed to update to finished: {response2.status_code}")
                return False
            
            # Test invalid cooking status values
            invalid_statuses = ["invalid", "pending", "completed", ""]
            for invalid_status in invalid_statuses:
                invalid_update = {
                    "order_id": created_order_id,
                    "item_name": "Coffee",
                    "cooking_status": invalid_status
                }
                invalid_response = requests.patch(f"{API_URL}/orders/cooking-status", json=invalid_update, headers=headers)
                if invalid_response.status_code not in [400, 422]:
                    print_result(False, f"Invalid status '{invalid_status}' should be rejected, got {invalid_response.status_code}")
                    return False
            
            print_result(True, "Invalid cooking status values correctly rejected")
            
            return True
        else:
            print_result(False, f"Cooking status update failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing cooking status updates: {str(e)}")
        return False

def test_integration_end_to_end():
    """Test complete flow: create order → view in view-orders → update cooking status"""
    print_test_header("Integration Testing End-to-End")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Step 1: Create a new order
        integration_order_data = {
            "customerName": "Integration Test Customer",
            "items": [
                {"name": "Coffee", "quantity": 1}
            ],
            "paymentMethod": "cashapp"
        }
        
        create_response = requests.post(f"{API_URL}/orders/", json=integration_order_data, headers=headers)
        if create_response.status_code != 201:
            print_result(False, f"Failed to create integration test order: {create_response.status_code}")
            return False
        
        integration_order = create_response.json()
        integration_order_id = integration_order["id"]
        integration_order_number = integration_order["orderNumber"]
        
        print_result(True, f"Step 1: Created integration test order {integration_order_number}")
        
        # Step 2: Verify order appears in view-orders
        view_response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        if view_response.status_code != 200:
            print_result(False, f"Failed to get view-orders: {view_response.status_code}")
            return False
        
        item_orders = view_response.json()
        found_integration_order = False
        
        for item_group in item_orders:
            if item_group["item_name"] == "Coffee":
                for order_info in item_group["orders"]:
                    if order_info["orderNumber"] == integration_order_number:
                        found_integration_order = True
                        if order_info["cooking_status"] != "not started":
                            print_result(False, f"Expected 'not started', got '{order_info['cooking_status']}'")
                            return False
                        break
        
        if not found_integration_order:
            print_result(False, "Integration order not found in view-orders")
            return False
        
        print_result(True, "Step 2: Order found in view-orders with correct cooking status")
        
        # Step 3: Update cooking status
        update_data = {
            "order_id": integration_order_id,
            "item_name": "Coffee",
            "cooking_status": "cooking"
        }
        
        update_response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
        if update_response.status_code != 200:
            print_result(False, f"Failed to update cooking status: {update_response.status_code}")
            return False
        
        print_result(True, "Step 3: Updated cooking status to 'cooking'")
        
        # Step 4: Verify customer can lookup order by order number
        lookup_response = requests.get(f"{API_URL}/orders/myorder/{integration_order_number}")
        if lookup_response.status_code != 200:
            print_result(False, f"Customer lookup failed: {lookup_response.status_code}")
            return False
        
        customer_order = lookup_response.json()
        if customer_order["orderNumber"] != integration_order_number:
            print_result(False, "Customer got wrong order")
            return False
        
        print_result(True, "Step 4: Customer successfully looked up order by order number")
        
        # Step 5: Verify pricing functionality preserved
        if abs(customer_order["totalAmount"] - 3.00) > 0.01:  # Coffee is $3.00
            print_result(False, f"Pricing not preserved: expected $3.00, got ${customer_order['totalAmount']:.2f}")
            return False
        
        print_result(True, "Step 5: All pricing functionality preserved")
        
        print_result(True, "🎉 Complete end-to-end integration test PASSED!")
        return True
        
    except Exception as e:
        print_result(False, f"Error in integration test: {str(e)}")
        return False

def run_order_management_tests():
    """Run all order management system tests"""
    print(f"🚀 Starting Order Management System Tests")
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔄 Testing comprehensive order management updates with order numbers and cooking status")
    
    # Get authentication token first
    if not get_auth_token():
        print("❌ Cannot proceed without authentication")
        return False
    
    # Run all tests in priority order
    tests = [
        ("Order Creation with Order Numbers", test_order_creation_with_order_numbers, "HIGH"),
        ("Order Number Lookup", test_order_number_lookup, "HIGH"),
        ("View Orders by Item", test_view_orders_by_item, "HIGH"),
        ("Cooking Status Updates", test_cooking_status_updates, "HIGH"),
        ("Integration Testing End-to-End", test_integration_end_to_end, "MEDIUM")
    ]
    
    results = []
    for test_name, test_func, priority in tests:
        try:
            print(f"\n🎯 Priority: {priority}")
            result = test_func()
            results.append((test_name, result, priority))
        except Exception as e:
            print_result(False, f"Test {test_name} crashed: {str(e)}")
            results.append((test_name, False, priority))
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 ORDER MANAGEMENT SYSTEM TEST SUMMARY")
    print('='*60)
    
    passed = 0
    total = len(results)
    high_priority_passed = 0
    high_priority_total = 0
    
    for test_name, result, priority in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} [{priority}] {test_name}")
        if result:
            passed += 1
        if priority == "HIGH":
            high_priority_total += 1
            if result:
                high_priority_passed += 1
    
    print(f"\n🎯 Overall Results: {passed}/{total} tests passed")
    print(f"🔥 High Priority Results: {high_priority_passed}/{high_priority_total} tests passed")
    
    if passed == total:
        print("🎉 All order management tests PASSED!")
        print("✅ Order numbers, cooking status, and view orders functionality working correctly")
        return True
    elif high_priority_passed == high_priority_total:
        print("⚠️  All HIGH PRIORITY tests passed, some medium priority tests failed")
        print("✅ Core order management functionality works correctly")
        return True
    else:
        print("❌ Some HIGH PRIORITY tests FAILED - critical issues found")
        return False

if __name__ == "__main__":
    success = run_order_management_tests()
    sys.exit(0 if success else 1)
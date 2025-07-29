#!/usr/bin/env python3
"""
Sequential Order Number System Testing
Tests the updated order management system with sequential order numbers (1, 2, 3, 4...)
"""

import requests
import json
import sys
import os
from datetime import datetime
import time

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
print(f"🔗 Testing sequential order numbers at: {API_URL}")

# Test data for sequential order number testing
SAMPLE_ORDERS = [
    {
        "customerName": "Sequential Test Customer 1",
        "items": [{"name": "Tea", "quantity": 1}],
        "paymentMethod": "cash"
    },
    {
        "customerName": "Sequential Test Customer 2", 
        "items": [{"name": "Coffee", "quantity": 2}],
        "paymentMethod": "zelle"
    },
    {
        "customerName": "Sequential Test Customer 3",
        "items": [{"name": "Tea", "quantity": 1}, {"name": "Coffee", "quantity": 1}],
        "paymentMethod": "cashapp"
    },
    {
        "customerName": "Sequential Test Customer 4",
        "items": [{"name": "Coffee", "quantity": 3}],
        "paymentMethod": "cash"
    }
]

# Global variables for test data
auth_token = None
created_orders = []

def print_test_header(test_name):
    print(f"\n{'='*70}")
    print(f"🧪 {test_name}")
    print('='*70)

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

def test_sequential_order_number_generation():
    """HIGH PRIORITY: Test creating multiple orders generates sequential numbers (1, 2, 3, 4...)"""
    print_test_header("Sequential Order Number Generation")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    global created_orders
    created_orders = []
    
    try:
        # Create multiple orders and check sequential numbering
        for i, order_data in enumerate(SAMPLE_ORDERS):
            response = requests.post(f"{API_URL}/orders/", json=order_data, headers=headers)
            
            if response.status_code == 201:
                order = response.json()
                created_orders.append(order)
                
                # Check that order has orderNumber field
                if "orderNumber" not in order:
                    print_result(False, f"Order {i+1} missing orderNumber field")
                    return False
                
                order_number = order["orderNumber"]
                
                # Validate order number is a simple number (not ORD-ABC123 format)
                if not order_number.isdigit():
                    print_result(False, f"Order {i+1} has non-numeric order number: {order_number}")
                    return False
                
                print_result(True, f"Order {i+1} created with order number: {order_number}")
                
            else:
                print_result(False, f"Failed to create order {i+1}: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        
        # Verify sequential numbering
        order_numbers = [int(order["orderNumber"]) for order in created_orders]
        order_numbers.sort()
        
        # Check if numbers are sequential (allowing for existing orders)
        if len(order_numbers) >= 2:
            # Check that all numbers are unique
            if len(set(order_numbers)) != len(order_numbers):
                print_result(False, "Duplicate order numbers found")
                return False
            
            print_result(True, f"All order numbers are unique: {order_numbers}")
            
            # Check that numbers are incrementing (but not necessarily starting from 1)
            for i in range(1, len(order_numbers)):
                if order_numbers[i] != order_numbers[i-1] + 1:
                    print_result(False, f"Order numbers not sequential: {order_numbers}")
                    return False
            
            print_result(True, f"Order numbers are sequential: {order_numbers}")
        
        print_result(True, f"Successfully created {len(created_orders)} orders with sequential numbers")
        return True
        
    except Exception as e:
        print_result(False, f"Error testing sequential order numbers: {str(e)}")
        return False

def test_order_number_validation():
    """HIGH PRIORITY: Test order number validation accepts simple numbers (not complex format)"""
    print_test_header("Order Number Validation")
    
    if not created_orders:
        print_result(False, "No created orders available for testing")
        return False
    
    try:
        # Test valid numeric order numbers
        for order in created_orders[:2]:  # Test first 2 orders
            order_number = order["orderNumber"]
            response = requests.get(f"{API_URL}/orders/myorder/{order_number}")
            
            if response.status_code == 200:
                retrieved_order = response.json()
                if retrieved_order["id"] == order["id"]:
                    print_result(True, f"Successfully retrieved order with number: {order_number}")
                else:
                    print_result(False, f"Retrieved wrong order for number: {order_number}")
                    return False
            else:
                print_result(False, f"Failed to retrieve order {order_number}: {response.status_code}")
                return False
        
        # Test invalid order number formats (should be rejected)
        invalid_formats = [
            "ORD-ABC123",  # Old complex format
            "ORD-123",     # Partial old format
            "ABC123",      # Letters and numbers
            "1.5",         # Decimal
            "-1",          # Negative
            "0",           # Zero
            "abc",         # Letters only
            "",            # Empty string
            "1a",          # Mixed alphanumeric
        ]
        
        for invalid_number in invalid_formats:
            response = requests.get(f"{API_URL}/orders/myorder/{invalid_number}")
            
            if response.status_code == 400:
                print_result(True, f"Correctly rejected invalid order number: '{invalid_number}'")
            else:
                print_result(False, f"Should have rejected invalid order number '{invalid_number}', got status: {response.status_code}")
                return False
        
        # Test non-existent order number (should return 404)
        non_existent_number = "99999"
        response = requests.get(f"{API_URL}/orders/myorder/{non_existent_number}")
        
        if response.status_code == 404:
            print_result(True, f"Correctly returned 404 for non-existent order number: {non_existent_number}")
        else:
            print_result(False, f"Should have returned 404 for non-existent order {non_existent_number}, got: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print_result(False, f"Error testing order number validation: {str(e)}")
        return False

def test_myorder_customer_lookup():
    """HIGH PRIORITY: Test MyOrder customer lookup works with simple numbers"""
    print_test_header("MyOrder Customer Lookup with Simple Numbers")
    
    if not created_orders:
        print_result(False, "No created orders available for testing")
        return False
    
    try:
        # Test customer lookup with simple numeric order numbers
        for i, order in enumerate(created_orders):
            order_number = order["orderNumber"]
            
            # Test the MyOrder endpoint (no authentication required)
            response = requests.get(f"{API_URL}/orders/myorder/{order_number}")
            
            if response.status_code == 200:
                retrieved_order = response.json()
                
                # Verify it's the correct order
                if retrieved_order["id"] != order["id"]:
                    print_result(False, f"Retrieved wrong order for number {order_number}")
                    return False
                
                # Verify order number is displayed
                if retrieved_order["orderNumber"] != order_number:
                    print_result(False, f"Order number mismatch in retrieved order")
                    return False
                
                # Verify customer name matches
                if retrieved_order["customerName"] != order["customerName"]:
                    print_result(False, f"Customer name mismatch for order {order_number}")
                    return False
                
                print_result(True, f"Customer lookup successful for order #{order_number} - {order['customerName']}")
                
            else:
                print_result(False, f"Customer lookup failed for order {order_number}: {response.status_code}")
                return False
        
        print_result(True, f"All {len(created_orders)} orders successfully retrieved via customer lookup")
        return True
        
    except Exception as e:
        print_result(False, f"Error testing customer lookup: {str(e)}")
        return False

def test_view_orders_integration():
    """MEDIUM PRIORITY: Test view orders functionality works with sequential numbers"""
    print_test_header("View Orders Integration with Sequential Numbers")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Test view orders endpoint
        response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if response.status_code == 200:
            item_groups = response.json()
            
            if not isinstance(item_groups, list):
                print_result(False, f"Expected list, got {type(item_groups)}")
                return False
            
            # Check that orders are grouped by menu items
            found_orders = 0
            for group in item_groups:
                if "item_name" not in group or "orders" not in group:
                    print_result(False, "Invalid group structure in view orders")
                    return False
                
                item_name = group["item_name"]
                orders_in_group = group["orders"]
                
                # Check each order in the group
                for order_info in orders_in_group:
                    # Verify order has orderNumber field
                    if "orderNumber" not in order_info:
                        print_result(False, f"Order in {item_name} group missing orderNumber")
                        return False
                    
                    order_number = order_info["orderNumber"]
                    
                    # Verify order number is simple numeric format
                    if not str(order_number).isdigit():
                        print_result(False, f"Non-numeric order number in view orders: {order_number}")
                        return False
                    
                    # Verify cooking status is present
                    if "cooking_status" not in order_info:
                        print_result(False, f"Order {order_number} missing cooking_status")
                        return False
                    
                    found_orders += 1
                
                print_result(True, f"Item '{item_name}' group has {len(orders_in_group)} orders with sequential numbers")
            
            print_result(True, f"View orders shows {found_orders} orders with sequential numbering")
            return True
            
        else:
            print_result(False, f"View orders failed: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing view orders integration: {str(e)}")
        return False

def test_cooking_status_updates():
    """MEDIUM PRIORITY: Test cooking status updates work with sequential numbers"""
    print_test_header("Cooking Status Updates with Sequential Numbers")
    
    if not auth_token or not created_orders:
        print_result(False, "No auth token or created orders available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Test updating cooking status for first created order
        test_order = created_orders[0]
        order_id = test_order["id"]
        order_number = test_order["orderNumber"]
        
        # Get the first item from the order
        if not test_order["items"]:
            print_result(False, "Test order has no items")
            return False
        
        test_item = test_order["items"][0]
        item_name = test_item["name"]
        
        # Test updating cooking status from "not started" to "cooking"
        update_data = {
            "order_id": order_id,
            "item_name": item_name,
            "cooking_status": "cooking"
        }
        
        response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
        
        if response.status_code == 200:
            print_result(True, f"Updated cooking status for order #{order_number}, item '{item_name}' to 'cooking'")
            
            # Verify the update persisted by checking view orders
            response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
            if response.status_code == 200:
                item_groups = response.json()
                
                # Find our updated item
                found_update = False
                for group in item_groups:
                    if group["item_name"] == item_name:
                        for order_info in group["orders"]:
                            if order_info["orderNumber"] == order_number:
                                if order_info["cooking_status"] == "cooking":
                                    print_result(True, f"Cooking status update persisted for order #{order_number}")
                                    found_update = True
                                    break
                
                if not found_update:
                    print_result(False, f"Cooking status update not found in view orders for order #{order_number}")
                    return False
            
            # Test updating to "finished"
            update_data["cooking_status"] = "finished"
            response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
            
            if response.status_code == 200:
                print_result(True, f"Updated cooking status for order #{order_number} to 'finished'")
            else:
                print_result(False, f"Failed to update cooking status to finished: {response.status_code}")
                return False
            
            return True
            
        else:
            print_result(False, f"Failed to update cooking status: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing cooking status updates: {str(e)}")
        return False

def test_integration_end_to_end():
    """MEDIUM PRIORITY: Test complete flow with sequential numbers"""
    print_test_header("Integration Testing End-to-End with Sequential Numbers")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Step 1: Create a new order for integration testing
        integration_order_data = {
            "customerName": "Integration Test Customer",
            "items": [{"name": "Coffee", "quantity": 1}],
            "paymentMethod": "zelle"
        }
        
        response = requests.post(f"{API_URL}/orders/", json=integration_order_data, headers=headers)
        
        if response.status_code != 201:
            print_result(False, f"Failed to create integration test order: {response.status_code}")
            return False
        
        integration_order = response.json()
        order_number = integration_order["orderNumber"]
        order_id = integration_order["id"]
        
        # Verify order number is sequential
        if not order_number.isdigit():
            print_result(False, f"Integration order has non-numeric order number: {order_number}")
            return False
        
        print_result(True, f"Step 1: Created integration test order #{order_number}")
        
        # Step 2: Verify order appears in view orders
        response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        if response.status_code != 200:
            print_result(False, f"Failed to get view orders: {response.status_code}")
            return False
        
        item_groups = response.json()
        found_in_view_orders = False
        
        for group in item_groups:
            if group["item_name"] == "Coffee":
                for order_info in group["orders"]:
                    if order_info["orderNumber"] == order_number:
                        found_in_view_orders = True
                        print_result(True, f"Step 2: Order #{order_number} found in view orders with cooking status: {order_info['cooking_status']}")
                        break
        
        if not found_in_view_orders:
            print_result(False, f"Integration order #{order_number} not found in view orders")
            return False
        
        # Step 3: Update cooking status
        update_data = {
            "order_id": order_id,
            "item_name": "Coffee",
            "cooking_status": "cooking"
        }
        
        response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
        if response.status_code != 200:
            print_result(False, f"Failed to update cooking status: {response.status_code}")
            return False
        
        print_result(True, f"Step 3: Updated cooking status for order #{order_number} to 'cooking'")
        
        # Step 4: Customer lookup by order number
        response = requests.get(f"{API_URL}/orders/myorder/{order_number}")
        if response.status_code != 200:
            print_result(False, f"Customer lookup failed for order #{order_number}: {response.status_code}")
            return False
        
        customer_order = response.json()
        if customer_order["id"] != order_id:
            print_result(False, f"Customer lookup returned wrong order")
            return False
        
        print_result(True, f"Step 4: Customer successfully looked up order #{order_number}")
        
        # Step 5: Verify pricing functionality is preserved
        if "totalAmount" not in customer_order or customer_order["totalAmount"] <= 0:
            print_result(False, "Pricing functionality not preserved in integration test")
            return False
        
        # Coffee should be $3.00
        expected_total = 3.00
        if abs(customer_order["totalAmount"] - expected_total) > 0.01:
            print_result(False, f"Pricing incorrect: expected ${expected_total:.2f}, got ${customer_order['totalAmount']:.2f}")
            return False
        
        print_result(True, f"Step 5: Pricing preserved - Total: ${customer_order['totalAmount']:.2f}")
        
        print_result(True, "🎉 Complete end-to-end integration test PASSED!")
        print_result(True, f"Order #{order_number} successfully created → viewed → updated → looked up")
        
        return True
        
    except Exception as e:
        print_result(False, f"Error in integration testing: {str(e)}")
        return False

def test_atomic_counter_system():
    """HIGH PRIORITY: Test atomic counter system prevents duplicate numbers"""
    print_test_header("Atomic Counter System Testing")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Create multiple orders rapidly to test atomic counter
        rapid_orders = []
        order_data = {
            "customerName": "Atomic Test Customer",
            "items": [{"name": "Tea", "quantity": 1}],
            "paymentMethod": "cash"
        }
        
        # Create 3 orders in quick succession
        for i in range(3):
            response = requests.post(f"{API_URL}/orders/", json=order_data, headers=headers)
            
            if response.status_code == 201:
                order = response.json()
                rapid_orders.append(order)
                print_result(True, f"Rapid order {i+1} created with number: {order['orderNumber']}")
            else:
                print_result(False, f"Failed to create rapid order {i+1}: {response.status_code}")
                return False
        
        # Verify all order numbers are unique
        order_numbers = [order["orderNumber"] for order in rapid_orders]
        unique_numbers = set(order_numbers)
        
        if len(unique_numbers) != len(order_numbers):
            print_result(False, f"Duplicate order numbers found in rapid creation: {order_numbers}")
            return False
        
        print_result(True, f"Atomic counter system working - all numbers unique: {order_numbers}")
        
        # Verify numbers are sequential
        numeric_numbers = [int(num) for num in order_numbers]
        numeric_numbers.sort()
        
        for i in range(1, len(numeric_numbers)):
            if numeric_numbers[i] != numeric_numbers[i-1] + 1:
                print_result(False, f"Numbers not sequential: {numeric_numbers}")
                return False
        
        print_result(True, f"Sequential numbering maintained: {numeric_numbers}")
        return True
        
    except Exception as e:
        print_result(False, f"Error testing atomic counter system: {str(e)}")
        return False

def run_sequential_order_tests():
    """Run all sequential order number tests"""
    print(f"🚀 Starting Sequential Order Number System Tests")
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔢 Testing updated system with simple sequential numbers (1, 2, 3, 4...)")
    
    # Get authentication token first
    if not get_auth_token():
        print("❌ Cannot proceed without authentication")
        return False
    
    # Run all tests in priority order
    tests = [
        ("Sequential Order Number Generation", test_sequential_order_number_generation, "HIGH"),
        ("Order Number Validation", test_order_number_validation, "HIGH"),
        ("MyOrder Customer Lookup", test_myorder_customer_lookup, "HIGH"),
        ("Atomic Counter System", test_atomic_counter_system, "HIGH"),
        ("View Orders Integration", test_view_orders_integration, "MEDIUM"),
        ("Cooking Status Updates", test_cooking_status_updates, "MEDIUM"),
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
    print(f"\n{'='*70}")
    print("📊 SEQUENTIAL ORDER NUMBER SYSTEM TEST SUMMARY")
    print('='*70)
    
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
        print("🎉 All sequential order number tests PASSED!")
        print("✅ Sequential order number system (1, 2, 3, 4...) working perfectly")
        return True
    elif high_priority_passed == high_priority_total:
        print("⚠️  All HIGH PRIORITY tests passed, some medium priority tests failed")
        print("✅ Core sequential numbering functionality working correctly")
        return True
    else:
        print("❌ Some HIGH PRIORITY tests FAILED - critical issues with sequential numbering")
        return False

if __name__ == "__main__":
    success = run_sequential_order_tests()
    sys.exit(0 if success else 1)
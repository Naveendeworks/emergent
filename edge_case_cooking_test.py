#!/usr/bin/env python3
"""
Edge Case Testing for Enhanced Cooking Status Functionality
Tests edge cases like updating already completed orders, concurrent updates, etc.
"""

import requests
import json
import sys
import os
from datetime import datetime
import time
import threading

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

# Test data
EDGE_CASE_ORDER_DATA = {
    "customerName": "Edge Case Test Customer",
    "items": [
        {"name": "Tea", "quantity": 1},
        {"name": "Coffee", "quantity": 1}
    ],
    "paymentMethod": "cash"
}

# Global variables
auth_token = None
edge_case_order_id = None

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

def test_updating_completed_order():
    """Test updating cooking status on already completed orders"""
    print_test_header("Updating Already Completed Orders")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Create an order
        response = requests.post(f"{API_URL}/orders/", json=EDGE_CASE_ORDER_DATA, headers=headers)
        
        if response.status_code != 201:
            print_result(False, f"Failed to create order: {response.status_code}")
            return False
        
        order = response.json()
        global edge_case_order_id
        edge_case_order_id = order["id"]
        
        print_result(True, f"Order created - ID: {order['id']}")
        
        # Complete the order by finishing all items
        for item_name in ["Tea", "Coffee"]:
            update_data = {
                "order_id": edge_case_order_id,
                "item_name": item_name,
                "cooking_status": "finished"
            }
            
            response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
            
            if response.status_code != 200:
                print_result(False, f"Failed to update {item_name} status: {response.status_code}")
                return False
        
        print_result(True, "Order completed by finishing all items")
        
        # Verify order is completed
        response = requests.get(f"{API_URL}/orders/{edge_case_order_id}", headers=headers)
        if response.status_code == 200:
            order = response.json()
            if order.get("status") != "completed":
                print_result(False, f"Order should be completed, got '{order.get('status')}'")
                return False
        
        # Now try to update cooking status on completed order
        update_data = {
            "order_id": edge_case_order_id,
            "item_name": "Tea",
            "cooking_status": "cooking"
        }
        
        response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
        
        # Should handle gracefully (either allow update or return appropriate response)
        if response.status_code == 200:
            result = response.json()
            print_result(True, f"Completed order update handled gracefully: {result.get('message', 'No message')}")
            
            # Should not auto-complete again
            if result.get("order_auto_completed"):
                print_result(False, "Already completed order should not trigger auto-completion again")
                return False
            
            print_result(True, "No duplicate auto-completion triggered")
            return True
        else:
            # If it returns an error, that's also acceptable behavior
            print_result(True, f"Completed order update appropriately rejected with status {response.status_code}")
            return True
        
    except Exception as e:
        print_result(False, f"Error testing completed order updates: {str(e)}")
        return False

def test_rapid_status_updates():
    """Test rapid status updates on same order"""
    print_test_header("Rapid Status Updates on Same Order")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Create an order for rapid updates
        rapid_order_data = {
            "customerName": "Rapid Update Test Customer",
            "items": [{"name": "Tea", "quantity": 1}],
            "paymentMethod": "zelle"
        }
        
        response = requests.post(f"{API_URL}/orders/", json=rapid_order_data, headers=headers)
        
        if response.status_code != 201:
            print_result(False, f"Failed to create rapid test order: {response.status_code}")
            return False
        
        order = response.json()
        rapid_order_id = order["id"]
        
        print_result(True, f"Rapid test order created - ID: {order['id']}")
        
        # Perform rapid status updates
        statuses = ["cooking", "not started", "cooking", "finished"]
        
        for i, status in enumerate(statuses):
            update_data = {
                "order_id": rapid_order_id,
                "item_name": "Tea",
                "cooking_status": status
            }
            
            response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
            
            if response.status_code != 200:
                print_result(False, f"Rapid update {i+1} failed: {response.status_code}")
                return False
            
            result = response.json()
            print_result(True, f"Rapid update {i+1}: {status} - {result.get('message', 'No message')}")
            
            # Only the last update (finished) should trigger auto-completion
            if status == "finished" and not result.get("order_auto_completed"):
                print_result(False, "Final 'finished' update should trigger auto-completion")
                return False
            elif status != "finished" and result.get("order_auto_completed"):
                print_result(False, f"Non-finishing update '{status}' should not trigger auto-completion")
                return False
        
        print_result(True, "All rapid updates processed correctly")
        return True
        
    except Exception as e:
        print_result(False, f"Error testing rapid status updates: {str(e)}")
        return False

def test_view_orders_integration():
    """Test that auto-completed orders appear correctly in view orders"""
    print_test_header("View Orders Integration with Auto-Completed Orders")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Get view orders before creating new order
        response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if response.status_code != 200:
            print_result(False, f"Failed to get view orders: {response.status_code}")
            return False
        
        initial_view_orders = response.json()
        print_result(True, f"Initial view orders count: {len(initial_view_orders)} item groups")
        
        # Create a new order that will be auto-completed
        integration_order_data = {
            "customerName": "View Orders Integration Test",
            "items": [{"name": "Coffee", "quantity": 1}],
            "paymentMethod": "cashapp"
        }
        
        response = requests.post(f"{API_URL}/orders/", json=integration_order_data, headers=headers)
        
        if response.status_code != 201:
            print_result(False, f"Failed to create integration test order: {response.status_code}")
            return False
        
        order = response.json()
        integration_order_id = order["id"]
        order_number = order.get("orderNumber")
        
        print_result(True, f"Integration test order created - ID: {order['id']}, Number: {order_number}")
        
        # Verify it appears in view orders (should be pending)
        response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if response.status_code == 200:
            view_orders = response.json()
            
            # Look for our order in the Coffee group
            found_pending = False
            for item_group in view_orders:
                if item_group.get("item_name") == "Coffee":
                    for order_info in item_group.get("orders", []):
                        if order_info.get("orderNumber") == order_number:
                            found_pending = True
                            if order_info.get("cooking_status") != "not started":
                                print_result(False, f"New order should have 'not started' status, got '{order_info.get('cooking_status')}'")
                                return False
                            break
            
            if found_pending:
                print_result(True, "New order appears in view orders with correct status")
            else:
                print_result(False, "New order not found in view orders")
                return False
        
        # Complete the order by finishing the item
        update_data = {
            "order_id": integration_order_id,
            "item_name": "Coffee",
            "cooking_status": "finished"
        }
        
        response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
        
        if response.status_code != 200:
            print_result(False, f"Failed to complete integration test order: {response.status_code}")
            return False
        
        result = response.json()
        if not result.get("order_auto_completed"):
            print_result(False, "Order should be auto-completed")
            return False
        
        print_result(True, "Order auto-completed successfully")
        
        # Verify it no longer appears in view orders (completed orders are filtered out)
        response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if response.status_code == 200:
            view_orders = response.json()
            
            # Should not find our completed order
            found_completed = False
            for item_group in view_orders:
                if item_group.get("item_name") == "Coffee":
                    for order_info in item_group.get("orders", []):
                        if order_info.get("orderNumber") == order_number:
                            found_completed = True
                            break
            
            if not found_completed:
                print_result(True, "Auto-completed order correctly filtered out of view orders")
            else:
                print_result(False, "Auto-completed order should not appear in view orders (pending only)")
                return False
        
        return True
        
    except Exception as e:
        print_result(False, f"Error testing view orders integration: {str(e)}")
        return False

def test_order_number_lookup_after_completion():
    """Test that customer can still lookup auto-completed orders by order number"""
    print_test_header("Order Number Lookup After Auto-Completion")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Create and auto-complete an order
        lookup_order_data = {
            "customerName": "Order Lookup Test Customer",
            "items": [{"name": "Tea", "quantity": 1}],
            "paymentMethod": "cash"
        }
        
        response = requests.post(f"{API_URL}/orders/", json=lookup_order_data, headers=headers)
        
        if response.status_code != 201:
            print_result(False, f"Failed to create lookup test order: {response.status_code}")
            return False
        
        order = response.json()
        lookup_order_id = order["id"]
        order_number = order.get("orderNumber")
        
        print_result(True, f"Lookup test order created - Number: {order_number}")
        
        # Auto-complete the order
        update_data = {
            "order_id": lookup_order_id,
            "item_name": "Tea",
            "cooking_status": "finished"
        }
        
        response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
        
        if response.status_code != 200:
            print_result(False, f"Failed to complete lookup test order: {response.status_code}")
            return False
        
        result = response.json()
        if not result.get("order_auto_completed"):
            print_result(False, "Order should be auto-completed")
            return False
        
        print_result(True, "Order auto-completed successfully")
        
        # Test customer lookup by order number (no auth required)
        response = requests.get(f"{API_URL}/orders/myorder/{order_number}")
        
        if response.status_code != 200:
            print_result(False, f"Failed to lookup completed order: {response.status_code}")
            return False
        
        looked_up_order = response.json()
        
        # Verify it's the same order and shows completed status
        if looked_up_order.get("id") != lookup_order_id:
            print_result(False, f"Looked up order ID mismatch: expected {lookup_order_id}, got {looked_up_order.get('id')}")
            return False
        
        if looked_up_order.get("status") != "completed":
            print_result(False, f"Looked up order should be 'completed', got '{looked_up_order.get('status')}'")
            return False
        
        if not looked_up_order.get("completedTime"):
            print_result(False, "Looked up order should have completedTime")
            return False
        
        print_result(True, f"Auto-completed order successfully looked up by customer")
        print_result(True, f"Order status: {looked_up_order.get('status')}")
        print_result(True, f"Completed time: {looked_up_order.get('completedTime')}")
        
        return True
        
    except Exception as e:
        print_result(False, f"Error testing order number lookup after completion: {str(e)}")
        return False

def run_edge_case_tests():
    """Run all edge case tests"""
    print(f"🚀 Starting Edge Case Tests for Enhanced Cooking Status")
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔍 Testing edge cases and integration scenarios")
    
    # Get authentication token first
    if not get_auth_token():
        print("❌ Cannot proceed without authentication")
        return False
    
    # Run all tests in priority order
    tests = [
        ("Updating Already Completed Orders", test_updating_completed_order, "MEDIUM"),
        ("Rapid Status Updates on Same Order", test_rapid_status_updates, "MEDIUM"),
        ("View Orders Integration with Auto-Completed Orders", test_view_orders_integration, "MEDIUM"),
        ("Order Number Lookup After Auto-Completion", test_order_number_lookup_after_completion, "MEDIUM")
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
    print("📊 EDGE CASE TEST SUMMARY")
    print('='*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result, priority in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} [{priority}] {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All edge case tests PASSED!")
        print("✅ Enhanced cooking status functionality handles edge cases correctly")
        return True
    else:
        print("❌ Some edge case tests FAILED - issues found")
        return False

if __name__ == "__main__":
    success = run_edge_case_tests()
    sys.exit(0 if success else 1)
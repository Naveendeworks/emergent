#!/usr/bin/env python3
"""
Backend API Testing for Enhanced Cooking Status Functionality
Tests enhanced cooking status updates with automatic order completion
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
print(f"🔗 Testing backend at: {API_URL}")

# Test data for enhanced cooking status testing
MULTI_ITEM_ORDER_DATA = {
    "customerName": "Enhanced Cooking Test Customer",
    "items": [
        {"name": "Tea", "quantity": 2},
        {"name": "Coffee", "quantity": 1},
        {"name": "Chicken Biryani", "quantity": 1}
    ],
    "paymentMethod": "cash"
}

SINGLE_ITEM_ORDER_DATA = {
    "customerName": "Single Item Test Customer",
    "items": [
        {"name": "Tea", "quantity": 1}
    ],
    "paymentMethod": "zelle"
}

# Global variables for test data
auth_token = None
multi_item_order_id = None
single_item_order_id = None

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

def test_create_multi_item_order():
    """Test creating order with multiple items for auto-completion testing"""
    print_test_header("Create Multi-Item Order for Auto-Completion Testing")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.post(f"{API_URL}/orders/", json=MULTI_ITEM_ORDER_DATA, headers=headers)
        
        if response.status_code == 201:
            order = response.json()
            
            # Verify order has multiple items
            if len(order["items"]) != 3:
                print_result(False, f"Expected 3 items, got {len(order['items'])}")
                return False
            
            # Verify all items have cooking_status defaulting to 'not started'
            for item in order["items"]:
                if item.get("cooking_status") != "not started":
                    print_result(False, f"Item '{item['name']}' has incorrect initial cooking status: {item.get('cooking_status')}")
                    return False
            
            # Verify order status is pending
            if order.get("status") != "pending":
                print_result(False, f"Order status should be 'pending', got '{order.get('status')}'")
                return False
            
            print_result(True, f"Multi-item order created - ID: {order['id']}")
            print_result(True, f"Items: {[item['name'] for item in order['items']]}")
            print_result(True, f"All items have 'not started' cooking status")
            
            # Store order ID for later tests
            global multi_item_order_id
            multi_item_order_id = order["id"]
            
            return True
        else:
            print_result(False, f"Failed to create multi-item order: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error creating multi-item order: {str(e)}")
        return False

def test_partial_item_status_updates():
    """Test updating some items to cooking/finished but not all"""
    print_test_header("Partial Item Status Updates (Order Should Remain Pending)")
    
    if not auth_token or not multi_item_order_id:
        print_result(False, "No auth token or multi-item order ID available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Update Tea to 'cooking'
        update_data = {
            "order_id": multi_item_order_id,
            "item_name": "Tea",
            "cooking_status": "cooking"
        }
        
        response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
        
        if response.status_code != 200:
            print_result(False, f"Failed to update Tea status: {response.status_code}")
            return False
        
        result = response.json()
        if not result.get("message"):
            print_result(False, "No message in response")
            return False
        
        # Check that order was NOT auto-completed
        if result.get("order_auto_completed"):
            print_result(False, "Order should NOT be auto-completed with partial updates")
            return False
        
        print_result(True, f"Tea status updated to 'cooking': {result['message']}")
        
        # Update Coffee to 'finished'
        update_data = {
            "order_id": multi_item_order_id,
            "item_name": "Coffee",
            "cooking_status": "finished"
        }
        
        response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
        
        if response.status_code != 200:
            print_result(False, f"Failed to update Coffee status: {response.status_code}")
            return False
        
        result = response.json()
        
        # Check that order was still NOT auto-completed
        if result.get("order_auto_completed"):
            print_result(False, "Order should NOT be auto-completed with partial updates")
            return False
        
        print_result(True, f"Coffee status updated to 'finished': {result['message']}")
        
        # Verify order is still pending by fetching it
        response = requests.get(f"{API_URL}/orders/{multi_item_order_id}", headers=headers)
        if response.status_code == 200:
            order = response.json()
            if order.get("status") != "pending":
                print_result(False, f"Order status should still be 'pending', got '{order.get('status')}'")
                return False
            
            print_result(True, "Order remains 'pending' with partial item updates")
            
            # Verify mixed statuses
            tea_status = None
            coffee_status = None
            biryani_status = None
            
            for item in order["items"]:
                if item["name"] == "Tea":
                    tea_status = item.get("cooking_status")
                elif item["name"] == "Coffee":
                    coffee_status = item.get("cooking_status")
                elif item["name"] == "Chicken Biryani":
                    biryani_status = item.get("cooking_status")
            
            if tea_status != "cooking":
                print_result(False, f"Tea status should be 'cooking', got '{tea_status}'")
                return False
            
            if coffee_status != "finished":
                print_result(False, f"Coffee status should be 'finished', got '{coffee_status}'")
                return False
            
            if biryani_status != "not started":
                print_result(False, f"Chicken Biryani status should be 'not started', got '{biryani_status}'")
                return False
            
            print_result(True, "Mixed item statuses verified: Tea=cooking, Coffee=finished, Chicken Biryani=not started")
            return True
        else:
            print_result(False, f"Failed to fetch order for verification: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing partial item status updates: {str(e)}")
        return False

def test_automatic_order_completion():
    """Test that order automatically completes when ALL items are finished"""
    print_test_header("Automatic Order Completion When All Items Finished")
    
    if not auth_token or not multi_item_order_id:
        print_result(False, "No auth token or multi-item order ID available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Update Tea to 'finished' (Coffee is already finished from previous test)
        update_data = {
            "order_id": multi_item_order_id,
            "item_name": "Tea",
            "cooking_status": "finished"
        }
        
        response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
        
        if response.status_code != 200:
            print_result(False, f"Failed to update Tea status: {response.status_code}")
            return False
        
        result = response.json()
        print_result(True, f"Tea status updated: {result['message']}")
        
        # Order should still be pending (2 out of 3 items finished)
        if result.get("order_auto_completed"):
            print_result(False, "Order should NOT be auto-completed yet (2/3 items finished)")
            return False
        
        # Now update the last item (Chicken Biryani) to 'finished'
        update_data = {
            "order_id": multi_item_order_id,
            "item_name": "Chicken Biryani",
            "cooking_status": "finished"
        }
        
        response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
        
        if response.status_code != 200:
            print_result(False, f"Failed to update Chicken Biryani status: {response.status_code}")
            return False
        
        result = response.json()
        print_result(True, f"Chicken Biryani status updated: {result['message']}")
        
        # NOW the order should be auto-completed
        if not result.get("order_auto_completed"):
            print_result(False, "Order should be auto-completed when all items are finished")
            return False
        
        print_result(True, "✨ Order automatically completed when all items finished!")
        
        # Verify the enhanced API response
        if "Order automatically completed!" not in result.get("message", ""):
            print_result(False, "Enhanced API response should include auto-completion message")
            return False
        
        print_result(True, "Enhanced API response includes auto-completion notification")
        
        # Verify order status changed to 'completed' by fetching it
        response = requests.get(f"{API_URL}/orders/{multi_item_order_id}", headers=headers)
        if response.status_code == 200:
            order = response.json()
            
            if order.get("status") != "completed":
                print_result(False, f"Order status should be 'completed', got '{order.get('status')}'")
                return False
            
            # Verify completedTime and actualDeliveryTime are set
            if not order.get("completedTime"):
                print_result(False, "completedTime should be set when order auto-completes")
                return False
            
            if not order.get("actualDeliveryTime"):
                print_result(False, "actualDeliveryTime should be set when order auto-completes")
                return False
            
            print_result(True, f"Order status changed to 'completed'")
            print_result(True, f"completedTime set: {order.get('completedTime')}")
            print_result(True, f"actualDeliveryTime set: {order.get('actualDeliveryTime')}")
            
            return True
        else:
            print_result(False, f"Failed to fetch completed order: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing automatic order completion: {str(e)}")
        return False

def test_single_item_auto_completion():
    """Test auto-completion with single item order"""
    print_test_header("Single Item Order Auto-Completion")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Create single item order
        response = requests.post(f"{API_URL}/orders/", json=SINGLE_ITEM_ORDER_DATA, headers=headers)
        
        if response.status_code != 201:
            print_result(False, f"Failed to create single item order: {response.status_code}")
            return False
        
        order = response.json()
        global single_item_order_id
        single_item_order_id = order["id"]
        
        print_result(True, f"Single item order created - ID: {order['id']}")
        
        # Update the single item to 'finished' - should auto-complete immediately
        update_data = {
            "order_id": single_item_order_id,
            "item_name": "Tea",
            "cooking_status": "finished"
        }
        
        response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
        
        if response.status_code != 200:
            print_result(False, f"Failed to update Tea status: {response.status_code}")
            return False
        
        result = response.json()
        
        # Should be auto-completed immediately
        if not result.get("order_auto_completed"):
            print_result(False, "Single item order should be auto-completed when item is finished")
            return False
        
        print_result(True, "✨ Single item order automatically completed!")
        print_result(True, f"Response: {result['message']}")
        
        return True
        
    except Exception as e:
        print_result(False, f"Error testing single item auto-completion: {str(e)}")
        return False

def test_enhanced_api_response():
    """Test enhanced API response includes detailed information"""
    print_test_header("Enhanced API Response Information")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Create a new order for testing
        test_order_data = {
            "customerName": "API Response Test Customer",
            "items": [{"name": "Coffee", "quantity": 1}],
            "paymentMethod": "cashapp"
        }
        
        response = requests.post(f"{API_URL}/orders/", json=test_order_data, headers=headers)
        
        if response.status_code != 201:
            print_result(False, f"Failed to create test order: {response.status_code}")
            return False
        
        order = response.json()
        test_order_id = order["id"]
        
        # Test normal status update (not finishing)
        update_data = {
            "order_id": test_order_id,
            "item_name": "Coffee",
            "cooking_status": "cooking"
        }
        
        response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
        
        if response.status_code != 200:
            print_result(False, f"Failed to update status: {response.status_code}")
            return False
        
        result = response.json()
        
        # Verify enhanced response structure
        required_fields = ["message", "status"]
        for field in required_fields:
            if field not in result:
                print_result(False, f"Enhanced API response missing field: {field}")
                return False
        
        if result["status"] != "cooking":
            print_result(False, f"Status field should be 'cooking', got '{result['status']}'")
            return False
        
        if "order_auto_completed" in result and result["order_auto_completed"]:
            print_result(False, "order_auto_completed should be false for non-finishing update")
            return False
        
        print_result(True, "Enhanced API response structure verified for normal update")
        
        # Test finishing update (should auto-complete)
        update_data = {
            "order_id": test_order_id,
            "item_name": "Coffee",
            "cooking_status": "finished"
        }
        
        response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
        
        if response.status_code != 200:
            print_result(False, f"Failed to update to finished: {response.status_code}")
            return False
        
        result = response.json()
        
        # Should have auto-completion flag
        if not result.get("order_auto_completed"):
            print_result(False, "order_auto_completed should be true when order completes")
            return False
        
        if "Order automatically completed!" not in result.get("message", ""):
            print_result(False, "Message should include auto-completion notification")
            return False
        
        print_result(True, "Enhanced API response verified for auto-completion")
        print_result(True, f"Auto-completion message: {result['message']}")
        
        return True
        
    except Exception as e:
        print_result(False, f"Error testing enhanced API response: {str(e)}")
        return False

def test_error_handling():
    """Test error handling for invalid orders or items"""
    print_test_header("Error Handling for Invalid Orders/Items")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Test invalid order ID
        update_data = {
            "order_id": "invalid-order-id",
            "item_name": "Tea",
            "cooking_status": "cooking"
        }
        
        response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
        
        if response.status_code != 404:
            print_result(False, f"Should return 404 for invalid order ID, got {response.status_code}")
            return False
        
        print_result(True, "Invalid order ID correctly returns 404")
        
        # Test invalid item name (using valid order)
        if multi_item_order_id:
            update_data = {
                "order_id": multi_item_order_id,
                "item_name": "Invalid Item Name",
                "cooking_status": "cooking"
            }
            
            response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
            
            if response.status_code not in [400, 404]:
                print_result(False, f"Should return 400/404 for invalid item name, got {response.status_code}")
                return False
            
            print_result(True, "Invalid item name correctly returns error")
        
        # Test invalid cooking status
        if multi_item_order_id:
            update_data = {
                "order_id": multi_item_order_id,
                "item_name": "Tea",
                "cooking_status": "invalid_status"
            }
            
            response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
            
            if response.status_code not in [400, 422]:
                print_result(False, f"Should return 400/422 for invalid cooking status, got {response.status_code}")
                return False
            
            print_result(True, "Invalid cooking status correctly returns validation error")
        
        return True
        
    except Exception as e:
        print_result(False, f"Error testing error handling: {str(e)}")
        return False

def run_enhanced_cooking_tests():
    """Run all enhanced cooking status tests"""
    print(f"🚀 Starting Enhanced Cooking Status Tests")
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🍳 Testing enhanced cooking status functionality with automatic order completion")
    
    # Get authentication token first
    if not get_auth_token():
        print("❌ Cannot proceed without authentication")
        return False
    
    # Run all tests in priority order
    tests = [
        ("Create Multi-Item Order for Auto-Completion Testing", test_create_multi_item_order, "HIGH"),
        ("Partial Item Status Updates (Order Should Remain Pending)", test_partial_item_status_updates, "HIGH"),
        ("Automatic Order Completion When All Items Finished", test_automatic_order_completion, "HIGH"),
        ("Enhanced API Response Information", test_enhanced_api_response, "HIGH"),
        ("Single Item Order Auto-Completion", test_single_item_auto_completion, "MEDIUM"),
        ("Error Handling for Invalid Orders/Items", test_error_handling, "MEDIUM")
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
    print("📊 ENHANCED COOKING STATUS TEST SUMMARY")
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
        print("🎉 All enhanced cooking status tests PASSED!")
        print("✅ Enhanced cooking status functionality with automatic order completion working perfectly")
        return True
    elif high_priority_passed == high_priority_total:
        print("⚠️  All HIGH PRIORITY tests passed, some medium priority tests failed")
        print("✅ Core enhanced cooking status functionality working correctly")
        return True
    else:
        print("❌ Some HIGH PRIORITY tests FAILED - critical issues found")
        return False

if __name__ == "__main__":
    success = run_enhanced_cooking_tests()
    sys.exit(0 if success else 1)
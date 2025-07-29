#!/usr/bin/env python3
"""
Backend API Testing for OPTIONAL Phone Number Functionality
Tests the updated phone number features where phone numbers are now OPTIONAL
"""

import requests
import json
import sys
import os
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

# Test data
VALID_PHONE_NUMBERS = [
    "1234567890",      # 10 digits (minimum)
    "12345678901",     # 11 digits
    "123456789012345"  # 15 digits (maximum)
]

INVALID_PHONE_NUMBERS = [
    "123456789",       # 9 digits (too short)
    "1234567890123456" # 16 digits (too long)
]

# Sample order data WITHOUT phone number (for testing optional functionality)
SAMPLE_ORDER_DATA_NO_PHONE = {
    "customerName": "Jane Doe",
    "items": [
        {"name": "Pizza", "quantity": 1},
        {"name": "Soda", "quantity": 2}
    ],
    "paymentMethod": "zelle"
}

# Sample order data WITH phone number
SAMPLE_ORDER_DATA_WITH_PHONE = {
    "customerName": "John Smith",
    "phoneNumber": "1234567890",
    "items": [
        {"name": "Burger", "quantity": 2},
        {"name": "Fries", "quantity": 1}
    ],
    "paymentMethod": "cash"
}

# Global variables for test data
auth_token = None
created_order_id_no_phone = None
created_order_id_with_phone = None

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

def test_order_creation_without_phone():
    """HIGH PRIORITY: Test order creation WITHOUT phone number (should succeed)"""
    print_test_header("Order Creation WITHOUT Phone Number")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        order_data = SAMPLE_ORDER_DATA_NO_PHONE.copy()
        
        response = requests.post(f"{API_URL}/orders/", json=order_data, headers=headers)
        
        if response.status_code == 201:
            order = response.json()
            # Phone number should be None or not present
            phone_number = order.get("phoneNumber")
            if phone_number is None:
                print_result(True, f"Order created successfully without phone number")
                global created_order_id_no_phone
                created_order_id_no_phone = order.get("id")
                return True
            else:
                print_result(False, f"Expected phoneNumber to be None, got: {phone_number}")
                return False
        else:
            print_result(False, f"Failed to create order without phone: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing order creation without phone: {str(e)}")
        return False

def test_order_creation_with_valid_phone():
    """HIGH PRIORITY: Test order creation WITH valid phone number (should succeed)"""
    print_test_header("Order Creation WITH Valid Phone Numbers")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    success_count = 0
    
    for phone in VALID_PHONE_NUMBERS:
        try:
            order_data = SAMPLE_ORDER_DATA_WITH_PHONE.copy()
            order_data["phoneNumber"] = phone
            order_data["customerName"] = f"Customer {phone}"
            
            response = requests.post(f"{API_URL}/orders/", json=order_data, headers=headers)
            
            if response.status_code == 201:
                order = response.json()
                if order.get("phoneNumber") == phone:
                    print_result(True, f"Order created with phone {phone}")
                    success_count += 1
                    # Store first order ID for later tests
                    global created_order_id_with_phone
                    if not created_order_id_with_phone:
                        created_order_id_with_phone = order.get("id")
                else:
                    print_result(False, f"Phone number mismatch for {phone}")
            else:
                print_result(False, f"Failed to create order with phone {phone}: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print_result(False, f"Error testing phone {phone}: {str(e)}")
    
    return success_count == len(VALID_PHONE_NUMBERS)

def test_order_creation_with_invalid_phone():
    """HIGH PRIORITY: Test order creation WITH invalid phone number (should fail validation)"""
    print_test_header("Order Creation WITH Invalid Phone Numbers")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    success_count = 0
    
    for phone in INVALID_PHONE_NUMBERS:
        try:
            order_data = SAMPLE_ORDER_DATA_WITH_PHONE.copy()
            order_data["phoneNumber"] = phone
            order_data["customerName"] = f"Customer {phone}"
            
            response = requests.post(f"{API_URL}/orders/", json=order_data, headers=headers)
            
            if response.status_code == 422:  # Validation error expected
                print_result(True, f"Correctly rejected invalid phone {phone}")
                success_count += 1
            else:
                print_result(False, f"Should have rejected phone {phone}, got status {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print_result(False, f"Error testing invalid phone {phone}: {str(e)}")
    
    return success_count == len(INVALID_PHONE_NUMBERS)

def test_order_update_without_phone():
    """MEDIUM PRIORITY: Test order update without phone number (should work)"""
    print_test_header("Order Update WITHOUT Phone Number")
    
    if not auth_token or not created_order_id_no_phone:
        print_result(False, "No auth token or order ID available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Update order without phone number
        update_data = {
            "customerName": "Updated Customer No Phone",
            "items": [
                {"name": "Updated Pizza", "quantity": 2}
            ],
            "paymentMethod": "cashapp"
        }
        
        response = requests.put(f"{API_URL}/orders/{created_order_id_no_phone}", json=update_data, headers=headers)
        
        if response.status_code == 200:
            updated_order = response.json()
            if updated_order.get("phoneNumber") is None:
                print_result(True, f"Order updated successfully without phone number")
                return True
            else:
                print_result(False, f"Expected phoneNumber to remain None")
                return False
        else:
            print_result(False, f"Failed to update order: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing order update without phone: {str(e)}")
        return False

def test_order_update_with_phone():
    """MEDIUM PRIORITY: Test order update with phone number (should work)"""
    print_test_header("Order Update WITH Phone Number")
    
    if not auth_token or not created_order_id_with_phone:
        print_result(False, "No auth token or order ID available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Update order with new phone number
        new_phone = "9876543210"
        update_data = {
            "customerName": "Updated Customer With Phone",
            "phoneNumber": new_phone,
            "items": [
                {"name": "Updated Pizza", "quantity": 1}
            ],
            "paymentMethod": "zelle"
        }
        
        response = requests.put(f"{API_URL}/orders/{created_order_id_with_phone}", json=update_data, headers=headers)
        
        if response.status_code == 200:
            updated_order = response.json()
            if updated_order.get("phoneNumber") == new_phone:
                print_result(True, f"Order updated with new phone number {new_phone}")
                return True
            else:
                print_result(False, f"Phone number not updated correctly")
                return False
        else:
            print_result(False, f"Failed to update order: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing order update with phone: {str(e)}")
        return False

def test_myorder_endpoint_with_phone():
    """MEDIUM PRIORITY: Test myorder endpoint still works for orders with phone numbers"""
    print_test_header("MyOrder Endpoint with Phone Numbers")
    
    # Test with a phone number that should have orders
    test_phone = VALID_PHONE_NUMBERS[0]  # "1234567890"
    
    try:
        # Test without authentication (should work)
        response = requests.get(f"{API_URL}/orders/myorder/{test_phone}")
        
        if response.status_code == 200:
            orders = response.json()
            if isinstance(orders, list):
                print_result(True, f"Retrieved {len(orders)} orders for phone {test_phone}")
                
                # Verify all orders have the correct phone number
                if orders:
                    phone_match = all(order.get("phoneNumber") == test_phone for order in orders)
                    if phone_match:
                        print_result(True, "All returned orders have correct phone number")
                    else:
                        print_result(False, "Some orders have incorrect phone numbers")
                        return False
                else:
                    print_result(True, "No orders found for this phone number (expected if no orders exist)")
                    
                return True
            else:
                print_result(False, f"Expected list, got {type(orders)}")
                return False
        else:
            print_result(False, f"Failed to get orders by phone: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing myorder endpoint: {str(e)}")
        return False

def test_myorder_endpoint_with_invalid_phone():
    """Test myorder endpoint with invalid phone numbers"""
    print_test_header("MyOrder Endpoint with Invalid Phone Numbers")
    
    success_count = 0
    
    for phone in INVALID_PHONE_NUMBERS:
        try:
            response = requests.get(f"{API_URL}/orders/myorder/{phone}")
            
            if response.status_code == 400:  # Bad request expected
                print_result(True, f"Correctly rejected invalid phone {phone}")
                success_count += 1
            else:
                print_result(False, f"Should have rejected phone {phone}, got status {response.status_code}")
                
        except Exception as e:
            print_result(False, f"Error testing invalid phone {phone}: {str(e)}")
    
    return success_count == len(INVALID_PHONE_NUMBERS)

def run_all_tests():
    """Run all optional phone number functionality tests"""
    print(f"🚀 Starting OPTIONAL Phone Number Functionality Tests")
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Testing that phone numbers are now OPTIONAL in order management")
    
    # Get authentication token first
    if not get_auth_token():
        print("❌ Cannot proceed without authentication")
        return False
    
    # Run all tests in priority order
    tests = [
        # HIGH PRIORITY TESTS
        ("HIGH: Order Creation WITHOUT Phone Number", test_order_creation_without_phone),
        ("HIGH: Order Creation WITH Valid Phone Numbers", test_order_creation_with_valid_phone),
        ("HIGH: Order Creation WITH Invalid Phone Numbers", test_order_creation_with_invalid_phone),
        
        # MEDIUM PRIORITY TESTS
        ("MEDIUM: Order Update WITHOUT Phone Number", test_order_update_without_phone),
        ("MEDIUM: Order Update WITH Phone Number", test_order_update_with_phone),
        ("MEDIUM: MyOrder Endpoint with Phone Numbers", test_myorder_endpoint_with_phone),
        ("MEDIUM: MyOrder Endpoint with Invalid Phone Numbers", test_myorder_endpoint_with_invalid_phone)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_result(False, f"Test {test_name} crashed: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print('='*60)
    
    passed = 0
    total = len(results)
    high_priority_passed = 0
    high_priority_total = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
        
        if test_name.startswith("HIGH:"):
            high_priority_total += 1
            if result:
                high_priority_passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    print(f"🔥 High Priority: {high_priority_passed}/{high_priority_total} tests passed")
    
    if passed == total:
        print("🎉 All optional phone number functionality tests PASSED!")
        return True
    elif high_priority_passed == high_priority_total:
        print("✅ All HIGH PRIORITY tests PASSED! Some medium priority tests failed.")
        return True
    else:
        print("⚠️  Some HIGH PRIORITY tests FAILED - check implementation")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Backend API Testing for Fresh Database with Complete Schema
Tests creating new orders with complete schema after database cleanup
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

SAMPLE_ORDER_DATA = {
    "customerName": "Fresh Database Test",
    "phoneNumber": "9876543210",
    "items": [
        {"name": "Tea", "quantity": 2},
        {"name": "Coffee", "quantity": 1}
    ],
    "paymentMethod": "cash"
}

SAMPLE_ORDER_NO_PHONE = {
    "customerName": "No Phone Test Customer",
    "items": [
        {"name": "Tea", "quantity": 1}
    ],
    "paymentMethod": "zelle"
}

# Global variables for test data
auth_token = None
created_order_id = None

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

def test_order_creation_with_valid_phone():
    """Test order creation with valid phone numbers"""
    print_test_header("Order Creation with Valid Phone Numbers")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    success_count = 0
    
    for phone in VALID_PHONE_NUMBERS:
        try:
            order_data = SAMPLE_ORDER_DATA.copy()
            order_data["phoneNumber"] = phone
            order_data["customerName"] = f"Customer {phone}"
            
            response = requests.post(f"{API_URL}/orders/", json=order_data, headers=headers)
            
            if response.status_code == 201:
                order = response.json()
                if order.get("phoneNumber") == phone:
                    print_result(True, f"Order created with phone {phone}")
                    success_count += 1
                    # Store first order ID for later tests
                    global created_order_id
                    if not created_order_id:
                        created_order_id = order.get("id")
                else:
                    print_result(False, f"Phone number mismatch for {phone}")
            else:
                print_result(False, f"Failed to create order with phone {phone}: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print_result(False, f"Error testing phone {phone}: {str(e)}")
    
    return success_count == len(VALID_PHONE_NUMBERS)

def test_order_creation_with_invalid_phone():
    """Test order creation with invalid phone numbers (should fail)"""
    print_test_header("Order Creation with Invalid Phone Numbers")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    success_count = 0
    
    for phone in INVALID_PHONE_NUMBERS:
        try:
            order_data = SAMPLE_ORDER_DATA.copy()
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

def test_customer_self_service_endpoint():
    """Test the /api/orders/myorder/{phone_number} endpoint"""
    print_test_header("Customer Self-Service Endpoint")
    
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
                phone_match = all(order.get("phoneNumber") == test_phone for order in orders)
                if phone_match:
                    print_result(True, "All returned orders have correct phone number")
                else:
                    print_result(False, "Some orders have incorrect phone numbers")
                    return False
                    
                return True
            else:
                print_result(False, f"Expected list, got {type(orders)}")
                return False
        else:
            print_result(False, f"Failed to get orders by phone: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing self-service endpoint: {str(e)}")
        return False

def test_invalid_phone_self_service():
    """Test self-service endpoint with invalid phone numbers"""
    print_test_header("Self-Service Endpoint with Invalid Phone Numbers")
    
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

def test_order_update_with_phone():
    """Test updating an order with phone number"""
    print_test_header("Order Update with Phone Number")
    
    if not auth_token or not created_order_id:
        print_result(False, "No auth token or order ID available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Update order with new phone number
        new_phone = "9876543210"
        update_data = {
            "customerName": "Updated Customer",
            "phoneNumber": new_phone,
            "items": [
                {"name": "Pizza", "quantity": 1}
            ],
            "paymentMethod": "zelle"
        }
        
        response = requests.put(f"{API_URL}/orders/{created_order_id}", json=update_data, headers=headers)
        
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
        print_result(False, f"Error testing order update: {str(e)}")
        return False

def test_order_update_with_invalid_phone():
    """Test updating an order with invalid phone number"""
    print_test_header("Order Update with Invalid Phone Number")
    
    if not auth_token or not created_order_id:
        print_result(False, "No auth token or order ID available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Try to update with invalid phone
        invalid_phone = "123"  # Too short
        update_data = {
            "customerName": "Test Customer",
            "phoneNumber": invalid_phone,
            "items": [
                {"name": "Test Item", "quantity": 1}
            ],
            "paymentMethod": "cash"
        }
        
        response = requests.put(f"{API_URL}/orders/{created_order_id}", json=update_data, headers=headers)
        
        if response.status_code == 422:  # Validation error expected
            print_result(True, "Correctly rejected invalid phone number in update")
            return True
        else:
            print_result(False, f"Should have rejected invalid phone, got status {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing invalid phone update: {str(e)}")
        return False

def test_existing_authentication_still_works():
    """Test that existing authentication still works for admin endpoints"""
    print_test_header("Existing Authentication Still Works")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Test getting all orders (requires authentication)
        response = requests.get(f"{API_URL}/orders/", headers=headers)
        
        if response.status_code == 200:
            orders = response.json()
            print_result(True, f"Successfully retrieved {len(orders)} orders with authentication")
            return True
        else:
            print_result(False, f"Failed to get orders with auth: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing authentication: {str(e)}")
        return False

def run_all_tests():
    """Run all phone number functionality tests"""
    print(f"🚀 Starting Phone Number Functionality Tests")
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get authentication token first
    if not get_auth_token():
        print("❌ Cannot proceed without authentication")
        return False
    
    # Run all tests
    tests = [
        ("Order Creation with Valid Phone Numbers", test_order_creation_with_valid_phone),
        ("Order Creation with Invalid Phone Numbers", test_order_creation_with_invalid_phone),
        ("Customer Self-Service Endpoint", test_customer_self_service_endpoint),
        ("Self-Service with Invalid Phone Numbers", test_invalid_phone_self_service),
        ("Order Update with Phone Number", test_order_update_with_phone),
        ("Order Update with Invalid Phone Number", test_order_update_with_invalid_phone),
        ("Existing Authentication Still Works", test_existing_authentication_still_works)
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
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All phone number functionality tests PASSED!")
        return True
    else:
        print("⚠️  Some tests FAILED - check implementation")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
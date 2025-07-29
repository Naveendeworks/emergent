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

# Test data for fresh database testing
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

def test_menu_items_return_prices():
    """Test that menu items still return prices correctly after database cleanup"""
    print_test_header("Menu Items Return Prices Correctly")
    
    try:
        response = requests.get(f"{API_URL}/menu/")
        
        if response.status_code == 200:
            menu_data = response.json()
            # Menu endpoint returns an object with "items" array
            menu_items = menu_data.get("items", [])
            if not menu_items:
                print_result(False, "No menu items returned")
                return False
            
            # Check that all items have price field
            items_with_prices = 0
            expected_prices = {
                "Tea": 2.00,
                "Coffee": 3.00
            }
            
            for item in menu_items:
                if "price" in item:
                    items_with_prices += 1
                    # Check specific expected prices
                    if item["name"] in expected_prices:
                        expected_price = expected_prices[item["name"]]
                        if item["price"] == expected_price:
                            print_result(True, f"{item['name']} has correct price: ${item['price']:.2f}")
                        else:
                            print_result(False, f"{item['name']} price mismatch: expected ${expected_price:.2f}, got ${item['price']:.2f}")
                            return False
            
            print_result(True, f"All {items_with_prices} menu items include price field")
            return items_with_prices > 0
        else:
            print_result(False, f"Failed to get menu items: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing menu items: {str(e)}")
        return False

def test_create_order_complete_schema():
    """Test creating new order with complete schema (customerName, phoneNumber, items with prices, totalAmount)"""
    print_test_header("Create Order with Complete Schema")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.post(f"{API_URL}/orders/", json=SAMPLE_ORDER_DATA, headers=headers)
        
        if response.status_code == 201:
            order = response.json()
            
            # Verify complete schema
            required_fields = ["id", "customerName", "phoneNumber", "items", "totalAmount", "status", "createdAt"]
            missing_fields = []
            
            for field in required_fields:
                if field not in order:
                    missing_fields.append(field)
            
            if missing_fields:
                print_result(False, f"Missing fields in order: {missing_fields}")
                return False
            
            # Verify customer name
            if order["customerName"] != SAMPLE_ORDER_DATA["customerName"]:
                print_result(False, f"Customer name mismatch: expected {SAMPLE_ORDER_DATA['customerName']}, got {order['customerName']}")
                return False
            
            # Verify phone number
            if order["phoneNumber"] != SAMPLE_ORDER_DATA["phoneNumber"]:
                print_result(False, f"Phone number mismatch: expected {SAMPLE_ORDER_DATA['phoneNumber']}, got {order['phoneNumber']}")
                return False
            
            # Verify items have pricing fields
            for item in order["items"]:
                required_item_fields = ["name", "quantity", "price", "subtotal"]
                for field in required_item_fields:
                    if field not in item:
                        print_result(False, f"Missing field '{field}' in order item")
                        return False
            
            # Verify totalAmount exists and is calculated
            if "totalAmount" not in order or order["totalAmount"] <= 0:
                print_result(False, "totalAmount missing or invalid")
                return False
            
            # Calculate expected total (Tea: $2.00 x 2 = $4.00, Coffee: $3.00 x 1 = $3.00, Total: $7.00)
            expected_total = 7.00
            if abs(order["totalAmount"] - expected_total) > 0.01:
                print_result(False, f"Total amount incorrect: expected ${expected_total:.2f}, got ${order['totalAmount']:.2f}")
                return False
            
            print_result(True, f"Order created with complete schema - ID: {order['id']}, Total: ${order['totalAmount']:.2f}")
            
            # Store order ID for later tests
            global created_order_id
            created_order_id = order["id"]
            
            return True
        else:
            print_result(False, f"Failed to create order: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error creating order: {str(e)}")
        return False

def test_order_pricing_fields():
    """Test that order has all pricing fields (price, subtotal, totalAmount)"""
    print_test_header("Verify Order Has All Pricing Fields")
    
    if not auth_token or not created_order_id:
        print_result(False, "No auth token or order ID available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{API_URL}/orders/{created_order_id}", headers=headers)
        
        if response.status_code == 200:
            order = response.json()
            
            # Check totalAmount
            if "totalAmount" not in order:
                print_result(False, "Order missing totalAmount field")
                return False
            
            print_result(True, f"Order has totalAmount: ${order['totalAmount']:.2f}")
            
            # Check each item has price and subtotal
            for i, item in enumerate(order["items"]):
                if "price" not in item:
                    print_result(False, f"Item {i+1} missing price field")
                    return False
                if "subtotal" not in item:
                    print_result(False, f"Item {i+1} missing subtotal field")
                    return False
                
                # Verify subtotal calculation
                expected_subtotal = item["price"] * item["quantity"]
                if abs(item["subtotal"] - expected_subtotal) > 0.01:
                    print_result(False, f"Item {i+1} subtotal incorrect: expected ${expected_subtotal:.2f}, got ${item['subtotal']:.2f}")
                    return False
                
                print_result(True, f"Item '{item['name']}': ${item['price']:.2f} x {item['quantity']} = ${item['subtotal']:.2f}")
            
            return True
        else:
            print_result(False, f"Failed to get order: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error verifying pricing fields: {str(e)}")
        return False

def test_myorder_endpoint_with_new_order():
    """Test myorder endpoint works with new order"""
    print_test_header("MyOrder Endpoint Works with New Order")
    
    if not created_order_id:
        print_result(False, "No order ID available")
        return False
    
    # Use the phone number from the created order
    test_phone = SAMPLE_ORDER_DATA["phoneNumber"]
    
    try:
        response = requests.get(f"{API_URL}/orders/myorder/{test_phone}")
        
        if response.status_code == 200:
            orders = response.json()
            
            if not isinstance(orders, list):
                print_result(False, f"Expected list, got {type(orders)}")
                return False
            
            if len(orders) == 0:
                print_result(False, "No orders found for phone number")
                return False
            
            # Find our created order
            found_order = None
            for order in orders:
                if order.get("id") == created_order_id:
                    found_order = order
                    break
            
            if not found_order:
                print_result(False, f"Created order {created_order_id} not found in myorder results")
                return False
            
            # Verify the order has complete pricing information
            if "totalAmount" not in found_order:
                print_result(False, "Order in myorder response missing totalAmount")
                return False
            
            for item in found_order["items"]:
                if "price" not in item or "subtotal" not in item:
                    print_result(False, "Order items in myorder response missing pricing fields")
                    return False
            
            print_result(True, f"MyOrder endpoint returned {len(orders)} orders with complete pricing info")
            print_result(True, f"Found created order with total: ${found_order['totalAmount']:.2f}")
            
            return True
        else:
            print_result(False, f"MyOrder endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing myorder endpoint: {str(e)}")
        return False

def test_create_order_without_phone():
    """Test creating order without phone number (optional field)"""
    print_test_header("Create Order Without Phone Number")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.post(f"{API_URL}/orders/", json=SAMPLE_ORDER_NO_PHONE, headers=headers)
        
        if response.status_code == 201:
            order = response.json()
            
            # Verify phoneNumber is None or not present
            if "phoneNumber" in order and order["phoneNumber"] is not None:
                print_result(False, f"Expected phoneNumber to be None, got {order['phoneNumber']}")
                return False
            
            # Verify other fields are still present and correct
            if order["customerName"] != SAMPLE_ORDER_NO_PHONE["customerName"]:
                print_result(False, "Customer name incorrect")
                return False
            
            # Verify pricing still works
            if "totalAmount" not in order or order["totalAmount"] <= 0:
                print_result(False, "totalAmount missing or invalid")
                return False
            
            # Expected total for Tea: $2.00 x 1 = $2.00
            expected_total = 2.00
            if abs(order["totalAmount"] - expected_total) > 0.01:
                print_result(False, f"Total amount incorrect: expected ${expected_total:.2f}, got ${order['totalAmount']:.2f}")
                return False
            
            print_result(True, f"Order created without phone number - ID: {order['id']}, Total: ${order['totalAmount']:.2f}")
            return True
        else:
            print_result(False, f"Failed to create order without phone: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error creating order without phone: {str(e)}")
        return False

def run_fresh_database_tests():
    """Run all fresh database tests with complete schema"""
    print(f"🚀 Starting Fresh Database Tests with Complete Schema")
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🗄️ Testing system after database cleanup with fresh data")
    
    # Get authentication token first
    if not get_auth_token():
        print("❌ Cannot proceed without authentication")
        return False
    
    # Run all tests in priority order
    tests = [
        ("Menu Items Return Prices Correctly", test_menu_items_return_prices, "MEDIUM"),
        ("Create Order with Complete Schema", test_create_order_complete_schema, "HIGH"),
        ("Verify Order Has All Pricing Fields", test_order_pricing_fields, "HIGH"),
        ("MyOrder Endpoint Works with New Order", test_myorder_endpoint_with_new_order, "HIGH"),
        ("Create Order Without Phone Number", test_create_order_without_phone, "MEDIUM")
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
    print("📊 FRESH DATABASE TEST SUMMARY")
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
        print("🎉 All fresh database tests PASSED!")
        print("✅ System works correctly with clean database and complete schema")
        return True
    elif high_priority_passed == high_priority_total:
        print("⚠️  All HIGH PRIORITY tests passed, some medium priority tests failed")
        print("✅ Core functionality works with fresh database")
        return True
    else:
        print("❌ Some HIGH PRIORITY tests FAILED - critical issues found")
        return False

if __name__ == "__main__":
    success = run_fresh_database_tests()
    sys.exit(0 if success else 1)
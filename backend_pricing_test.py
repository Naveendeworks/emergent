#!/usr/bin/env python3
"""
Backend API Testing for Pricing Functionality
Tests the new pricing features in the order management system
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

# Expected pricing list to verify
EXPECTED_PRICES = {
    "Tea": 2.00,
    "Coffee": 3.00,
    "Chicken Biryani": 12.99,
    "Goat Biryani": 12.99,
    "Dosa": 10.99,
    "Idly": 9.99,
    "Chicken 65": 9.99,
    "Fish Pulusu": 12.99,
    "Goat Curry": 14.99,
    "Keema": 15.99,
    "Paya Soup": 8.99,
    "Nellore Kaaram": 10.99,
    "Aloo Masala": 6.99,
    "Chaat Items": 5.99,
    "Bajji": 6.99,
    "Punugulu": 5.99,
    "Fruits Cutting": 5.99
}

SAMPLE_ORDER_DATA_WITH_PRICING = {
    "customerName": "John Smith",
    "phoneNumber": "1234567890",
    "items": [
        {"name": "Tea", "quantity": 2},  # $2.00 * 2 = $4.00
        {"name": "Coffee", "quantity": 1}  # $3.00 * 1 = $3.00
        # Total expected: $7.00
    ],
    "paymentMethod": "cash"
}

INVALID_MENU_ORDER = {
    "customerName": "Test Customer",
    "phoneNumber": "1234567890",
    "items": [
        {"name": "Invalid Item", "quantity": 1}
    ],
    "paymentMethod": "cash"
}

BIRYANI_ORDER = {
    "customerName": "Biryani Lover",
    "phoneNumber": "5555555555",
    "items": [
        {"name": "Chicken Biryani", "quantity": 2},  # $12.99 * 2 = $25.98
        {"name": "Goat Biryani", "quantity": 1}     # $12.99 * 1 = $12.99
        # Total expected: $38.97
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

def test_menu_items_include_prices():
    """HIGH PRIORITY: Test menu items now include prices"""
    print_test_header("Menu Items Include Prices")
    
    try:
        response = requests.get(f"{API_URL}/menu/")
        
        if response.status_code == 200:
            menu_data = response.json()
            items = menu_data.get("items", [])
            
            if not items:
                print_result(False, "No menu items found")
                return False
            
            print_result(True, f"Retrieved {len(items)} menu items")
            
            # Check if all items have price field
            items_with_prices = 0
            price_matches = 0
            
            for item in items:
                if "price" in item:
                    items_with_prices += 1
                    item_name = item.get("name")
                    item_price = item.get("price")
                    
                    # Check if price matches expected pricing
                    if item_name in EXPECTED_PRICES:
                        expected_price = EXPECTED_PRICES[item_name]
                        if abs(item_price - expected_price) < 0.01:  # Allow for floating point precision
                            price_matches += 1
                            print_result(True, f"{item_name}: ${item_price:.2f} ✓")
                        else:
                            print_result(False, f"{item_name}: Expected ${expected_price:.2f}, got ${item_price:.2f}")
                    else:
                        print_result(True, f"{item_name}: ${item_price:.2f} (not in expected list)")
                else:
                    print_result(False, f"Item {item.get('name', 'Unknown')} missing price field")
            
            if items_with_prices == len(items):
                print_result(True, f"All {len(items)} menu items have price field")
                if price_matches > 0:
                    print_result(True, f"{price_matches} items have correct expected prices")
                return True
            else:
                print_result(False, f"Only {items_with_prices}/{len(items)} items have price field")
                return False
                
        else:
            print_result(False, f"Failed to get menu: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing menu prices: {str(e)}")
        return False

def test_order_creation_calculates_prices():
    """HIGH PRIORITY: Test order creation automatically calculates prices and totals"""
    print_test_header("Order Creation Calculates Prices and Totals")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.post(f"{API_URL}/orders/", json=SAMPLE_ORDER_DATA_WITH_PRICING, headers=headers)
        
        if response.status_code == 201:
            order = response.json()
            global created_order_id
            created_order_id = order.get("id")
            
            # Check if order has totalAmount field
            if "totalAmount" not in order:
                print_result(False, "Order missing totalAmount field")
                return False
            
            total_amount = order.get("totalAmount")
            expected_total = 7.00  # Tea: $2.00 * 2 + Coffee: $3.00 * 1
            
            if abs(total_amount - expected_total) < 0.01:
                print_result(True, f"Total amount calculated correctly: ${total_amount:.2f}")
            else:
                print_result(False, f"Total amount incorrect: Expected ${expected_total:.2f}, got ${total_amount:.2f}")
                return False
            
            # Check individual items have price and subtotal
            items = order.get("items", [])
            if not items:
                print_result(False, "Order has no items")
                return False
            
            items_correct = 0
            for item in items:
                name = item.get("name")
                quantity = item.get("quantity")
                price = item.get("price")
                subtotal = item.get("subtotal")
                
                if price is None:
                    print_result(False, f"Item {name} missing price field")
                    continue
                
                if subtotal is None:
                    print_result(False, f"Item {name} missing subtotal field")
                    continue
                
                expected_subtotal = price * quantity
                if abs(subtotal - expected_subtotal) < 0.01:
                    print_result(True, f"{name}: ${price:.2f} × {quantity} = ${subtotal:.2f} ✓")
                    items_correct += 1
                else:
                    print_result(False, f"{name}: Expected subtotal ${expected_subtotal:.2f}, got ${subtotal:.2f}")
            
            if items_correct == len(items):
                print_result(True, f"All {len(items)} items have correct price calculations")
                return True
            else:
                print_result(False, f"Only {items_correct}/{len(items)} items have correct calculations")
                return False
                
        else:
            print_result(False, f"Failed to create order: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing order creation pricing: {str(e)}")
        return False

def test_order_update_recalculates_prices():
    """HIGH PRIORITY: Test order update recalculates prices and totals"""
    print_test_header("Order Update Recalculates Prices and Totals")
    
    if not auth_token or not created_order_id:
        print_result(False, "No auth token or order ID available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Update order with different items
        update_data = {
            "customerName": "Updated Customer",
            "phoneNumber": "1234567890",
            "items": [
                {"name": "Chicken Biryani", "quantity": 1},  # $12.99
                {"name": "Dosa", "quantity": 2}              # $10.99 * 2 = $21.98
                # Total expected: $34.97
            ],
            "paymentMethod": "cashapp"
        }
        
        response = requests.put(f"{API_URL}/orders/{created_order_id}", json=update_data, headers=headers)
        
        if response.status_code == 200:
            updated_order = response.json()
            
            # Check if total amount was recalculated
            total_amount = updated_order.get("totalAmount")
            expected_total = 34.97  # Chicken Biryani: $12.99 + Dosa: $10.99 * 2
            
            if abs(total_amount - expected_total) < 0.01:
                print_result(True, f"Total amount recalculated correctly: ${total_amount:.2f}")
            else:
                print_result(False, f"Total amount incorrect: Expected ${expected_total:.2f}, got ${total_amount:.2f}")
                return False
            
            # Check individual items were updated with correct prices
            items = updated_order.get("items", [])
            items_correct = 0
            
            for item in items:
                name = item.get("name")
                quantity = item.get("quantity")
                price = item.get("price")
                subtotal = item.get("subtotal")
                
                expected_subtotal = price * quantity
                if abs(subtotal - expected_subtotal) < 0.01:
                    print_result(True, f"{name}: ${price:.2f} × {quantity} = ${subtotal:.2f} ✓")
                    items_correct += 1
                else:
                    print_result(False, f"{name}: Expected subtotal ${expected_subtotal:.2f}, got ${subtotal:.2f}")
            
            if items_correct == len(items):
                print_result(True, f"All {len(items)} updated items have correct price calculations")
                return True
            else:
                print_result(False, f"Only {items_correct}/{len(items)} updated items have correct calculations")
                return False
                
        else:
            print_result(False, f"Failed to update order: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing order update pricing: {str(e)}")
        return False

def test_invalid_menu_items_rejected():
    """HIGH PRIORITY: Test that invalid menu items are rejected during order creation"""
    print_test_header("Invalid Menu Items Rejected During Order Creation")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.post(f"{API_URL}/orders/", json=INVALID_MENU_ORDER, headers=headers)
        
        # Should fail with 500 error (ValueError from menu item not found)
        if response.status_code == 500:
            print_result(True, "Correctly rejected order with invalid menu item")
            return True
        else:
            print_result(False, f"Should have rejected invalid menu item, got status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing invalid menu item rejection: {str(e)}")
        return False

def test_orders_display_pricing_information():
    """MEDIUM PRIORITY: Test orders display individual item prices and subtotals"""
    print_test_header("Orders Display Individual Item Prices and Subtotals")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Create a new order with multiple items for testing
        response = requests.post(f"{API_URL}/orders/", json=BIRYANI_ORDER, headers=headers)
        
        if response.status_code == 201:
            order = response.json()
            order_id = order.get("id")
            
            # Verify the created order has all pricing fields
            items = order.get("items", [])
            if not items:
                print_result(False, "Order has no items")
                return False
            
            all_fields_present = True
            for item in items:
                name = item.get("name")
                has_price = "price" in item
                has_subtotal = "subtotal" in item
                has_quantity = "quantity" in item
                
                if has_price and has_subtotal and has_quantity:
                    print_result(True, f"{name}: Has price, quantity, and subtotal fields ✓")
                else:
                    missing_fields = []
                    if not has_price: missing_fields.append("price")
                    if not has_subtotal: missing_fields.append("subtotal")
                    if not has_quantity: missing_fields.append("quantity")
                    print_result(False, f"{name}: Missing fields: {', '.join(missing_fields)}")
                    all_fields_present = False
            
            # Check if order has totalAmount
            if "totalAmount" in order:
                print_result(True, f"Order has totalAmount: ${order['totalAmount']:.2f}")
            else:
                print_result(False, "Order missing totalAmount field")
                all_fields_present = False
            
            return all_fields_present
            
        else:
            print_result(False, f"Failed to create test order: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing order pricing display: {str(e)}")
        return False

def test_myorder_endpoint_returns_pricing():
    """MEDIUM PRIORITY: Test MyOrder endpoint returns orders with pricing information"""
    print_test_header("MyOrder Endpoint Returns Orders with Pricing Information")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Use a unique phone number for this test
    test_phone = "9999999999"
    
    try:
        # First create a fresh order with this phone number
        test_order = {
            "customerName": "MyOrder Test Customer",
            "phoneNumber": test_phone,
            "items": [
                {"name": "Tea", "quantity": 1},      # $2.00
                {"name": "Coffee", "quantity": 2}    # $3.00 * 2 = $6.00
                # Total expected: $8.00
            ],
            "paymentMethod": "cash"
        }
        
        create_response = requests.post(f"{API_URL}/orders/", json=test_order, headers=headers)
        
        if create_response.status_code != 201:
            print_result(False, f"Failed to create test order: {create_response.status_code}")
            return False
        
        created_order = create_response.json()
        print_result(True, f"Created test order with phone {test_phone}")
        
        # Now test the MyOrder endpoint
        response = requests.get(f"{API_URL}/orders/myorder/{test_phone}")
        
        if response.status_code == 200:
            orders = response.json()
            
            if not orders:
                print_result(False, "No orders found for test phone number")
                return False
            
            print_result(True, f"Retrieved {len(orders)} orders for phone {test_phone}")
            
            # Check if orders have pricing information
            orders_with_pricing = 0
            for order in orders:
                has_total_amount = "totalAmount" in order
                items = order.get("items", [])
                
                items_have_pricing = True
                for item in items:
                    if not ("price" in item and "subtotal" in item):
                        items_have_pricing = False
                        break
                
                if has_total_amount and items_have_pricing:
                    orders_with_pricing += 1
                    total_amount = order.get("totalAmount")
                    print_result(True, f"Order {order.get('id', 'Unknown')}: Has complete pricing information (${total_amount:.2f}) ✓")
                else:
                    print_result(False, f"Order {order.get('id', 'Unknown')}: Missing pricing information")
            
            if orders_with_pricing == len(orders):
                print_result(True, f"All {len(orders)} orders have complete pricing information")
                return True
            else:
                print_result(False, f"Only {orders_with_pricing}/{len(orders)} orders have complete pricing")
                return False
                
        else:
            print_result(False, f"Failed to get orders by phone: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing MyOrder endpoint pricing: {str(e)}")
        return False

def test_optional_phone_number_still_works():
    """Test that optional phone number functionality still works with pricing"""
    print_test_header("Optional Phone Number Still Works with Pricing")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Create order without phone number
        order_without_phone = {
            "customerName": "No Phone Customer",
            "items": [
                {"name": "Tea", "quantity": 1}  # $2.00
            ],
            "paymentMethod": "cash"
        }
        
        response = requests.post(f"{API_URL}/orders/", json=order_without_phone, headers=headers)
        
        if response.status_code == 201:
            order = response.json()
            
            # Check pricing is still calculated
            total_amount = order.get("totalAmount")
            expected_total = 2.00
            
            if abs(total_amount - expected_total) < 0.01:
                print_result(True, f"Order without phone has correct pricing: ${total_amount:.2f}")
                
                # Check phone number is None
                phone_number = order.get("phoneNumber")
                if phone_number is None:
                    print_result(True, "Phone number is correctly None")
                    return True
                else:
                    print_result(False, f"Expected phone number to be None, got {phone_number}")
                    return False
            else:
                print_result(False, f"Pricing incorrect: Expected ${expected_total:.2f}, got ${total_amount:.2f}")
                return False
                
        else:
            print_result(False, f"Failed to create order without phone: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing optional phone with pricing: {str(e)}")
        return False

def run_all_pricing_tests():
    """Run all pricing functionality tests"""
    print(f"🚀 Starting Pricing Functionality Tests")
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get authentication token first
    if not get_auth_token():
        print("❌ Cannot proceed without authentication")
        return False
    
    # Run all tests in priority order
    tests = [
        # HIGH PRIORITY TESTS
        ("Menu Items Include Prices", test_menu_items_include_prices),
        ("Order Creation Calculates Prices and Totals", test_order_creation_calculates_prices),
        ("Order Update Recalculates Prices and Totals", test_order_update_recalculates_prices),
        ("Invalid Menu Items Rejected During Order Creation", test_invalid_menu_items_rejected),
        
        # MEDIUM PRIORITY TESTS
        ("Orders Display Individual Item Prices and Subtotals", test_orders_display_pricing_information),
        ("MyOrder Endpoint Returns Orders with Pricing Information", test_myorder_endpoint_returns_pricing),
        
        # COMPATIBILITY TEST
        ("Optional Phone Number Still Works with Pricing", test_optional_phone_number_still_works)
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
    print("📊 PRICING FUNCTIONALITY TEST SUMMARY")
    print('='*60)
    
    passed = 0
    total = len(results)
    high_priority_passed = 0
    high_priority_total = 4  # First 4 tests are high priority
    
    for i, (test_name, result) in enumerate(results):
        status = "✅ PASS" if result else "❌ FAIL"
        priority = "HIGH" if i < high_priority_total else "MEDIUM/LOW"
        print(f"{status} [{priority}] {test_name}")
        if result:
            passed += 1
            if i < high_priority_total:
                high_priority_passed += 1
    
    print(f"\n🎯 Overall Results: {passed}/{total} tests passed")
    print(f"🔥 High Priority Results: {high_priority_passed}/{high_priority_total} tests passed")
    
    if passed == total:
        print("🎉 All pricing functionality tests PASSED!")
        return True
    elif high_priority_passed == high_priority_total:
        print("✅ All HIGH PRIORITY pricing tests PASSED!")
        print("⚠️  Some medium/low priority tests failed - check implementation")
        return True
    else:
        print("❌ Some HIGH PRIORITY tests FAILED - pricing functionality needs fixes")
        return False

if __name__ == "__main__":
    success = run_all_pricing_tests()
    sys.exit(0 if success else 1)
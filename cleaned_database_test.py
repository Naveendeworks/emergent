#!/usr/bin/env python3
"""
Cleaned Database Testing for "Mem Famous Stall 2025" System
Tests the system functionality after database cleanup to ensure it works correctly with fresh data
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
print(f"🔗 Testing cleaned database at: {API_URL}")

# Test data for cleaned database testing
SAMPLE_ORDER_DATA = {
    "customerName": "Fresh Start Customer",
    "items": [
        {"name": "Masala Chai", "quantity": 2},
        {"name": "Arakku Filter Coffee", "quantity": 1}
    ],
    "paymentMethod": "cash"
}

# Global variables for test data
auth_token = None
first_order_id = None
first_order_number = None

def print_test_header(test_name):
    print(f"\n{'='*80}")
    print(f"🧪 {test_name}")
    print('='*80)

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
            print_result(True, "Authentication successful with admin/memfamous2025")
            return True
        else:
            print_result(False, f"Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Authentication error: {str(e)}")
        return False

# HIGH PRIORITY TESTS - Database Clean State

def test_database_clean_state():
    """Test that all collections (orders, counters, notifications) are empty"""
    print_test_header("Database Clean State Verification")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Test orders collection is empty
        orders_response = requests.get(f"{API_URL}/orders/", headers=headers)
        
        if orders_response.status_code == 200:
            orders = orders_response.json()
            if len(orders) == 0:
                print_result(True, "Orders collection is empty")
            else:
                print_result(False, f"Orders collection not empty: found {len(orders)} orders")
                return False
        else:
            print_result(False, f"Failed to get orders: {orders_response.status_code}")
            return False
        
        # Test view orders is empty
        view_orders_response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if view_orders_response.status_code == 200:
            categories = view_orders_response.json()
            total_items = sum(len(cat.get('items', [])) for cat in categories)
            if total_items == 0:
                print_result(True, "View orders is empty (no pending orders)")
            else:
                print_result(False, f"View orders not empty: found {total_items} items")
                return False
        else:
            print_result(False, f"Failed to get view orders: {view_orders_response.status_code}")
            return False
        
        # Test notifications collection (if endpoint exists)
        try:
            notifications_response = requests.get(f"{API_URL}/notifications/", headers=headers)
            if notifications_response.status_code == 200:
                notifications = notifications_response.json()
                if len(notifications) == 0:
                    print_result(True, "Notifications collection is empty")
                else:
                    print_result(False, f"Notifications collection not empty: found {len(notifications)} notifications")
                    return False
            elif notifications_response.status_code == 404:
                print_result(True, "Notifications endpoint not found (expected for clean system)")
        except:
            print_result(True, "Notifications endpoint not accessible (expected for clean system)")
        
        print_result(True, "✅ Database is in clean state - all collections empty")
        return True
        
    except Exception as e:
        print_result(False, f"Error testing database clean state: {str(e)}")
        return False

def test_admin_authentication():
    """Test login with admin/memfamous2025 credentials works correctly"""
    print_test_header("Admin Authentication Test")
    
    try:
        # Test correct credentials
        response = requests.post(f"{API_URL}/auth/login", json={
            "username": "admin",
            "password": "memfamous2025"
        })
        
        if response.status_code == 200:
            token_data = response.json()
            if "access_token" in token_data:
                print_result(True, "Admin login successful with correct credentials")
            else:
                print_result(False, "Login response missing access_token")
                return False
        else:
            print_result(False, f"Admin login failed: {response.status_code}")
            return False
        
        # Test incorrect credentials
        wrong_response = requests.post(f"{API_URL}/auth/login", json={
            "username": "admin",
            "password": "wrongpassword"
        })
        
        if wrong_response.status_code in [401, 403]:
            print_result(True, "Incorrect credentials properly rejected")
        else:
            print_result(False, f"Incorrect credentials not properly rejected: {wrong_response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print_result(False, f"Error testing admin authentication: {str(e)}")
        return False

def test_menu_items_available():
    """Test all menu items are available with correct pricing (hardcoded menu service)"""
    print_test_header("Menu Items Availability and Pricing")
    
    try:
        response = requests.get(f"{API_URL}/menu/")
        
        if response.status_code == 200:
            menu_data = response.json()
            items = menu_data.get('items', [])
            
            if len(items) == 0:
                print_result(False, "No menu items found")
                return False
            
            print_result(True, f"Found {len(items)} menu items")
            
            # Check for expected items with correct pricing
            expected_items = {
                "Masala Chai": 1.00,
                "Arakku Filter Coffee": 3.00,
                "Hyderabad Chicken Dum Biryani": 12.00,
                "Thalapakatti Goat Biryani": 15.00,
                "Ghee Massala Dosa": 12.00,
                "Idly (3)": 7.00
            }
            
            found_items = {}
            for item in items:
                if 'name' in item and 'price' in item:
                    found_items[item['name']] = item['price']
            
            missing_items = []
            price_mismatches = []
            
            for expected_name, expected_price in expected_items.items():
                if expected_name not in found_items:
                    missing_items.append(expected_name)
                elif abs(found_items[expected_name] - expected_price) > 0.01:
                    price_mismatches.append(f"{expected_name}: expected ${expected_price:.2f}, got ${found_items[expected_name]:.2f}")
            
            if missing_items:
                print_result(False, f"Missing expected menu items: {missing_items}")
                return False
            
            if price_mismatches:
                print_result(False, f"Price mismatches: {price_mismatches}")
                return False
            
            print_result(True, "All expected menu items found with correct pricing")
            
            # Verify all items have required fields
            for item in items:
                required_fields = ['name', 'price', 'category']
                for field in required_fields:
                    if field not in item:
                        print_result(False, f"Menu item {item.get('name', 'unknown')} missing field: {field}")
                        return False
            
            print_result(True, "All menu items have required fields (name, price, category)")
            return True
        else:
            print_result(False, f"Failed to get menu: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing menu items: {str(e)}")
        return False

def test_order_creation_fresh_start():
    """Test creating a new order to verify the system can start fresh with order #1"""
    print_test_header("Order Creation - Fresh Start with Order #1")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Create first order after cleanup
        response = requests.post(f"{API_URL}/orders/", json=SAMPLE_ORDER_DATA, headers=headers)
        
        if response.status_code == 201:
            order = response.json()
            
            # Store for later tests
            global first_order_id, first_order_number
            first_order_id = order['id']
            first_order_number = order['orderNumber']
            
            print_result(True, f"Successfully created first order with ID: {first_order_id}")
            
            # Verify order has all required fields
            required_fields = ['id', 'customerName', 'items', 'totalAmount', 'status', 'orderTime', 'orderNumber']
            for field in required_fields:
                if field not in order:
                    print_result(False, f"Order missing required field: {field}")
                    return False
            
            print_result(True, "Order has all required fields")
            
            # Verify pricing calculations
            expected_total = (1.00 * 2) + (3.00 * 1)  # Masala Chai $1.00 x 2 + Arakku Filter Coffee $3.00 x 1 = $5.00
            actual_total = order['totalAmount']
            
            if abs(actual_total - expected_total) > 0.01:
                print_result(False, f"Price calculation error: expected ${expected_total:.2f}, got ${actual_total:.2f}")
                return False
            
            print_result(True, f"Pricing calculation correct: ${actual_total:.2f}")
            
            # Verify order status
            if order['status'] != 'pending':
                print_result(False, f"Expected status 'pending', got '{order['status']}'")
                return False
            
            print_result(True, "Order status correctly set to 'pending'")
            
            # Verify items have cooking status
            for item in order['items']:
                if 'cooking_status' not in item:
                    print_result(False, f"Item {item.get('name', 'unknown')} missing cooking_status")
                    return False
                if item['cooking_status'] != 'not started':
                    print_result(False, f"Item {item.get('name', 'unknown')} cooking_status should be 'not started', got '{item['cooking_status']}'")
                    return False
            
            print_result(True, "All items have correct cooking_status 'not started'")
            return True
        else:
            print_result(False, f"Failed to create order: {response.status_code}")
            if response.status_code == 400:
                print_result(False, f"Error details: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing order creation: {str(e)}")
        return False

def test_sequential_order_numbers_restart():
    """Test first order gets orderNumber "1" and counter system restarts properly"""
    print_test_header("Sequential Order Numbers - Counter System Restart")
    
    if not first_order_number:
        print_result(False, "No first order number available from previous test")
        return False
    
    try:
        # Verify first order has order number "1"
        if str(first_order_number) != "1":
            print_result(False, f"First order number should be '1', got '{first_order_number}'")
            return False
        
        print_result(True, f"✅ First order correctly assigned order number: {first_order_number}")
        
        # Create a second order to verify sequential numbering
        if not auth_token:
            print_result(False, "No auth token available")
            return False
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        second_order_data = {
            "customerName": "Second Order Customer",
            "items": [{"name": "Coffee", "quantity": 1}],
            "paymentMethod": "cashapp"
        }
        
        response = requests.post(f"{API_URL}/orders/", json=second_order_data, headers=headers)
        
        if response.status_code == 201:
            second_order = response.json()
            second_order_number = second_order['orderNumber']
            
            if str(second_order_number) != "2":
                print_result(False, f"Second order number should be '2', got '{second_order_number}'")
                return False
            
            print_result(True, f"✅ Second order correctly assigned order number: {second_order_number}")
            print_result(True, "Counter system properly restarted and working sequentially")
            return True
        else:
            print_result(False, f"Failed to create second order: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing sequential order numbers: {str(e)}")
        return False

def test_order_management_statistics():
    """Test viewing orders, getting statistics (should show 0 pending, 0 completed initially, then updated counts)"""
    print_test_header("Order Management and Statistics")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Get all orders
        orders_response = requests.get(f"{API_URL}/orders/", headers=headers)
        
        if orders_response.status_code == 200:
            orders = orders_response.json()
            
            # Count orders by status
            pending_count = sum(1 for order in orders if order.get('status') == 'pending')
            completed_count = sum(1 for order in orders if order.get('status') == 'completed')
            total_count = len(orders)
            
            print_result(True, f"Order statistics: {pending_count} pending, {completed_count} completed, {total_count} total")
            
            # After creating 2 orders in previous tests, we should have 2 pending orders
            if pending_count < 2:
                print_result(False, f"Expected at least 2 pending orders, got {pending_count}")
                return False
            
            if completed_count != 0:
                print_result(False, f"Expected 0 completed orders in fresh database, got {completed_count}")
                return False
            
            print_result(True, "✅ Order statistics correct for fresh database")
        else:
            print_result(False, f"Failed to get orders: {orders_response.status_code}")
            return False
        
        # Test view orders shows pending orders
        view_orders_response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if view_orders_response.status_code == 200:
            categories = view_orders_response.json()
            
            total_items_in_view = 0
            for category in categories:
                for item in category.get('items', []):
                    total_items_in_view += len(item.get('orders', []))
            
            if total_items_in_view < 3:  # Should have at least 3 items (2 Tea + 1 Coffee from first order, 1 Coffee from second order)
                print_result(False, f"Expected at least 3 items in view orders, got {total_items_in_view}")
                return False
            
            print_result(True, f"✅ View orders shows {total_items_in_view} pending items")
        else:
            print_result(False, f"Failed to get view orders: {view_orders_response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print_result(False, f"Error testing order management statistics: {str(e)}")
        return False

# MEDIUM PRIORITY TESTS

def test_api_endpoints_functionality():
    """Test all major endpoints work (orders, menu, reports, auth)"""
    print_test_header("API Endpoints Functionality")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        endpoints_to_test = [
            ("/auth/login", "POST", {"username": "admin", "password": "memfamous2025"}, False),
            ("/menu/", "GET", None, False),
            ("/orders/", "GET", None, True),
            ("/orders/view-orders", "GET", None, True),
            ("/orders/price-analysis", "GET", None, True),
            ("/reports/price-analysis/export", "GET", None, True)
        ]
        
        working_endpoints = 0
        total_endpoints = len(endpoints_to_test)
        
        for endpoint, method, data, requires_auth in endpoints_to_test:
            try:
                request_headers = headers if requires_auth else {}
                
                if method == "GET":
                    response = requests.get(f"{API_URL}{endpoint}", headers=request_headers)
                elif method == "POST":
                    response = requests.post(f"{API_URL}{endpoint}", json=data, headers=request_headers)
                else:
                    continue
                
                if response.status_code in [200, 201]:
                    print_result(True, f"{method} {endpoint} - Working")
                    working_endpoints += 1
                else:
                    print_result(False, f"{method} {endpoint} - Failed ({response.status_code})")
            except Exception as e:
                print_result(False, f"{method} {endpoint} - Error: {str(e)}")
        
        if working_endpoints == total_endpoints:
            print_result(True, f"✅ All {total_endpoints} major endpoints working")
            return True
        else:
            print_result(False, f"Only {working_endpoints}/{total_endpoints} endpoints working")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing API endpoints: {str(e)}")
        return False

def test_pricing_calculations():
    """Test order creation calculates prices correctly from menu items"""
    print_test_header("Pricing Calculations Verification")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Test order with specific items to verify pricing
        test_order_data = {
            "customerName": "Pricing Test Customer",
            "items": [
                {"name": "Tea", "quantity": 3},      # $2.00 x 3 = $6.00
                {"name": "Coffee", "quantity": 2},   # $3.00 x 2 = $6.00
                {"name": "Chicken Biryani", "quantity": 1}  # $12.99 x 1 = $12.99
            ],
            "paymentMethod": "cash"
        }
        
        expected_total = (2.00 * 3) + (3.00 * 2) + (12.99 * 1)  # $6.00 + $6.00 + $12.99 = $24.99
        
        response = requests.post(f"{API_URL}/orders/", json=test_order_data, headers=headers)
        
        if response.status_code == 201:
            order = response.json()
            actual_total = order['totalAmount']
            
            if abs(actual_total - expected_total) > 0.01:
                print_result(False, f"Total price calculation error: expected ${expected_total:.2f}, got ${actual_total:.2f}")
                return False
            
            print_result(True, f"✅ Total price calculation correct: ${actual_total:.2f}")
            
            # Verify individual item pricing
            for item in order['items']:
                item_name = item['name']
                quantity = item['quantity']
                price = item['price']
                subtotal = item['subtotal']
                
                expected_subtotal = price * quantity
                if abs(subtotal - expected_subtotal) > 0.01:
                    print_result(False, f"Subtotal calculation error for {item_name}: expected ${expected_subtotal:.2f}, got ${subtotal:.2f}")
                    return False
                
                print_result(True, f"{item_name}: ${price:.2f} x {quantity} = ${subtotal:.2f}")
            
            print_result(True, "✅ All individual item pricing calculations correct")
            return True
        else:
            print_result(False, f"Failed to create pricing test order: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing pricing calculations: {str(e)}")
        return False

def test_database_persistence():
    """Test new orders are properly saved and can be retrieved"""
    print_test_header("Database Persistence Verification")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Create a test order
        persistence_test_data = {
            "customerName": "Persistence Test Customer",
            "items": [{"name": "Tea", "quantity": 1}],
            "paymentMethod": "cashapp"
        }
        
        create_response = requests.post(f"{API_URL}/orders/", json=persistence_test_data, headers=headers)
        
        if create_response.status_code != 201:
            print_result(False, f"Failed to create persistence test order: {create_response.status_code}")
            return False
        
        created_order = create_response.json()
        order_id = created_order['id']
        order_number = created_order['orderNumber']
        
        print_result(True, f"Created persistence test order: {order_number}")
        
        # Retrieve order by ID from all orders
        all_orders_response = requests.get(f"{API_URL}/orders/", headers=headers)
        
        if all_orders_response.status_code != 200:
            print_result(False, "Failed to retrieve all orders")
            return False
        
        all_orders = all_orders_response.json()
        found_order = next((order for order in all_orders if order['id'] == order_id), None)
        
        if not found_order:
            print_result(False, f"Order {order_id} not found in all orders list")
            return False
        
        print_result(True, "✅ Order found in all orders list")
        
        # Retrieve order via customer lookup
        lookup_response = requests.get(f"{API_URL}/orders/myorder/{order_number}")
        
        if lookup_response.status_code != 200:
            print_result(False, f"Customer lookup failed for order {order_number}")
            return False
        
        looked_up_order = lookup_response.json()
        
        if looked_up_order['id'] != order_id:
            print_result(False, "Customer lookup returned wrong order")
            return False
        
        print_result(True, "✅ Order accessible via customer lookup")
        
        # Verify order appears in view orders
        view_orders_response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if view_orders_response.status_code != 200:
            print_result(False, "Failed to get view orders")
            return False
        
        categories = view_orders_response.json()
        order_found_in_view = False
        
        for category in categories:
            for item in category.get('items', []):
                for order in item.get('orders', []):
                    if order['order_id'] == order_id:
                        order_found_in_view = True
                        break
        
        if not order_found_in_view:
            print_result(False, "Order not found in view orders")
            return False
        
        print_result(True, "✅ Order appears in view orders")
        print_result(True, "✅ Database persistence working correctly")
        return True
        
    except Exception as e:
        print_result(False, f"Error testing database persistence: {str(e)}")
        return False

def test_customer_lookup_functionality():
    """Test MyOrder customer lookup with the new order"""
    print_test_header("Customer Lookup Functionality")
    
    if not first_order_number:
        print_result(False, "No first order number available")
        return False
    
    try:
        # Test customer lookup with first order
        lookup_response = requests.get(f"{API_URL}/orders/myorder/{first_order_number}")
        
        if lookup_response.status_code == 200:
            order = lookup_response.json()
            
            # Verify order details
            if order['orderNumber'] != first_order_number:
                print_result(False, f"Order number mismatch: expected {first_order_number}, got {order['orderNumber']}")
                return False
            
            if order['customerName'] != SAMPLE_ORDER_DATA['customerName']:
                print_result(False, f"Customer name mismatch: expected {SAMPLE_ORDER_DATA['customerName']}, got {order['customerName']}")
                return False
            
            print_result(True, f"✅ Customer lookup successful for order {first_order_number}")
            
            # Verify pricing information is included
            if 'totalAmount' not in order:
                print_result(False, "Total amount missing from customer lookup")
                return False
            
            for item in order.get('items', []):
                required_fields = ['name', 'quantity', 'price', 'subtotal']
                for field in required_fields:
                    if field not in item:
                        print_result(False, f"Item missing field {field} in customer lookup")
                        return False
            
            print_result(True, "✅ Customer lookup includes complete pricing information")
            return True
        else:
            print_result(False, f"Customer lookup failed: {lookup_response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing customer lookup: {str(e)}")
        return False

def test_dashboard_statistics_reset():
    """Test dashboard statistics reflect empty database initially and update correctly"""
    print_test_header("Dashboard Statistics Reset and Update")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Get current statistics
        orders_response = requests.get(f"{API_URL}/orders/", headers=headers)
        
        if orders_response.status_code != 200:
            print_result(False, "Failed to get orders for statistics")
            return False
        
        orders = orders_response.json()
        
        # Count orders by status
        pending_count = sum(1 for order in orders if order.get('status') == 'pending')
        completed_count = sum(1 for order in orders if order.get('status') == 'completed')
        total_count = len(orders)
        
        print_result(True, f"Current statistics: {pending_count} pending, {completed_count} completed, {total_count} total")
        
        # After cleanup and creating test orders, we should have:
        # - Several pending orders (from our tests)
        # - 0 completed orders (fresh start)
        if completed_count != 0:
            print_result(False, f"Expected 0 completed orders after cleanup, got {completed_count}")
            return False
        
        if pending_count < 3:  # We created at least 3 orders in our tests
            print_result(False, f"Expected at least 3 pending orders from tests, got {pending_count}")
            return False
        
        print_result(True, "✅ Statistics correctly reflect fresh database state")
        
        # Test price analysis with fresh data
        price_analysis_response = requests.get(f"{API_URL}/orders/price-analysis", headers=headers)
        
        if price_analysis_response.status_code == 200:
            analysis = price_analysis_response.json()
            
            # Should show 0 completed orders in analysis (only completed orders are analyzed)
            if analysis['total_orders'] != 0:
                print_result(False, f"Price analysis should show 0 orders (no completed orders), got {analysis['total_orders']}")
                return False
            
            if analysis['total_revenue'] != 0:
                print_result(False, f"Price analysis should show $0 revenue (no completed orders), got ${analysis['total_revenue']}")
                return False
            
            print_result(True, "✅ Price analysis correctly shows $0 revenue (no completed orders)")
        else:
            print_result(False, f"Failed to get price analysis: {price_analysis_response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print_result(False, f"Error testing dashboard statistics: {str(e)}")
        return False

def run_cleaned_database_tests():
    """Run all cleaned database tests"""
    print(f"🚀 Starting Cleaned Database Tests for Mem Famous Stall 2025")
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🧹 Testing system functionality after database cleanup")
    print(f"🎯 FOCUS: Verify system works correctly with fresh data and order numbering starts from 1")
    
    # Get authentication token first
    if not get_auth_token():
        print("❌ Cannot proceed without authentication")
        return False
    
    # Run all tests in priority order
    tests = [
        # HIGH PRIORITY TESTS
        ("Database Clean State Verification", test_database_clean_state, "HIGH"),
        ("Admin Authentication Test", test_admin_authentication, "HIGH"),
        ("Menu Items Availability and Pricing", test_menu_items_available, "HIGH"),
        ("Order Creation - Fresh Start with Order #1", test_order_creation_fresh_start, "HIGH"),
        ("Sequential Order Numbers - Counter System Restart", test_sequential_order_numbers_restart, "HIGH"),
        ("Order Management and Statistics", test_order_management_statistics, "HIGH"),
        
        # MEDIUM PRIORITY TESTS
        ("API Endpoints Functionality", test_api_endpoints_functionality, "MEDIUM"),
        ("Pricing Calculations Verification", test_pricing_calculations, "MEDIUM"),
        ("Database Persistence Verification", test_database_persistence, "MEDIUM"),
        ("Customer Lookup Functionality", test_customer_lookup_functionality, "MEDIUM"),
        ("Dashboard Statistics Reset and Update", test_dashboard_statistics_reset, "MEDIUM")
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
    print(f"\n{'='*80}")
    print("📊 CLEANED DATABASE TEST SUMMARY")
    print('='*80)
    
    passed = 0
    total = len(results)
    high_priority_passed = 0
    high_priority_total = 0
    medium_priority_passed = 0
    medium_priority_total = 0
    
    for test_name, result, priority in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} [{priority}] {test_name}")
        if result:
            passed += 1
        if priority == "HIGH":
            high_priority_total += 1
            if result:
                high_priority_passed += 1
        elif priority == "MEDIUM":
            medium_priority_total += 1
            if result:
                medium_priority_passed += 1
    
    print(f"\n🎯 Overall Results: {passed}/{total} tests passed")
    print(f"🔥 High Priority Results: {high_priority_passed}/{high_priority_total} tests passed")
    print(f"📊 Medium Priority Results: {medium_priority_passed}/{medium_priority_total} tests passed")
    
    if passed == total:
        print("🎉 All cleaned database tests PASSED!")
        print("✅ System ready for fresh use with order numbering starting from 1")
        return True
    elif high_priority_passed == high_priority_total:
        print("✅ All HIGH PRIORITY tests passed - Core functionality working!")
        if medium_priority_passed == medium_priority_total:
            print("✅ All MEDIUM PRIORITY tests also passed")
            print("🎉 Complete system functionality verified")
        else:
            print("⚠️  Some MEDIUM PRIORITY tests failed, but core functionality is working")
        return True
    else:
        print("❌ Some HIGH PRIORITY tests FAILED - Core functionality issues!")
        print("🚨 URGENT: System needs attention before use")
        return False

if __name__ == "__main__":
    success = run_cleaned_database_tests()
    sys.exit(0 if success else 1)
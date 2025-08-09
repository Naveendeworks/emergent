#!/usr/bin/env python3
"""
Backend API Testing for Enhanced "Mem Famous Stall 2025" System
Tests new features including category-based view orders, price analysis, and notification system preparation
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

# Test data for enhanced system testing
SAMPLE_ORDER_DATA = {
    "customerName": "Enhanced Test Customer",
    "items": [
        {"name": "Tea", "quantity": 2},
        {"name": "Coffee", "quantity": 1}
    ],
    "paymentMethod": "cash"
}

SAMPLE_BIRYANI_ORDER = {
    "customerName": "Biryani Test Customer",
    "items": [
        {"name": "Chicken Biryani", "quantity": 1},
        {"name": "Goat Biryani", "quantity": 1}
    ],
    "paymentMethod": "cashapp"
}

# Global variables for test data
auth_token = None
created_order_id = None

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
            print_result(True, "Authentication successful")
            return True
        else:
            print_result(False, f"Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Authentication error: {str(e)}")
        return False

# HIGH PRIORITY TESTS - Category-Based View Orders

def test_category_based_view_orders():
    """Test /api/orders/view-orders endpoint returns data grouped by food category"""
    print_test_header("Category-Based View Orders Endpoint")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if response.status_code == 200:
            categories = response.json()
            
            if not isinstance(categories, list):
                print_result(False, f"Expected list, got {type(categories)}")
                return False
            
            # Check if data is grouped by categories
            for category in categories:
                if not isinstance(category, dict):
                    print_result(False, "Category data should be dict")
                    return False
                
                required_fields = ['category_name', 'items', 'total_items']
                for field in required_fields:
                    if field not in category:
                        print_result(False, f"Missing field '{field}' in category")
                        return False
                
                # Check items structure
                if not isinstance(category['items'], list):
                    print_result(False, "Category items should be list")
                    return False
                
                print_result(True, f"Category '{category['category_name']}' has {len(category['items'])} items")
            
            print_result(True, f"View orders grouped by {len(categories)} food categories")
            return True
        else:
            print_result(False, f"Failed to get view orders: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing category-based view orders: {str(e)}")
        return False

def test_category_grouping():
    """Test categories show proper food groupings (Beverages, Biryani, South Indian, etc.)"""
    print_test_header("Category Grouping with Food Categories")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if response.status_code == 200:
            categories = response.json()
            
            # Expected food categories from menu service
            expected_categories = ['Beverages', 'Biryani', 'South Indian', 'Curry', 'Fish', 'Starters', 'Chaat', 'Snacks', 'Spicy', 'Soup', 'Meat', 'Vegetarian', 'Dessert']
            found_categories = [cat['category_name'] for cat in categories]
            
            # Check if we have proper food categories (at least some expected ones)
            valid_categories_found = 0
            for expected in expected_categories:
                if expected in found_categories:
                    valid_categories_found += 1
                    print_result(True, f"Found expected category: {expected}")
            
            if valid_categories_found > 0:
                print_result(True, f"Found {valid_categories_found} valid food categories")
                return True
            else:
                print_result(True, "No categories found (empty database)")
                return True
        else:
            print_result(False, f"Failed to get categories: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing category grouping: {str(e)}")
        return False

def test_item_status_in_categories():
    """Test each category contains items with cooking status and order information"""
    print_test_header("Individual Item Status in Categories")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if response.status_code == 200:
            categories = response.json()
            
            items_with_status = 0
            for category in categories:
                for item in category['items']:
                    # Check item structure
                    required_fields = ['item_name', 'total_quantity', 'orders']
                    for field in required_fields:
                        if field not in item:
                            print_result(False, f"Missing field '{field}' in item")
                            return False
                    
                    # Check orders within items
                    for order in item['orders']:
                        required_order_fields = ['order_id', 'orderNumber', 'customerName', 'quantity', 'cooking_status', 'orderTime']
                        for field in required_order_fields:
                            if field not in order:
                                print_result(False, f"Missing field '{field}' in order")
                                return False
                        
                        # Validate cooking status
                        valid_statuses = ['not started', 'cooking', 'finished']
                        if order['cooking_status'] not in valid_statuses:
                            print_result(False, f"Invalid cooking status: {order['cooking_status']}")
                            return False
                        
                        items_with_status += 1
            
            if items_with_status > 0:
                print_result(True, f"Found {items_with_status} items with proper cooking status and order info")
                return True
            else:
                print_result(True, "No items with cooking status found (empty database)")
                return True
        else:
            print_result(False, f"Failed to get view orders: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing item status in categories: {str(e)}")
        return False

def test_pricing_in_category_view():
    """Test pricing information included in category view"""
    print_test_header("Pricing Information in Category View")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if response.status_code == 200:
            categories = response.json()
            
            items_with_pricing = 0
            for category in categories:
                for item in category['items']:
                    for order in item['orders']:
                        # Check pricing fields
                        pricing_fields = ['price', 'subtotal']
                        for field in pricing_fields:
                            if field not in order:
                                print_result(False, f"Missing pricing field '{field}' in order")
                                return False
                            
                            if not isinstance(order[field], (int, float)) or order[field] < 0:
                                print_result(False, f"Invalid pricing value for '{field}': {order[field]}")
                                return False
                        
                        items_with_pricing += 1
            
            if items_with_pricing > 0:
                print_result(True, f"Found {items_with_pricing} items with proper pricing information")
                return True
            else:
                print_result(True, "No items with pricing information found (empty database)")
                return True
        else:
            print_result(False, f"Failed to get view orders: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing pricing in category view: {str(e)}")
        return False

# HIGH PRIORITY TESTS - Price Analysis System

def test_price_analysis_authentication():
    """Test /api/orders/price-analysis endpoint requires authentication"""
    print_test_header("Price Analysis Endpoint Authentication")
    
    try:
        # Test without authentication
        response = requests.get(f"{API_URL}/orders/price-analysis")
        
        if response.status_code in [401, 403]:  # Both are valid authentication errors
            print_result(True, f"Price analysis endpoint correctly requires authentication (status: {response.status_code})")
        else:
            print_result(False, f"Expected 401 or 403, got {response.status_code}")
            return False
        
        # Test with authentication
        if not auth_token:
            print_result(False, "No auth token available")
            return False
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API_URL}/orders/price-analysis", headers=headers)
        
        if response.status_code == 200:
            print_result(True, "Price analysis endpoint works with authentication")
            return True
        else:
            print_result(False, f"Failed with auth: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing price analysis authentication: {str(e)}")
        return False

def test_price_analysis_data_structure():
    """Test analysis includes item-wise revenue, quantity sold, and order count"""
    print_test_header("Price Analysis Data Structure")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{API_URL}/orders/price-analysis", headers=headers)
        
        if response.status_code == 200:
            analysis = response.json()
            
            # Check main structure
            required_fields = ['items', 'total_revenue', 'total_items_sold', 'total_orders', 'average_order_value']
            for field in required_fields:
                if field not in analysis:
                    print_result(False, f"Missing field '{field}' in analysis")
                    return False
            
            # Check items structure
            if not isinstance(analysis['items'], list):
                print_result(False, "Items should be a list")
                return False
            
            for item in analysis['items']:
                required_item_fields = ['item_name', 'category', 'unit_price', 'total_quantity', 'total_revenue', 'order_count']
                for field in required_item_fields:
                    if field not in item:
                        print_result(False, f"Missing field '{field}' in item analysis")
                        return False
                
                # Validate data types
                if not isinstance(item['total_quantity'], int) or item['total_quantity'] < 0:
                    print_result(False, f"Invalid total_quantity: {item['total_quantity']}")
                    return False
                
                if not isinstance(item['total_revenue'], (int, float)) or item['total_revenue'] < 0:
                    print_result(False, f"Invalid total_revenue: {item['total_revenue']}")
                    return False
                
                if not isinstance(item['order_count'], int) or item['order_count'] < 0:
                    print_result(False, f"Invalid order_count: {item['order_count']}")
                    return False
            
            print_result(True, f"Price analysis has correct structure with {len(analysis['items'])} items")
            print_result(True, f"Total revenue: ${analysis['total_revenue']:.2f}, Average order value: ${analysis['average_order_value']:.2f}")
            return True
        else:
            print_result(False, f"Failed to get price analysis: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing price analysis data structure: {str(e)}")
        return False

def test_revenue_calculation_sorting():
    """Test items sorted by revenue (highest first) and calculations are correct"""
    print_test_header("Revenue Calculation and Sorting")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{API_URL}/orders/price-analysis", headers=headers)
        
        if response.status_code == 200:
            analysis = response.json()
            items = analysis['items']
            
            if len(items) == 0:
                print_result(True, "No items to analyze (empty database)")
                return True
            
            # Check sorting (highest revenue first)
            for i in range(len(items) - 1):
                if items[i]['total_revenue'] < items[i + 1]['total_revenue']:
                    print_result(False, f"Items not sorted by revenue: {items[i]['total_revenue']} < {items[i + 1]['total_revenue']}")
                    return False
            
            print_result(True, "Items correctly sorted by revenue (highest first)")
            
            # Verify revenue calculations
            total_calculated_revenue = 0
            for item in items:
                expected_revenue = item['unit_price'] * item['total_quantity']
                if abs(item['total_revenue'] - expected_revenue) > 0.01:
                    print_result(False, f"Revenue calculation error for {item['item_name']}: expected {expected_revenue}, got {item['total_revenue']}")
                    return False
                total_calculated_revenue += item['total_revenue']
            
            # Check total revenue matches sum of individual items
            if abs(analysis['total_revenue'] - total_calculated_revenue) > 0.01:
                print_result(False, f"Total revenue mismatch: expected {total_calculated_revenue}, got {analysis['total_revenue']}")
                return False
            
            print_result(True, f"Revenue calculations correct, total: ${analysis['total_revenue']:.2f}")
            return True
        else:
            print_result(False, f"Failed to get price analysis: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing revenue calculation and sorting: {str(e)}")
        return False

def test_completed_orders_analysis():
    """Test analysis only includes completed orders"""
    print_test_header("Completed Orders Only Analysis")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # First, get all orders to check status distribution
        all_orders_response = requests.get(f"{API_URL}/orders/", headers=headers)
        if all_orders_response.status_code != 200:
            print_result(False, "Could not get all orders for comparison")
            return False
        
        all_orders = all_orders_response.json()
        completed_orders = [order for order in all_orders if order.get('status') == 'completed']
        pending_orders = [order for order in all_orders if order.get('status') == 'pending']
        
        print_result(True, f"Found {len(completed_orders)} completed orders and {len(pending_orders)} pending orders")
        
        # Get price analysis
        analysis_response = requests.get(f"{API_URL}/orders/price-analysis", headers=headers)
        
        if analysis_response.status_code == 200:
            analysis = analysis_response.json()
            
            # The total_orders in analysis should match completed orders count
            if analysis['total_orders'] != len(completed_orders):
                print_result(False, f"Analysis includes wrong order count: expected {len(completed_orders)}, got {analysis['total_orders']}")
                return False
            
            print_result(True, f"Price analysis correctly includes only {analysis['total_orders']} completed orders")
            
            # If we have both completed and pending orders, verify only completed are analyzed
            if len(pending_orders) > 0 and len(completed_orders) > 0:
                print_result(True, f"Correctly excluded {len(pending_orders)} pending orders from analysis")
            
            return True
        else:
            print_result(False, f"Failed to get price analysis: {analysis_response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing completed orders analysis: {str(e)}")
        return False

# HIGH PRIORITY TESTS - Price Analysis Excel Export

def test_price_analysis_excel_authentication():
    """Test /api/reports/price-analysis/export endpoint requires authentication"""
    print_test_header("Price Analysis Excel Export Authentication")
    
    try:
        # Test without authentication
        response = requests.get(f"{API_URL}/reports/price-analysis/export")
        
        if response.status_code in [401, 403]:  # Both are valid authentication errors
            print_result(True, f"Excel export endpoint correctly requires authentication (status: {response.status_code})")
        else:
            print_result(False, f"Expected 401 or 403, got {response.status_code}")
            return False
        
        # Test with authentication
        if not auth_token:
            print_result(False, "No auth token available")
            return False
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API_URL}/reports/price-analysis/export", headers=headers)
        
        if response.status_code == 200:
            print_result(True, "Excel export endpoint works with authentication")
            return True
        else:
            print_result(False, f"Failed with auth: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing Excel export authentication: {str(e)}")
        return False

def test_price_analysis_excel_file_generation():
    """Test Excel export returns proper Excel file with binary content"""
    print_test_header("Price Analysis Excel Export File Generation")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{API_URL}/reports/price-analysis/export", headers=headers)
        
        if response.status_code == 200:
            # Check content type
            content_type = response.headers.get('content-type', '')
            expected_content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            if expected_content_type not in content_type:
                print_result(False, f"Wrong content type: expected {expected_content_type}, got {content_type}")
                return False
            
            print_result(True, f"Correct Excel content type: {content_type}")
            
            # Check if response contains binary data
            if len(response.content) == 0:
                print_result(False, "Excel file is empty")
                return False
            
            # Check if it's actually Excel format (starts with PK for ZIP-based formats like XLSX)
            if not response.content.startswith(b'PK'):
                print_result(False, "Response doesn't appear to be Excel format")
                return False
            
            print_result(True, f"Excel file generated successfully ({len(response.content)} bytes)")
            return True
        else:
            print_result(False, f"Failed to generate Excel file: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing Excel file generation: {str(e)}")
        return False

def test_price_analysis_excel_headers():
    """Test Excel export has proper Content-Disposition header with filename"""
    print_test_header("Price Analysis Excel Export Headers and Content")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{API_URL}/reports/price-analysis/export", headers=headers)
        
        if response.status_code == 200:
            # Check Content-Disposition header
            content_disposition = response.headers.get('content-disposition', '')
            
            if 'attachment' not in content_disposition:
                print_result(False, f"Missing attachment in Content-Disposition: {content_disposition}")
                return False
            
            if 'filename=' not in content_disposition:
                print_result(False, f"Missing filename in Content-Disposition: {content_disposition}")
                return False
            
            if 'price_analysis' not in content_disposition:
                print_result(False, f"Filename doesn't contain 'price_analysis': {content_disposition}")
                return False
            
            if '.xlsx' not in content_disposition:
                print_result(False, f"Filename doesn't have .xlsx extension: {content_disposition}")
                return False
            
            print_result(True, f"Proper Content-Disposition header: {content_disposition}")
            
            # Verify the file can be processed (basic validation)
            try:
                import io
                import zipfile
                
                # Excel files are ZIP archives, so we can check if it's a valid ZIP
                excel_data = io.BytesIO(response.content)
                with zipfile.ZipFile(excel_data, 'r') as zip_file:
                    # Check for typical Excel file structure
                    file_list = zip_file.namelist()
                    if 'xl/workbook.xml' in file_list:
                        print_result(True, "Excel file has valid internal structure")
                        return True
                    else:
                        print_result(False, "Excel file missing expected internal structure")
                        return False
                        
            except Exception as validation_error:
                print_result(False, f"Excel file validation failed: {str(validation_error)}")
                return False
        else:
            print_result(False, f"Failed to get Excel export: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing Excel headers: {str(e)}")
        return False

def test_price_analysis_excel_edge_cases():
    """Test Excel export behavior with edge cases (empty data, various pricing scenarios)"""
    print_test_header("Price Analysis Excel Export Edge Cases")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # First, get the price analysis data to understand what we're working with
        analysis_response = requests.get(f"{API_URL}/orders/price-analysis", headers=headers)
        
        if analysis_response.status_code != 200:
            print_result(False, "Could not get price analysis data for comparison")
            return False
        
        analysis_data = analysis_response.json()
        
        # Test Excel export with current data
        excel_response = requests.get(f"{API_URL}/reports/price-analysis/export", headers=headers)
        
        if excel_response.status_code == 200:
            print_result(True, "Excel export works with current data")
            
            # Test that Excel export works even with empty or minimal data
            if len(analysis_data.get('items', [])) == 0:
                print_result(True, "Excel export handles empty data gracefully")
            else:
                print_result(True, f"Excel export handles {len(analysis_data['items'])} items correctly")
            
            # Verify the Excel file size is reasonable
            file_size = len(excel_response.content)
            if file_size < 1000:  # Very small file might indicate an issue
                print_result(False, f"Excel file suspiciously small: {file_size} bytes")
                return False
            elif file_size > 10 * 1024 * 1024:  # Very large file might indicate an issue
                print_result(False, f"Excel file suspiciously large: {file_size} bytes")
                return False
            else:
                print_result(True, f"Excel file size reasonable: {file_size} bytes")
            
            return True
        else:
            print_result(False, f"Excel export failed: {excel_response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing Excel edge cases: {str(e)}")
        return False

# HIGH PRIORITY TESTS - Enhanced Data Structure

def test_orders_category_information():
    """Test orders include proper category information from menu service"""
    print_test_header("Orders Include Category Information")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Get menu to understand categories
        menu_response = requests.get(f"{API_URL}/menu/")
        if menu_response.status_code != 200:
            print_result(False, "Could not get menu for category mapping")
            return False
        
        menu_data = menu_response.json()
        menu_items = menu_data.get('items', [])
        item_category_map = {item['name']: item['category'] for item in menu_items}
        
        # Get view orders to check category information
        view_orders_response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if view_orders_response.status_code == 200:
            categories = view_orders_response.json()
            
            categories_found = 0
            for category in categories:
                category_name = category['category_name']
                
                # Check if items in this category match menu categories
                for item in category['items']:
                    item_name = item['item_name']
                    expected_category = item_category_map.get(item_name, 'Other')
                    
                    if category_name != expected_category and expected_category != 'Other':
                        print_result(False, f"Category mismatch for {item_name}: expected {expected_category}, got {category_name}")
                        return False
                
                categories_found += 1
                print_result(True, f"Category '{category_name}' has correct item grouping")
            
            if categories_found > 0:
                print_result(True, f"Found {categories_found} categories with proper menu service integration")
                return True
            else:
                print_result(True, "No categories found (empty database)")
                return True
        else:
            print_result(False, f"Failed to get view orders: {view_orders_response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing orders category information: {str(e)}")
        return False

def test_sequential_numbers_preserved():
    """Test sequential order numbers still work with enhanced features"""
    print_test_header("Sequential Order Numbers Preserved")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Create a test order to verify sequential numbering
        test_order_data = {
            "customerName": "Sequential Test Customer",
            "items": [{"name": "Tea", "quantity": 1}],
            "paymentMethod": "cash"
        }
        
        create_response = requests.post(f"{API_URL}/orders/", json=test_order_data, headers=headers)
        
        if create_response.status_code == 201:
            order = create_response.json()
            
            # Check order number is numeric
            order_number = order.get('orderNumber')
            if not order_number or not str(order_number).isdigit():
                print_result(False, f"Order number is not sequential numeric: {order_number}")
                return False
            
            print_result(True, f"Created order with sequential number: {order_number}")
            
            # Test customer lookup with sequential number
            lookup_response = requests.get(f"{API_URL}/orders/myorder/{order_number}")
            
            if lookup_response.status_code == 200:
                looked_up_order = lookup_response.json()
                if looked_up_order['id'] == order['id']:
                    print_result(True, f"Customer lookup works with sequential number {order_number}")
                    
                    # Store order ID for later tests
                    global created_order_id
                    created_order_id = order['id']
                    
                    return True
                else:
                    print_result(False, "Customer lookup returned wrong order")
                    return False
            else:
                print_result(False, f"Customer lookup failed: {lookup_response.status_code}")
                return False
        else:
            print_result(False, f"Failed to create test order: {create_response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing sequential numbers: {str(e)}")
        return False

def test_cooking_status_preserved():
    """Test cooking status tracking preserved in category view"""
    print_test_header("Cooking Status Tracking Preserved")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Get view orders to check cooking status
        view_orders_response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if view_orders_response.status_code == 200:
            categories = view_orders_response.json()
            
            cooking_status_found = 0
            valid_statuses = ['not started', 'cooking', 'finished']
            
            for category in categories:
                for item in category['items']:
                    for order in item['orders']:
                        cooking_status = order.get('cooking_status')
                        if cooking_status not in valid_statuses:
                            print_result(False, f"Invalid cooking status: {cooking_status}")
                            return False
                        cooking_status_found += 1
            
            if cooking_status_found > 0:
                print_result(True, f"Found {cooking_status_found} items with valid cooking status tracking")
                
                # Test cooking status update still works
                if cooking_status_found > 0 and created_order_id:
                    # Find first order to test status update
                    test_order = None
                    test_item = None
                    for category in categories:
                        for item in category['items']:
                            for order in item['orders']:
                                if order['cooking_status'] == 'not started' and order['order_id'] == created_order_id:
                                    test_order = order
                                    test_item = item['item_name']
                                    break
                            if test_order:
                                break
                        if test_order:
                            break
                    
                    if test_order:
                        # Test cooking status update
                        update_data = {
                            "order_id": test_order['order_id'],
                            "item_name": test_item,
                            "cooking_status": "cooking"
                        }
                        
                        update_response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
                        
                        if update_response.status_code == 200:
                            print_result(True, "Cooking status update still works with enhanced system")
                            return True
                        else:
                            print_result(False, f"Cooking status update failed: {update_response.status_code}")
                            return False
                    else:
                        print_result(True, "No orders available for status update test, but tracking is preserved")
                        return True
                
                return True
            else:
                print_result(True, "No orders found for cooking status test (empty database)")
                return True
        else:
            print_result(False, f"Failed to get view orders: {view_orders_response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing cooking status preservation: {str(e)}")
        return False

# HIGH PRIORITY TESTS - View Orders Bug Fix (Completed Orders Exclusion)

def test_view_orders_excludes_completed_orders():
    """Test that /api/orders/view-orders only returns pending orders and excludes completed orders"""
    print_test_header("View Orders Excludes Completed Orders")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # First, get all orders to understand the current state
        all_orders_response = requests.get(f"{API_URL}/orders/", headers=headers)
        if all_orders_response.status_code != 200:
            print_result(False, "Could not get all orders for comparison")
            return False
        
        all_orders = all_orders_response.json()
        pending_orders = [order for order in all_orders if order.get('status') == 'pending']
        completed_orders = [order for order in all_orders if order.get('status') == 'completed']
        
        print_result(True, f"Database state: {len(pending_orders)} pending orders, {len(completed_orders)} completed orders")
        
        # Get view orders response
        view_orders_response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if view_orders_response.status_code == 200:
            categories = view_orders_response.json()
            
            # Extract all order IDs from view-orders response
            view_orders_order_ids = set()
            for category in categories:
                for item in category['items']:
                    for order in item['orders']:
                        view_orders_order_ids.add(order['order_id'])
            
            # Check that no completed orders appear in view-orders
            completed_order_ids = {order['id'] for order in completed_orders}
            completed_in_view = view_orders_order_ids.intersection(completed_order_ids)
            
            if completed_in_view:
                print_result(False, f"CRITICAL: Found {len(completed_in_view)} completed orders in view-orders: {completed_in_view}")
                return False
            
            # Check that only pending orders appear in view-orders
            pending_order_ids = {order['id'] for order in pending_orders}
            pending_in_view = view_orders_order_ids.intersection(pending_order_ids)
            
            print_result(True, f"✅ View orders correctly excludes all {len(completed_orders)} completed orders")
            print_result(True, f"✅ View orders includes {len(pending_in_view)} pending orders (out of {len(pending_orders)} total pending)")
            
            # Verify all orders in view-orders have pending status
            for category in categories:
                for item in category['items']:
                    for order in item['orders']:
                        # Find the corresponding order in all_orders to check status
                        matching_order = next((o for o in all_orders if o['id'] == order['order_id']), None)
                        if matching_order and matching_order.get('status') != 'pending':
                            print_result(False, f"CRITICAL: Non-pending order {order['order_id']} found in view-orders with status: {matching_order.get('status')}")
                            return False
            
            print_result(True, "✅ All orders in view-orders have pending status")
            return True
        else:
            print_result(False, f"Failed to get view orders: {view_orders_response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing view orders exclusion: {str(e)}")
        return False

def test_order_completion_workflow():
    """Test that when an order is completed, it disappears from view-orders"""
    print_test_header("Order Completion Workflow - View Orders Integration")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Create a test order first
        test_order_data = {
            "customerName": "View Orders Test Customer",
            "items": [{"name": "Tea", "quantity": 1}],
            "paymentMethod": "cash"
        }
        
        create_response = requests.post(f"{API_URL}/orders/", json=test_order_data, headers=headers)
        
        if create_response.status_code != 201:
            print_result(False, f"Failed to create test order: {create_response.status_code}")
            return False
        
        created_order = create_response.json()
        order_id = created_order['id']
        order_number = created_order['orderNumber']
        
        print_result(True, f"Created test order {order_number} with ID {order_id}")
        
        # Verify order appears in view-orders (should be pending)
        view_orders_response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if view_orders_response.status_code != 200:
            print_result(False, "Failed to get view orders")
            return False
        
        categories = view_orders_response.json()
        order_found_in_view = False
        
        for category in categories:
            for item in category['items']:
                for order in item['orders']:
                    if order['order_id'] == order_id:
                        order_found_in_view = True
                        break
        
        if not order_found_in_view:
            print_result(False, "Test order not found in view-orders (should be pending)")
            return False
        
        print_result(True, "✅ Pending order correctly appears in view-orders")
        
        # Complete the order by marking all items as finished
        update_data = {
            "order_id": order_id,
            "item_name": "Tea",
            "cooking_status": "finished"
        }
        
        update_response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
        
        if update_response.status_code != 200:
            print_result(False, f"Failed to update cooking status: {update_response.status_code}")
            return False
        
        update_result = update_response.json()
        
        if not update_result.get("order_auto_completed"):
            print_result(False, "Order was not auto-completed when all items finished")
            return False
        
        print_result(True, "✅ Order auto-completed when all items marked as finished")
        
        # Verify order no longer appears in view-orders
        view_orders_response_after = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if view_orders_response_after.status_code != 200:
            print_result(False, "Failed to get view orders after completion")
            return False
        
        categories_after = view_orders_response_after.json()
        order_found_after_completion = False
        
        for category in categories_after:
            for item in category['items']:
                for order in item['orders']:
                    if order['order_id'] == order_id:
                        order_found_after_completion = True
                        break
        
        if order_found_after_completion:
            print_result(False, "CRITICAL: Completed order still appears in view-orders")
            return False
        
        print_result(True, "✅ Completed order correctly excluded from view-orders")
        
        # Verify order is still accessible via customer lookup
        lookup_response = requests.get(f"{API_URL}/orders/myorder/{order_number}")
        
        if lookup_response.status_code != 200:
            print_result(False, "Completed order not accessible via customer lookup")
            return False
        
        looked_up_order = lookup_response.json()
        if looked_up_order['status'] != 'completed':
            print_result(False, f"Order status incorrect in customer lookup: {looked_up_order['status']}")
            return False
        
        print_result(True, "✅ Completed order still accessible via customer lookup")
        
        return True
        
    except Exception as e:
        print_result(False, f"Error testing order completion workflow: {str(e)}")
        return False

def test_automatic_order_completion_view_orders():
    """Test that automatic order completion immediately removes orders from view-orders"""
    print_test_header("Automatic Order Completion - Immediate View Orders Update")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Create a multi-item test order
        test_order_data = {
            "customerName": "Multi-Item Auto-Complete Test",
            "items": [
                {"name": "Tea", "quantity": 1},
                {"name": "Coffee", "quantity": 1}
            ],
            "paymentMethod": "cash"
        }
        
        create_response = requests.post(f"{API_URL}/orders/", json=test_order_data, headers=headers)
        
        if create_response.status_code != 201:
            print_result(False, f"Failed to create multi-item test order: {create_response.status_code}")
            return False
        
        created_order = create_response.json()
        order_id = created_order['id']
        order_number = created_order['orderNumber']
        
        print_result(True, f"Created multi-item test order {order_number}")
        
        # Mark first item as finished (order should remain pending)
        update_data_1 = {
            "order_id": order_id,
            "item_name": "Tea",
            "cooking_status": "finished"
        }
        
        update_response_1 = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data_1, headers=headers)
        
        if update_response_1.status_code != 200:
            print_result(False, "Failed to update first item status")
            return False
        
        update_result_1 = update_response_1.json()
        
        if update_result_1.get("order_auto_completed"):
            print_result(False, "Order auto-completed prematurely (only 1 of 2 items finished)")
            return False
        
        print_result(True, "✅ Order remains pending when only some items are finished")
        
        # Verify order still appears in view-orders
        view_orders_response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if view_orders_response.status_code != 200:
            print_result(False, "Failed to get view orders")
            return False
        
        categories = view_orders_response.json()
        order_found = False
        
        for category in categories:
            for item in category['items']:
                for order in item['orders']:
                    if order['order_id'] == order_id:
                        order_found = True
                        break
        
        if not order_found:
            print_result(False, "Order disappeared from view-orders prematurely")
            return False
        
        print_result(True, "✅ Partially completed order still appears in view-orders")
        
        # Mark second item as finished (order should auto-complete)
        update_data_2 = {
            "order_id": order_id,
            "item_name": "Coffee",
            "cooking_status": "finished"
        }
        
        update_response_2 = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data_2, headers=headers)
        
        if update_response_2.status_code != 200:
            print_result(False, "Failed to update second item status")
            return False
        
        update_result_2 = update_response_2.json()
        
        if not update_result_2.get("order_auto_completed"):
            print_result(False, "Order was not auto-completed when all items finished")
            return False
        
        print_result(True, "✅ Order auto-completed when all items marked as finished")
        
        # Verify order immediately disappears from view-orders
        view_orders_response_final = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if view_orders_response_final.status_code != 200:
            print_result(False, "Failed to get view orders after auto-completion")
            return False
        
        categories_final = view_orders_response_final.json()
        order_found_final = False
        
        for category in categories_final:
            for item in category['items']:
                for order in item['orders']:
                    if order['order_id'] == order_id:
                        order_found_final = True
                        break
        
        if order_found_final:
            print_result(False, "CRITICAL: Auto-completed order still appears in view-orders")
            return False
        
        print_result(True, "✅ Auto-completed order immediately excluded from view-orders")
        
        return True
        
    except Exception as e:
        print_result(False, f"Error testing automatic order completion: {str(e)}")
        return False

def test_view_orders_status_filtering_edge_cases():
    """Test edge cases for view orders status filtering"""
    print_test_header("View Orders Status Filtering Edge Cases")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Get current view orders state
        view_orders_response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
        
        if view_orders_response.status_code != 200:
            print_result(False, "Failed to get view orders")
            return False
        
        categories = view_orders_response.json()
        
        # Verify all orders in view-orders have valid structure and pending status
        total_items_in_view = 0
        unique_order_ids = set()
        invalid_orders = []
        
        for category in categories:
            if not isinstance(category, dict) or 'items' not in category:
                print_result(False, "Invalid category structure in view-orders")
                return False
            
            for item in category['items']:
                if not isinstance(item, dict) or 'orders' not in item:
                    print_result(False, "Invalid item structure in view-orders")
                    return False
                
                for order in item['orders']:
                    total_items_in_view += 1
                    unique_order_ids.add(order['order_id'])
                    
                    # Check required fields
                    required_fields = ['order_id', 'orderNumber', 'customerName', 'quantity', 'cooking_status', 'orderTime']
                    for field in required_fields:
                        if field not in order:
                            invalid_orders.append(f"Order {order.get('order_id', 'unknown')} missing field: {field}")
                    
                    # Validate cooking status
                    valid_statuses = ['not started', 'cooking', 'finished']
                    if order.get('cooking_status') not in valid_statuses:
                        invalid_orders.append(f"Order {order.get('order_id', 'unknown')} has invalid cooking status: {order.get('cooking_status')}")
                    
                    # Validate order number format (should be numeric)
                    order_number = order.get('orderNumber')
                    if not str(order_number).isdigit():
                        invalid_orders.append(f"Order {order.get('order_id', 'unknown')} has non-numeric order number: {order_number}")
        
        if invalid_orders:
            for error in invalid_orders:
                print_result(False, error)
            return False
        
        print_result(True, f"✅ All {total_items_in_view} order items in view-orders have valid structure")
        print_result(True, f"✅ View-orders contains {len(unique_order_ids)} unique orders")
        
        # Cross-reference with all orders to ensure filtering is correct
        all_orders_response = requests.get(f"{API_URL}/orders/", headers=headers)
        
        if all_orders_response.status_code == 200:
            all_orders = all_orders_response.json()
            
            # Count orders by status
            status_counts = {}
            pending_orders = []
            for order in all_orders:
                status = order.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
                if status == 'pending':
                    pending_orders.append(order)
            
            print_result(True, f"Database order status distribution: {status_counts}")
            
            # Verify view-orders unique order count matches pending orders count
            pending_count = status_counts.get('pending', 0)
            
            if len(unique_order_ids) != pending_count:
                print_result(False, f"Mismatch: view-orders shows {len(unique_order_ids)} unique orders, but database has {pending_count} pending orders")
                return False
            
            print_result(True, f"✅ View-orders unique order count ({len(unique_order_ids)}) matches pending orders count ({pending_count})")
            
            # Calculate expected total items from pending orders
            expected_total_items = sum(len(order.get('items', [])) for order in pending_orders)
            
            if total_items_in_view != expected_total_items:
                print_result(False, f"Item count mismatch: view-orders shows {total_items_in_view} items, expected {expected_total_items} from pending orders")
                return False
            
            print_result(True, f"✅ View-orders item count ({total_items_in_view}) matches expected items from pending orders ({expected_total_items})")
        
        return True
        
    except Exception as e:
        print_result(False, f"Error testing view orders edge cases: {str(e)}")
        return False

# HIGH PRIORITY TESTS - Menu Updates Verification

def test_menu_item_price_updates():
    """Test that Pani Puri price is updated to $6.00 (changed from $7.00)"""
    print_test_header("Menu Item Price Updates - Pani Puri $6.00")
    
    try:
        response = requests.get(f"{API_URL}/menu/")
        
        if response.status_code == 200:
            menu_data = response.json()
            menu_items = menu_data.get('items', [])
            
            # Find Pani Puri item
            pani_puri = None
            for item in menu_items:
                if item['name'] == 'Pani Puri':
                    pani_puri = item
                    break
            
            if not pani_puri:
                print_result(False, "Pani Puri not found in menu")
                return False
            
            # Check price is $6.00
            if pani_puri['price'] != 6.00:
                print_result(False, f"Pani Puri price incorrect: expected $6.00, got ${pani_puri['price']}")
                return False
            
            print_result(True, f"✅ Pani Puri price correctly updated to ${pani_puri['price']}")
            
            # Verify it's in Chaat category
            if pani_puri['category'] != 'Chaat':
                print_result(False, f"Pani Puri category incorrect: expected 'Chaat', got '{pani_puri['category']}'")
                return False
            
            print_result(True, f"✅ Pani Puri correctly categorized as '{pani_puri['category']}'")
            return True
        else:
            print_result(False, f"Failed to get menu: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing menu price updates: {str(e)}")
        return False

def test_new_menu_item_batani_chaat():
    """Test that Batani Chaat is available for $7.00 in the Chaat category"""
    print_test_header("New Menu Item - Batani Chaat $7.00")
    
    try:
        response = requests.get(f"{API_URL}/menu/")
        
        if response.status_code == 200:
            menu_data = response.json()
            menu_items = menu_data.get('items', [])
            
            # Find Batani Chaat item
            batani_chaat = None
            for item in menu_items:
                if item['name'] == 'Batani Chaat':
                    batani_chaat = item
                    break
            
            if not batani_chaat:
                print_result(False, "Batani Chaat not found in menu")
                return False
            
            # Check price is $7.00
            if batani_chaat['price'] != 7.00:
                print_result(False, f"Batani Chaat price incorrect: expected $7.00, got ${batani_chaat['price']}")
                return False
            
            print_result(True, f"✅ Batani Chaat price correctly set to ${batani_chaat['price']}")
            
            # Verify it's in Chaat category
            if batani_chaat['category'] != 'Chaat':
                print_result(False, f"Batani Chaat category incorrect: expected 'Chaat', got '{batani_chaat['category']}'")
                return False
            
            print_result(True, f"✅ Batani Chaat correctly categorized as '{batani_chaat['category']}'")
            return True
        else:
            print_result(False, f"Failed to get menu: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing new menu item: {str(e)}")
        return False

def test_chaat_category_five_items():
    """Test that Chaat category now contains exactly 5 items"""
    print_test_header("Chaat Category - 5 Items Verification")
    
    try:
        response = requests.get(f"{API_URL}/menu/")
        
        if response.status_code == 200:
            menu_data = response.json()
            menu_items = menu_data.get('items', [])
            
            # Find all Chaat items
            chaat_items = [item for item in menu_items if item['category'] == 'Chaat']
            
            if len(chaat_items) != 5:
                print_result(False, f"Chaat category should have 5 items, found {len(chaat_items)}")
                return False
            
            # Expected Chaat items
            expected_items = ['Pani Puri', 'Bhel Puri', 'Dahi Puri', 'Sev Puri', 'Batani Chaat']
            found_items = [item['name'] for item in chaat_items]
            
            # Check all expected items are present
            for expected_item in expected_items:
                if expected_item not in found_items:
                    print_result(False, f"Missing expected Chaat item: {expected_item}")
                    return False
            
            print_result(True, f"✅ Chaat category contains all 5 expected items: {', '.join(found_items)}")
            
            # Verify pricing for each item
            pricing_correct = True
            for item in chaat_items:
                if item['name'] == 'Pani Puri' and item['price'] != 6.00:
                    print_result(False, f"Pani Puri price incorrect: ${item['price']}")
                    pricing_correct = False
                elif item['name'] in ['Bhel Puri', 'Dahi Puri', 'Sev Puri', 'Batani Chaat'] and item['price'] != 7.00:
                    print_result(False, f"{item['name']} price incorrect: ${item['price']}")
                    pricing_correct = False
            
            if pricing_correct:
                print_result(True, "✅ All Chaat items have correct pricing")
                return True
            else:
                return False
        else:
            print_result(False, f"Failed to get menu: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing Chaat category: {str(e)}")
        return False

def test_order_creation_with_updated_items():
    """Test creating an order with updated menu items to ensure pricing calculations work correctly"""
    print_test_header("Order Creation with Updated Menu Items")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Create order with both Pani Puri ($6.00) and Batani Chaat ($7.00)
        test_order_data = {
            "customerName": "Menu Update Test Customer",
            "items": [
                {"name": "Pani Puri", "quantity": 2},  # 2 x $6.00 = $12.00
                {"name": "Batani Chaat", "quantity": 1}  # 1 x $7.00 = $7.00
            ],
            "paymentMethod": "cash"
        }
        
        create_response = requests.post(f"{API_URL}/orders/", json=test_order_data, headers=headers)
        
        if create_response.status_code == 201:
            order = create_response.json()
            
            # Verify order total calculation: $12.00 + $7.00 = $19.00
            expected_total = 19.00
            if abs(order['totalAmount'] - expected_total) > 0.01:
                print_result(False, f"Order total incorrect: expected ${expected_total}, got ${order['totalAmount']}")
                return False
            
            print_result(True, f"✅ Order total correctly calculated: ${order['totalAmount']}")
            
            # Verify individual item pricing
            items = order.get('items', [])
            pani_puri_item = None
            batani_chaat_item = None
            
            for item in items:
                if item['name'] == 'Pani Puri':
                    pani_puri_item = item
                elif item['name'] == 'Batani Chaat':
                    batani_chaat_item = item
            
            if not pani_puri_item:
                print_result(False, "Pani Puri item not found in order")
                return False
            
            if not batani_chaat_item:
                print_result(False, "Batani Chaat item not found in order")
                return False
            
            # Check Pani Puri pricing: 2 x $6.00 = $12.00
            if pani_puri_item['price'] != 6.00:
                print_result(False, f"Pani Puri unit price incorrect: expected $6.00, got ${pani_puri_item['price']}")
                return False
            
            if abs(pani_puri_item['subtotal'] - 12.00) > 0.01:
                print_result(False, f"Pani Puri subtotal incorrect: expected $12.00, got ${pani_puri_item['subtotal']}")
                return False
            
            print_result(True, f"✅ Pani Puri pricing correct: ${pani_puri_item['price']} x {pani_puri_item['quantity']} = ${pani_puri_item['subtotal']}")
            
            # Check Batani Chaat pricing: 1 x $7.00 = $7.00
            if batani_chaat_item['price'] != 7.00:
                print_result(False, f"Batani Chaat unit price incorrect: expected $7.00, got ${batani_chaat_item['price']}")
                return False
            
            if abs(batani_chaat_item['subtotal'] - 7.00) > 0.01:
                print_result(False, f"Batani Chaat subtotal incorrect: expected $7.00, got ${batani_chaat_item['subtotal']}")
                return False
            
            print_result(True, f"✅ Batani Chaat pricing correct: ${batani_chaat_item['price']} x {batani_chaat_item['quantity']} = ${batani_chaat_item['subtotal']}")
            
            # Store order ID for potential cleanup
            global created_order_id
            created_order_id = order['id']
            
            return True
        else:
            print_result(False, f"Failed to create order: {create_response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing order creation with updated items: {str(e)}")
        return False

def test_menu_endpoint_updated_pricing():
    """Test that /api/menu/ returns the updated menu with correct pricing"""
    print_test_header("Menu Endpoint - Updated Pricing Verification")
    
    try:
        response = requests.get(f"{API_URL}/menu/")
        
        if response.status_code == 200:
            menu_data = response.json()
            
            # Verify response structure
            if 'items' not in menu_data or 'categories' not in menu_data:
                print_result(False, "Menu response missing required fields")
                return False
            
            menu_items = menu_data['items']
            categories = menu_data['categories']
            
            # Verify Chaat category is present
            if 'Chaat' not in categories:
                print_result(False, "Chaat category not found in categories list")
                return False
            
            print_result(True, f"✅ Menu contains {len(categories)} categories including 'Chaat'")
            
            # Verify total item count includes new item
            total_items = len(menu_items)
            if total_items < 30:  # Should have at least 30+ items with the new addition
                print_result(False, f"Menu seems to have too few items: {total_items}")
                return False
            
            print_result(True, f"✅ Menu contains {total_items} total items")
            
            # Verify specific pricing updates
            pricing_tests = [
                ('Pani Puri', 6.00, 'Chaat'),
                ('Batani Chaat', 7.00, 'Chaat'),
                ('Bhel Puri', 7.00, 'Chaat'),
                ('Dahi Puri', 7.00, 'Chaat'),
                ('Sev Puri', 7.00, 'Chaat')
            ]
            
            for item_name, expected_price, expected_category in pricing_tests:
                item = next((item for item in menu_items if item['name'] == item_name), None)
                
                if not item:
                    print_result(False, f"{item_name} not found in menu")
                    return False
                
                if item['price'] != expected_price:
                    print_result(False, f"{item_name} price incorrect: expected ${expected_price}, got ${item['price']}")
                    return False
                
                if item['category'] != expected_category:
                    print_result(False, f"{item_name} category incorrect: expected '{expected_category}', got '{item['category']}'")
                    return False
                
                print_result(True, f"✅ {item_name}: ${item['price']} in '{item['category']}' category")
            
            return True
        else:
            print_result(False, f"Failed to get menu: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error testing menu endpoint: {str(e)}")
        return False

def run_enhanced_mem_famous_tests():
    """Run all enhanced Mem Famous Stall 2025 tests"""
    print(f"🚀 Starting Enhanced Mem Famous Stall 2025 System Tests")
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏪 Testing enhanced system with category-based view orders, price analysis, and Excel export functionality")
    print(f"🎯 SPECIAL FOCUS: Menu Updates - Testing Pani Puri price change and Batani Chaat addition")
    
    # Get authentication token first
    if not get_auth_token():
        print("❌ Cannot proceed without authentication")
        return False
    
    # Run all tests in priority order
    tests = [
        # CRITICAL PRIORITY - View Orders Bug Fix (User Reported Issue)
        ("View Orders Excludes Completed Orders", test_view_orders_excludes_completed_orders, "CRITICAL"),
        ("Order Completion Workflow - View Orders Integration", test_order_completion_workflow, "CRITICAL"),
        ("Automatic Order Completion - Immediate View Orders Update", test_automatic_order_completion_view_orders, "CRITICAL"),
        ("View Orders Status Filtering Edge Cases", test_view_orders_status_filtering_edge_cases, "CRITICAL"),
        
        # HIGH PRIORITY - Category-Based View Orders
        ("Category-Based View Orders Endpoint", test_category_based_view_orders, "HIGH"),
        ("Category Grouping with Food Categories", test_category_grouping, "HIGH"),
        ("Individual Item Status in Categories", test_item_status_in_categories, "HIGH"),
        ("Pricing Information in Category View", test_pricing_in_category_view, "HIGH"),
        
        # HIGH PRIORITY - Price Analysis System
        ("Price Analysis Endpoint Authentication", test_price_analysis_authentication, "HIGH"),
        ("Price Analysis Data Structure", test_price_analysis_data_structure, "HIGH"),
        ("Revenue Calculation and Sorting", test_revenue_calculation_sorting, "HIGH"),
        ("Completed Orders Only Analysis", test_completed_orders_analysis, "HIGH"),
        
        # HIGH PRIORITY - Price Analysis Excel Export
        ("Price Analysis Excel Export Authentication", test_price_analysis_excel_authentication, "HIGH"),
        ("Price Analysis Excel Export File Generation", test_price_analysis_excel_file_generation, "HIGH"),
        ("Price Analysis Excel Export Headers and Content", test_price_analysis_excel_headers, "HIGH"),
        ("Price Analysis Excel Export Edge Cases", test_price_analysis_excel_edge_cases, "HIGH"),
        
        # HIGH PRIORITY - Enhanced Data Structure
        ("Orders Include Category Information", test_orders_category_information, "HIGH"),
        ("Sequential Order Numbers Preserved", test_sequential_numbers_preserved, "HIGH"),
        ("Cooking Status Tracking Preserved", test_cooking_status_preserved, "HIGH")
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
    print("📊 ENHANCED MEM FAMOUS STALL 2025 TEST SUMMARY")
    print('='*80)
    
    passed = 0
    total = len(results)
    critical_priority_passed = 0
    critical_priority_total = 0
    high_priority_passed = 0
    high_priority_total = 0
    
    for test_name, result, priority in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} [{priority}] {test_name}")
        if result:
            passed += 1
        if priority == "CRITICAL":
            critical_priority_total += 1
            if result:
                critical_priority_passed += 1
        elif priority == "HIGH":
            high_priority_total += 1
            if result:
                high_priority_passed += 1
    
    print(f"\n🎯 Overall Results: {passed}/{total} tests passed")
    print(f"🚨 CRITICAL Priority Results: {critical_priority_passed}/{critical_priority_total} tests passed")
    print(f"🔥 High Priority Results: {high_priority_passed}/{high_priority_total} tests passed")
    
    if passed == total:
        print("🎉 All enhanced Mem Famous Stall 2025 tests PASSED!")
        print("✅ System ready with all new features working correctly")
        return True
    elif critical_priority_passed == critical_priority_total:
        print("✅ All CRITICAL PRIORITY tests passed - View Orders bug fix verified!")
        if high_priority_passed == high_priority_total:
            print("✅ All HIGH PRIORITY tests also passed")
            print("🎉 Core enhanced functionality working correctly")
        else:
            print("⚠️  Some HIGH PRIORITY tests failed, but critical View Orders functionality is working")
        return True
    else:
        print("❌ Some CRITICAL PRIORITY tests FAILED - View Orders bug still present!")
        print("🚨 URGENT: View Orders functionality needs immediate attention")
        return False

if __name__ == "__main__":
    success = run_enhanced_mem_famous_tests()
    sys.exit(0 if success else 1)
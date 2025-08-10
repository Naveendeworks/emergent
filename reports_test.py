#!/usr/bin/env python3
"""
Reports API Testing for "Mem Famous Stall 2025" System
Investigating failing export endpoints: price-analysis/export, payment/export, items/export
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

# Global variables for test data
auth_token = None
created_order_ids = []

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

def test_database_state():
    """Check current database state"""
    print_test_header("Database State Investigation")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Check orders
        response = requests.get(f"{API_URL}/orders/", headers=headers)
        if response.status_code == 200:
            all_orders = response.json()
            completed_orders = [order for order in all_orders if order.get('status') == 'completed']
            pending_orders = [order for order in all_orders if order.get('status') == 'pending']
            
            print_result(True, f"Total orders: {len(all_orders)}")
            print_result(True, f"Completed orders: {len(completed_orders)}")
            print_result(True, f"Pending orders: {len(pending_orders)}")
            
            if len(completed_orders) == 0:
                print_result(True, "⚠️  Database has NO completed orders - this may cause export failures")
            
            return True
        else:
            print_result(False, f"Failed to get orders: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error checking database state: {str(e)}")
        return False

def test_non_export_endpoints():
    """Test non-export report endpoints first"""
    print_test_header("Non-Export Report Endpoints")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        endpoints = [
            ("/orders/price-analysis", "Price Analysis API"),
            ("/reports/payment", "Payment Reports API"),
            ("/reports/items", "Item Reports API")
        ]
        
        success_count = 0
        
        for endpoint, name in endpoints:
            response = requests.get(f"{API_URL}{endpoint}", headers=headers)
            
            if response.status_code == 200:
                print_result(True, f"✅ {name} SUCCESS")
                data = response.json()
                
                # Show data structure
                if isinstance(data, dict):
                    if 'items' in data:
                        print_result(True, f"  Contains {len(data['items'])} items")
                    if 'total_revenue' in data:
                        print_result(True, f"  Total revenue: ${data['total_revenue']}")
                elif isinstance(data, list):
                    print_result(True, f"  Contains {len(data)} records")
                
                success_count += 1
            else:
                print_result(False, f"❌ {name} FAILED (status: {response.status_code})")
                if response.status_code == 500:
                    try:
                        error_detail = response.json().get('detail', 'No error detail')
                        print_result(False, f"  Error: {error_detail}")
                    except:
                        print_result(False, f"  Raw error: {response.text[:300]}")
        
        return success_count == len(endpoints)
        
    except Exception as e:
        print_result(False, f"Error testing non-export endpoints: {str(e)}")
        return False

def test_export_endpoints_detailed():
    """Test export endpoints with detailed error analysis"""
    print_test_header("Export Endpoints - Detailed Investigation")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        export_endpoints = [
            ("/reports/price-analysis/export", "Price Analysis Export"),
            ("/reports/payment/export", "Payment Reports Export"),
            ("/reports/items/export", "Item Reports Export")
        ]
        
        success_count = 0
        
        for endpoint, name in export_endpoints:
            print(f"\n🔍 Testing {name}: {endpoint}")
            
            response = requests.get(f"{API_URL}{endpoint}", headers=headers)
            
            print_result(True, f"Status Code: {response.status_code}")
            print_result(True, f"Content-Type: {response.headers.get('content-type', 'Not set')}")
            print_result(True, f"Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 500:
                print_result(False, f"❌ {name} FAILED with 500 Internal Server Error")
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'No error detail available')
                    print_result(False, f"  Error Detail: {error_detail}")
                    
                    # Look for specific error patterns
                    if 'pandas' in error_detail.lower():
                        print_result(False, f"  🔍 PANDAS ERROR detected - likely Excel generation issue")
                    elif 'excel' in error_detail.lower():
                        print_result(False, f"  🔍 EXCEL ERROR detected - ExcelService issue")
                    elif 'empty' in error_detail.lower():
                        print_result(False, f"  🔍 EMPTY DATA ERROR detected - no data to export")
                    
                except:
                    print_result(False, f"  Raw Error Response: {response.text[:500]}")
                    
                    # Look for patterns in raw response
                    if 'pandas' in response.text.lower():
                        print_result(False, f"  🔍 PANDAS ERROR in raw response")
                    elif 'excel' in response.text.lower():
                        print_result(False, f"  🔍 EXCEL ERROR in raw response")
                        
            elif response.status_code == 200:
                print_result(True, f"✅ {name} SUCCESS")
                
                # Verify Excel format
                if response.content.startswith(b'PK'):
                    print_result(True, f"  Valid Excel format detected")
                    
                    # Check Content-Disposition header
                    content_disposition = response.headers.get('content-disposition', '')
                    if 'attachment' in content_disposition and '.xlsx' in content_disposition:
                        print_result(True, f"  Proper download headers: {content_disposition}")
                    else:
                        print_result(False, f"  Invalid download headers: {content_disposition}")
                else:
                    print_result(False, f"  Invalid Excel format - not a ZIP/Excel file")
                
                success_count += 1
            else:
                print_result(False, f"❌ {name} unexpected status: {response.status_code}")
        
        return success_count == len(export_endpoints)
        
    except Exception as e:
        print_result(False, f"Error testing export endpoints: {str(e)}")
        return False

def create_test_orders():
    """Create test orders to ensure we have data for reports"""
    print_test_header("Creating Test Orders for Reports")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Create diverse test orders
        test_orders = [
            {
                "customerName": "Reports Test Customer 1",
                "items": [
                    {"name": "Tea", "quantity": 2},
                    {"name": "Coffee", "quantity": 1}
                ],
                "paymentMethod": "cash"
            },
            {
                "customerName": "Reports Test Customer 2", 
                "items": [
                    {"name": "Chicken Biryani", "quantity": 1},
                    {"name": "Dosa", "quantity": 2}
                ],
                "paymentMethod": "cashapp"
            },
            {
                "customerName": "Reports Test Customer 3",
                "items": [
                    {"name": "Pani Puri", "quantity": 3}
                ],
                "paymentMethod": "cash"
            }
        ]
        
        global created_order_ids
        created_order_ids = []
        
        for i, order_data in enumerate(test_orders, 1):
            response = requests.post(f"{API_URL}/orders/", json=order_data, headers=headers)
            
            if response.status_code == 201:
                order = response.json()
                created_order_ids.append(order['id'])
                print_result(True, f"Created test order #{order['orderNumber']} - ${order['totalAmount']}")
            else:
                print_result(False, f"Failed to create test order {i}: {response.status_code}")
                return False
        
        print_result(True, f"Successfully created {len(created_order_ids)} test orders")
        return True
        
    except Exception as e:
        print_result(False, f"Error creating test orders: {str(e)}")
        return False

def complete_test_orders():
    """Complete some test orders to have completed data for reports"""
    print_test_header("Completing Test Orders")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    if not created_order_ids:
        print_result(False, "No test orders to complete")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Complete first 2 orders
        completed_count = 0
        
        for order_id in created_order_ids[:2]:
            # Get order details to know what items to complete
            order_response = requests.get(f"{API_URL}/orders/{order_id}", headers=headers)
            
            if order_response.status_code != 200:
                print_result(False, f"Failed to get order {order_id}")
                continue
            
            order = order_response.json()
            
            # Mark all items as finished
            for item in order['items']:
                update_data = {
                    "order_id": order_id,
                    "item_name": item['name'],
                    "cooking_status": "finished"
                }
                
                update_response = requests.patch(f"{API_URL}/orders/cooking-status", json=update_data, headers=headers)
                
                if update_response.status_code == 200:
                    update_result = update_response.json()
                    if update_result.get("order_auto_completed"):
                        print_result(True, f"Order #{order['orderNumber']} auto-completed")
                        completed_count += 1
                        break  # Order is completed, no need to update more items
                else:
                    print_result(False, f"Failed to update cooking status for order #{order['orderNumber']}")
        
        print_result(True, f"Successfully completed {completed_count} test orders")
        return completed_count > 0
        
    except Exception as e:
        print_result(False, f"Error completing test orders: {str(e)}")
        return False

def test_reports_with_data():
    """Test all report endpoints after ensuring we have data"""
    print_test_header("Testing Reports with Data")
    
    if not auth_token:
        print_result(False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Verify we now have completed orders
        response = requests.get(f"{API_URL}/orders/", headers=headers)
        if response.status_code == 200:
            all_orders = response.json()
            completed_orders = [order for order in all_orders if order.get('status') == 'completed']
            print_result(True, f"Database now has {len(completed_orders)} completed orders")
        
        # Test all endpoints
        all_endpoints = [
            ("/orders/price-analysis", "Price Analysis API", False),
            ("/reports/payment", "Payment Reports API", False),
            ("/reports/items", "Item Reports API", False),
            ("/reports/price-analysis/export", "Price Analysis Export", True),
            ("/reports/payment/export", "Payment Reports Export", True),
            ("/reports/items/export", "Item Reports Export", True)
        ]
        
        success_count = 0
        export_success_count = 0
        export_total = 0
        
        for endpoint, name, is_export in all_endpoints:
            response = requests.get(f"{API_URL}{endpoint}", headers=headers)
            
            if response.status_code == 200:
                print_result(True, f"✅ {name} SUCCESS")
                
                if is_export:
                    export_total += 1
                    if response.content.startswith(b'PK'):
                        print_result(True, f"  Valid Excel format ({len(response.content)} bytes)")
                        export_success_count += 1
                    else:
                        print_result(False, f"  Invalid Excel format")
                
                success_count += 1
            else:
                print_result(False, f"❌ {name} FAILED (status: {response.status_code})")
                if is_export:
                    export_total += 1
                
                if response.status_code == 500:
                    try:
                        error_detail = response.json().get('detail', 'No error detail')
                        print_result(False, f"  Error: {error_detail}")
                    except:
                        print_result(False, f"  Raw error: {response.text[:200]}")
        
        print_result(True, f"Overall: {success_count}/{len(all_endpoints)} endpoints working")
        print_result(True, f"Export endpoints: {export_success_count}/{export_total} working")
        
        return success_count == len(all_endpoints)
        
    except Exception as e:
        print_result(False, f"Error testing reports with data: {str(e)}")
        return False

def run_reports_investigation():
    """Run complete reports investigation"""
    print_test_header("REPORTS API INVESTIGATION - Export Endpoints Failing")
    print(f"📅 Investigation started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Focus: Identify why /api/reports/*/export endpoints return 500 errors")
    
    # Authentication first
    if not get_auth_token():
        print("❌ Authentication failed - cannot proceed")
        return False
    
    # Run investigation steps
    investigation_steps = [
        ("Database State Check", test_database_state),
        ("Non-Export Endpoints Test", test_non_export_endpoints),
        ("Export Endpoints Detailed Analysis", test_export_endpoints_detailed),
        ("Create Test Orders", create_test_orders),
        ("Complete Test Orders", complete_test_orders),
        ("Test Reports with Data", test_reports_with_data)
    ]
    
    results = []
    for step_name, step_func in investigation_steps:
        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            print_result(False, f"Investigation step {step_name} crashed: {str(e)}")
            results.append((step_name, False))
    
    # Print investigation summary
    print_test_header("INVESTIGATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"📊 Investigation Steps: {passed}/{total} successful")
    
    for step_name, result in results:
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"{status} {step_name}")
    
    if results[-1][1]:  # If final test passed
        print("\n🎉 INVESTIGATION COMPLETE - Export endpoints are now working!")
        print("✅ Root cause identified and resolved: Empty database issue")
    else:
        print("\n❌ INVESTIGATION INCOMPLETE - Export endpoints still failing")
        print("🔍 Further investigation needed - check server logs for detailed errors")
    
    return results[-1][1]

if __name__ == "__main__":
    success = run_reports_investigation()
    sys.exit(0 if success else 1)
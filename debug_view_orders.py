#!/usr/bin/env python3
"""
Debug script to investigate View Orders filtering issue
"""

import requests
import json
import sys

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
API_URL = f"{BASE_URL}/api"

def get_auth_token():
    """Get authentication token"""
    try:
        response = requests.post(f"{API_URL}/auth/login", json={
            "username": "admin",
            "password": "memfamous2025"
        })
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Authentication failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return None

def debug_view_orders():
    """Debug the view orders functionality"""
    print("🔍 DEBUGGING VIEW ORDERS FUNCTIONALITY")
    print("="*60)
    
    auth_token = get_auth_token()
    if not auth_token:
        print("❌ Cannot proceed without authentication")
        return
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Get all orders
    print("\n1. Getting all orders from database...")
    all_orders_response = requests.get(f"{API_URL}/orders/", headers=headers)
    
    if all_orders_response.status_code != 200:
        print(f"❌ Failed to get all orders: {all_orders_response.status_code}")
        return
    
    all_orders = all_orders_response.json()
    
    # Analyze order statuses
    status_counts = {}
    pending_orders = []
    completed_orders = []
    
    for order in all_orders:
        status = order.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
        
        if status == 'pending':
            pending_orders.append(order)
        elif status == 'completed':
            completed_orders.append(order)
    
    print(f"📊 Database order status distribution: {status_counts}")
    print(f"📋 Pending orders: {len(pending_orders)}")
    print(f"✅ Completed orders: {len(completed_orders)}")
    
    # Show details of pending orders
    print(f"\n2. Details of {len(pending_orders)} pending orders:")
    for i, order in enumerate(pending_orders, 1):
        print(f"   {i}. Order #{order.get('orderNumber')} - {order.get('customerName')} - Status: {order.get('status')}")
        print(f"      ID: {order.get('id')}")
        print(f"      Items: {[item.get('name') for item in order.get('items', [])]}")
    
    # Get view orders
    print(f"\n3. Getting view orders response...")
    view_orders_response = requests.get(f"{API_URL}/orders/view-orders", headers=headers)
    
    if view_orders_response.status_code != 200:
        print(f"❌ Failed to get view orders: {view_orders_response.status_code}")
        return
    
    categories = view_orders_response.json()
    
    # Extract all orders from view-orders response
    view_orders_list = []
    for category in categories:
        for item in category['items']:
            for order in item['orders']:
                view_orders_list.append(order)
    
    print(f"📋 View orders returned: {len(view_orders_list)} orders")
    
    # Show details of orders in view-orders
    print(f"\n4. Details of {len(view_orders_list)} orders in view-orders:")
    for i, order in enumerate(view_orders_list, 1):
        print(f"   {i}. Order #{order.get('orderNumber')} - {order.get('customerName')}")
        print(f"      ID: {order.get('order_id')}")
        print(f"      Item: {order.get('item_name')} (cooking status: {order.get('cooking_status')})")
    
    # Cross-reference to find discrepancies
    print(f"\n5. Cross-referencing orders...")
    
    view_order_ids = {order['order_id'] for order in view_orders_list}
    pending_order_ids = {order['id'] for order in pending_orders}
    
    print(f"📋 Unique order IDs in view-orders: {len(view_order_ids)}")
    print(f"📋 Unique order IDs in pending orders: {len(pending_order_ids)}")
    
    # Find orders in view-orders that are not in pending
    extra_in_view = view_order_ids - pending_order_ids
    if extra_in_view:
        print(f"🚨 ISSUE: {len(extra_in_view)} orders in view-orders that are NOT pending:")
        for order_id in extra_in_view:
            # Find the actual status of this order
            matching_order = next((o for o in all_orders if o['id'] == order_id), None)
            if matching_order:
                print(f"   - Order ID {order_id} has status: {matching_order.get('status')}")
            else:
                print(f"   - Order ID {order_id} not found in all orders!")
    
    # Find pending orders not in view-orders
    missing_from_view = pending_order_ids - view_order_ids
    if missing_from_view:
        print(f"🚨 ISSUE: {len(missing_from_view)} pending orders NOT in view-orders:")
        for order_id in missing_from_view:
            matching_order = next((o for o in pending_orders if o['id'] == order_id), None)
            if matching_order:
                print(f"   - Order #{matching_order.get('orderNumber')} ({order_id}) is pending but not in view-orders")
                print(f"     Customer: {matching_order.get('customerName')}")
                print(f"     Order Number Type: {type(matching_order.get('orderNumber'))}")
                print(f"     Has orderNumber field: {'orderNumber' in matching_order}")
    
    if not extra_in_view and not missing_from_view:
        print("✅ Perfect match: All pending orders are in view-orders, no extra orders")
    
    print(f"\n6. Summary:")
    print(f"   Database pending orders: {len(pending_orders)}")
    print(f"   View-orders total items: {len(view_orders_list)}")
    print(f"   View-orders unique orders: {len(view_order_ids)}")
    
    if len(view_order_ids) != len(pending_orders):
        print(f"🚨 MISMATCH DETECTED: Expected {len(pending_orders)} orders in view-orders, got {len(view_order_ids)}")
    else:
        print("✅ Order counts match correctly")

if __name__ == "__main__":
    debug_view_orders()
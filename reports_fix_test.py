#!/usr/bin/env python3
"""
Quick test to verify reports export fix
"""

import requests
import json

# Get backend URL
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
            print(f"Auth failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Auth error: {str(e)}")
        return None

def test_reports_fix():
    """Test if reports export endpoints are fixed"""
    print("🔧 Testing Reports Export Fix")
    
    # Get auth token
    auth_token = get_auth_token()
    if not auth_token:
        print("❌ Authentication failed")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create a test order with valid menu items
    print("\n1. Creating test order...")
    test_order = {
        "customerName": "Fix Test Customer",
        "items": [
            {"name": "Paya", "quantity": 1},
            {"name": "Idly (3)", "quantity": 2}
        ],
        "paymentMethod": "cash"
    }
    
    create_response = requests.post(f"{API_URL}/orders/", json=test_order, headers=headers)
    
    if create_response.status_code == 201:
        order = create_response.json()
        print(f"✅ Created order #{order['orderNumber']} - ${order['totalAmount']}")
        
        # Complete the order
        print("\n2. Completing test order...")
        order_id = order['id']
        
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
                    print(f"✅ Order auto-completed")
                    break
    else:
        print(f"❌ Failed to create order: {create_response.status_code}")
        print(f"Error: {create_response.text}")
    
    # Test export endpoints
    print("\n3. Testing export endpoints...")
    export_endpoints = [
        ("/reports/price-analysis/export", "Price Analysis Export"),
        ("/reports/payment/export", "Payment Reports Export"),
        ("/reports/items/export", "Item Reports Export")
    ]
    
    success_count = 0
    
    for endpoint, name in export_endpoints:
        response = requests.get(f"{API_URL}{endpoint}", headers=headers)
        
        if response.status_code == 200:
            if response.content.startswith(b'PK'):
                print(f"✅ {name} SUCCESS - Valid Excel file ({len(response.content)} bytes)")
                success_count += 1
            else:
                print(f"❌ {name} - Invalid Excel format")
        else:
            print(f"❌ {name} FAILED - Status: {response.status_code}")
            if response.status_code == 500:
                try:
                    error = response.json().get('detail', 'No error detail')
                    print(f"   Error: {error}")
                except:
                    print(f"   Raw error: {response.text[:200]}")
    
    print(f"\n📊 Results: {success_count}/3 export endpoints working")
    
    if success_count == 3:
        print("🎉 ALL EXPORT ENDPOINTS FIXED!")
        return True
    else:
        print("❌ Some export endpoints still failing")
        return False

if __name__ == "__main__":
    success = test_reports_fix()
    exit(0 if success else 1)
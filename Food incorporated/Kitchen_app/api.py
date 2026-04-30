import requests

# Change this to your Render URL later if you deploy!
BASE_URL = "http://127.0.0.1:5000" 

def fetch_orders():
    response = requests.get(f"{BASE_URL}/orders")
    return response.json()

def update_order_status(order_id, status):
    payload = {"status": status}
    return requests.patch(f"{BASE_URL}/orders/{order_id}/status", json=payload)

def fetch_stock():
    response = requests.get(f"{BASE_URL}/stock")
    return response.json()

def update_stock(item_id, change):
    payload = {"id": item_id, "change": change}
    return requests.post(f"{BASE_URL}/stock/update", json=payload)
# api.py
import requests

BASE_URL = "http://localhost:5000"

def fetch_orders():
    try:
        return requests.get(f"{BASE_URL}/orders").json()
    except:
        return []

def update_order_status(order_number, status):
    requests.patch(
        f"{BASE_URL}/orders/{order_number}/status",
        json={"status": status}
    )

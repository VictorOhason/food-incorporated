# api.py
import requests
# api.py
import requests

# REPLACE with your real Render URL
BASE_URL = "https://your-app-name.onrender.com"

def fetch_orders():
    try:
        # Note: Render "goes to sleep" after 15 mins of inactivity.
        # The first request might take 30 seconds to wake up!
        return requests.get(f"{BASE_URL}/orders", timeout=10).json()
    except:
        return []

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

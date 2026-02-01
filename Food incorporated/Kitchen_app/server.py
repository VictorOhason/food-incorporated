import os
from flask import Flask, jsonify, request
from flask_cors import CORS 
app = Flask(__name__)
# Change CORS to allow your specific GitHub URL
CORS(app, resources={r"/*": {"origins": ["https://victorohason.github.io/food-incorporated/", "http://localhost:5000"]}})

# Our "Database" (List of orders)
orders = []

@app.route('/orders', methods=['GET'])
def get_orders():
    return jsonify(orders)

@app.route('/orders', methods=['POST'])
def add_order():
    data = request.json
    
    # We map the website data to the format the Kitchen App expects
    new_order = {
        "orderNumber": data.get("orderNumber"),
        "tableNumber": data.get("tableNumber"),
        "customerName": data.get("customerName"), 
        "status": "pending",
        "items": data.get("items", [])
    }
    
    orders.append(new_order)
    
    # Clean logging so you can see what's happening in the terminal
    print(f"🔔 NEW ORDER: Table {new_order['tableNumber']} for {new_order['customerName']} (#{new_order['orderNumber']})")
    
    return jsonify({"success": True}), 201

@app.route('/orders/<order_id>/status', methods=['PATCH'])
def update_status(order_id):
    new_status = request.json.get("status")
    for order in orders:
        # We convert both to strings to ensure they match correctly
        if str(order["orderNumber"]) == str(order_id):
            order["status"] = new_status
            print(f"📦 Order #{order_id} updated to {new_status}")
            return jsonify({"success": True})
            
    return jsonify({"error": "Order not found"}), 404

if __name__ == "__main__":
    # Change this line to use the PORT provided by the host
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
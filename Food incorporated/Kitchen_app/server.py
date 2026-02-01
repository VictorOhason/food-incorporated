from flask import Flask, jsonify, request
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)  # Allows the website to talk to this server

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
    # Standard port for local development
    print("🚀 Kitchen Server starting on http://127.0.0.1:5000")
    app.run(port=5000, debug=True)
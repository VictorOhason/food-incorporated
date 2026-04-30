import os
import random
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from threading import Thread
from dotenv import load_dotenv
from models import db, Store, Table, Order, StockItem

# 1. load environment variables from .env if present
load_dotenv()

app = Flask(__name__)

# 2. application config
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///foodinc.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. cors setup
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
CORS(app, resources={
    r"/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

# connect SQLAlchemy to Flask
db.init_app(app)

# 4. database initialization

def init_db():
    """Create database schema and seed default values."""
    with app.app_context():
        db.create_all()

        # seed data only when database is empty
        if Store.query.count() == 0:
            print("Initializing database with default data")

            store1 = Store(store_id='store1', name='Food Inc - Main', location='Downtown')
            store2 = Store(store_id='store2', name='Food Inc - West', location='Westside')
            db.session.add_all([store1, store2])
            db.session.flush()

            for store in [store1, store2]:
                for i in range(1, 11):
                    table = Table(store_id=store.id, table_id=i, status='free')
                    db.session.add(table)

            # initial stock levels for kitchen inventory
            stock_items = [
                StockItem(name="Potatoes", quantity=50, unit="kg"),
                StockItem(name="Cooking Oil", quantity=20, unit="Liters"),
                StockItem(name="Cod Fillets", quantity=30, unit="pcs"),
                StockItem(name="Haddock Fillets", quantity=30, unit="pcs"),
                StockItem(name="Plaice Fillets", quantity=20, unit="pcs"),
                StockItem(name="Whole-tail Scampi", quantity=40, unit="pcs"),
                StockItem(name="Pork Sausages (for batter)", quantity=50, unit="pcs"),
                StockItem(name="Steak (for pies)", quantity=10, unit="kg"),
                StockItem(name="Kidney (for pies)", quantity=5, unit="kg"),
                StockItem(name="Chicken (for pies)", quantity=8, unit="kg"),
                StockItem(name="Mushrooms", quantity=5, unit="kg"),
                StockItem(name="Plain Flour", quantity=25, unit="kg"),
                StockItem(name="Pie Pastry Sheets", quantity=50, unit="pcs"),
                StockItem(name="Mushy Peas", quantity=10, unit="kg"),
                StockItem(name="Curry Sauce", quantity=10, unit="Liters"),
                StockItem(name="Gravy", quantity=8, unit="kg"),
                StockItem(name="Pickled Onions (jarred)", quantity=12, unit="jars"),
                StockItem(name="Traditional Lemonade (bottles/cans)", quantity=24, unit="pcs"),
                StockItem(name="Dandelion & Burdock (bottles/cans)", quantity=24, unit="pcs"),
                StockItem(name="Tea Bags", quantity=200, unit="pcs"),
                StockItem(name="Sugar", quantity=10, unit="kg"),
                StockItem(name="Salt", quantity=5, unit="kg"),
            ]
            db.session.add_all(stock_items)
            db.session.commit()
            print("Database initialized successfully")

# 5. health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "Server is running"}), 200

# 6. stock routes
@app.route('/stock', methods=['GET'])
def get_stock():
    """Return current stock inventory."""
    stock = StockItem.query.all()
    return jsonify([item.to_dict() for item in stock])

@app.route('/stock/update', methods=['POST'])
def update_stock_item():
    """Update a stock item quantity."""
    data = request.json
    item_id = data.get("id")
    change = data.get("change")
    
    item = StockItem.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    item.quantity += change
    if item.quantity < 0:
        item.quantity = 0
    
    db.session.commit()
    return jsonify({"success": True, "new_quantity": item.quantity})

# 7. order routes
@app.route('/orders', methods=['GET'])
def get_orders():
    """Fetch all order records."""
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders])

@app.route('/orders', methods=['POST'])
def add_order():
    """Create a new order"""
    data = request.json
    
    # Validate required fields
    if not data.get("orderNumber") or not data.get("tableNumber"):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Create order
    new_order = Order(
        order_number=data.get("orderNumber"),
        store_id=data.get("storeId", 1),
        table_number=data.get("tableNumber"),
        customer_name=data.get("customerName"),
        customer_email=data.get("customerEmail"),
        status="pending",
        items=data.get("items", []),
        total=data.get("total", 0.0)
    )
    
    db.session.add(new_order)
    db.session.flush()  # flush pending row so stock update can run safely

    # decrement stock for matching ingredients
    for item in new_order.items:
        item_name = item.get("name") if isinstance(item, dict) else str(item)
        if not item_name:
            continue
        
        item_name_l = item_name.lower()
        item_qty = item.get("quantity", 1) if isinstance(item, dict) else 1
        try:
            item_qty = int(item_qty)
        except Exception:
            item_qty = 1
        
        # Find matching stock item
        stock_item = StockItem.query.filter(
            StockItem.name.ilike(f"%{item_name}%")
        ).first()
        
        if stock_item:
            dec_each = random.randint(1, 5)
            dec_total = dec_each * max(1, item_qty)
            stock_item.quantity -= dec_total
            if stock_item.quantity < 0:
                stock_item.quantity = 0
    
    db.session.commit()
    return jsonify({"success": True, "orderNumber": new_order.order_number}), 201

@app.route('/orders/<int:order_id>/status', methods=['PATCH'])
def update_status(order_id):
    """Update order status"""
    new_status = request.json.get("status")
    order = Order.query.filter_by(order_number=order_id).first()
    
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    order.status = new_status
    db.session.commit()
    return jsonify({"success": True})

# 8. table routes
@app.route('/tables', methods=['GET'])
def get_all_tables():
    """Return all table states by store."""
    stores = Store.query.all()
    result = {}
    for store in stores:
        tables = Table.query.filter_by(store_id=store.id).all()
        result[store.store_id] = [table.to_dict() for table in tables]
    return jsonify(result)

@app.route('/tables/<store_id>', methods=['GET'])
def get_store_tables(store_id):
    """Get tables for a specific store"""
    store = Store.query.filter_by(store_id=store_id).first()
    if not store:
        return jsonify({"error": "Store not found"}), 404
    
    tables = Table.query.filter_by(store_id=store.id).all()
    return jsonify({store_id: [table.to_dict() for table in tables]})

@app.route('/tables/assign', methods=['POST'])
def assign_table():
    """Reserve the next available table."""
    data = request.json
    store_id = data.get("storeId", "store1")
    customer_email = data.get("customerEmail")
    
    store = Store.query.filter_by(store_id=store_id).first()
    if not store:
        return jsonify({"error": "Store not found"}), 404
    
    # Find first free table in the store
    table = Table.query.filter_by(
        store_id=store.id,
        status='free'
    ).first()
    
    if not table:
        return jsonify({"error": "No free tables available"}), 409
    
    table.status = 'occupied'
    table.assigned_to = customer_email
    table.occupied_since = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        "success": True,
        "storeId": store_id,
        "tableId": table.table_id,
        "message": f"Table {table.table_id} assigned"
    }), 201

@app.route('/tables/<store_id>/<int:table_id>/free', methods=['PATCH'])
def mark_table_free(store_id, table_id):
    """Mark a table as free"""
    store = Store.query.filter_by(store_id=store_id).first()
    if not store:
        return jsonify({"error": "Store not found"}), 404
    
    table = Table.query.filter_by(
        store_id=store.id,
        table_id=table_id
    ).first()
    
    if not table:
        return jsonify({"error": "Table not found"}), 404
    
    table.status = 'free'
    table.assigned_to = None
    table.occupied_since = None
    
    db.session.commit()
    
    return jsonify({"success": True, "message": f"Table {table_id} is now free"})

# 9. background worker

def check_occupied_tables():
    """Release occupied tables after they have been held for 30 minutes."""
    while True:
        time.sleep(60)

        try:
            with app.app_context():
                current_time = datetime.utcnow()
                occupied_tables = Table.query.filter_by(status='occupied').all()

                for table in occupied_tables:
                    if table.occupied_since:
                        elapsed = (current_time - table.occupied_since).total_seconds() / 60

                        if elapsed >= 30:
                            table.status = 'free'
                            table.assigned_to = None
                            table.occupied_since = None
                            print(f"Table {table.table_id} is now free")

                db.session.commit()
        except Exception as e:
            print(f"Error checking table status: {e}")

# start the table cleanup thread
table_monitor_thread = Thread(target=check_occupied_tables, daemon=True)
table_monitor_thread.start()

# 10. application startup
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('DEBUG', 'False') == 'True')
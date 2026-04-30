from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# 1. database models

# 2. store model
class Store(db.Model):
    """Represents a store location with its tables and orders."""
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tables = db.relationship('Table', backref='store', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='store', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'storeId': self.store_id,
            'name': self.name,
            'location': self.location
        }

# 3. table model
class Table(db.Model):
    """Tracks individual table availability and assignments."""
    __tablename__ = 'tables'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    table_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='free')
    assigned_to = db.Column(db.String(255))
    occupied_since = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('store_id', 'table_id', name='unique_store_table'),)

    def to_dict(self):
        return {
            'tableId': self.table_id,
            'status': self.status,
            'assignedTo': self.assigned_to,
            'occupiedSince': self.occupied_since.isoformat() if self.occupied_since else None
        }

# 4. stock item model
class StockItem(db.Model):
    """Inventory items that can be adjusted by the kitchen."""
    __tablename__ = 'stock_items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float, default=0)
    unit = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit
        }

# 5. order model
class Order(db.Model):
    """Customer order records stored in the database."""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.Integer, unique=True, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    table_number = db.Column(db.Integer, nullable=False)
    customer_name = db.Column(db.String(255))
    customer_email = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')
    items = db.Column(db.JSON)
    total = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'orderNumber': self.order_number,
            'tableNumber': self.table_number,
            'customerName': self.customer_name,
            'customerEmail': self.customer_email,
            'status': self.status,
            'items': self.items or [],
            'total': self.total,
            'createdAt': self.created_at.isoformat()
        }

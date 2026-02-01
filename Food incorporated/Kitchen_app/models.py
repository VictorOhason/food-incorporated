# models.py
class Order:
    def __init__(self, data):
        self.order_number = data["orderNumber"]
        self.table = data["tableNumber"]
        self.items = data["items"]
        self.status = data.get("status", "pending")

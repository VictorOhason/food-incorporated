import threading
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from api import update_order_status

class OrderCard(QWidget):
    def __init__(self, order, refresh_callback):
        super().__init__()
        self.order = order
        self.refresh_callback = refresh_callback
        self.build_ui()

    def build_ui(self):
        self.layout = QVBoxLayout(self)
        
        # Header with Order # and Table
        header = QHBoxLayout()
        self.title = QLabel(f"Order #{self.order.order_number}")
        self.title.setObjectName("orderTitle")
        self.table = QLabel(f"TABLE {self.order.table}")
        self.table.setObjectName("tableLabel")
        
        header.addWidget(self.title)
        header.addStretch()
        header.addWidget(self.table)
        self.layout.addLayout(header)

        # Items List
        for item in self.order.items:
            item_lbl = QLabel(f"{item['quantity']}x {item['name']}")
            item_lbl.setObjectName("itemLabel")
            self.layout.addWidget(item_lbl)

        # Action Button
        self.action_btn = QPushButton()
        self.action_btn.setObjectName("actionBtn")
        self.action_btn.clicked.connect(self.handle_action)
        self.layout.addWidget(self.action_btn)
        
        self.update_visuals()

    def update_visuals(self):
        # State Machine Logic
        if self.order.status == "pending":
            self.action_btn.setText("START PREPARING")
            self.action_btn.setVisible(True)
        elif self.order.status == "preparing":
            self.action_btn.setText("MARK AS READY")
            self.action_btn.setVisible(True)
        elif self.order.status == "ready":
            self.action_btn.setText("MARK AS SERVED")
            self.action_btn.setVisible(True)
        else: # "served"
            self.action_btn.setVisible(False)

        self.setProperty("status", self.order.status)
        self.style().unpolish(self)
        self.style().polish(self)

    def handle_action(self):
        # 1. Determine Next Status
        status_map = {
            "pending": "preparing",
            "preparing": "ready",
            "ready": "served"
        }
        new_status = status_map.get(self.order.status, "served")
        
        # 2. Instant UI Update
        self.order.status = new_status
        self.update_visuals()
        
        # 3. Background API Call
        threading.Thread(
            target=update_order_status, 
            args=(self.order.order_number, new_status), 
            daemon=True
        ).start()
import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QScrollArea, QLabel
from PySide6.QtCore import QThread, Signal, QTimer, Qt
from PySide6.QtMultimedia import QSoundEffect, QAudioOutput
from PySide6.QtCore import QUrl

from api import fetch_orders
from models import Order
from widgets.order_card import OrderCard

class FetchWorker(QThread):
    orders_fetched = Signal(list)
    def run(self):
        data = fetch_orders()
        self.orders_fetched.emit(data)

class KitchenApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kitchen Pro - Food Inc.")
        self.resize(1000, 800)
        
        self.current_filter = "all"
        self.cards = {}
        self.seen_ids = set() # To track new orders for sound
        
        # Setup Sound
        self.effect = QSoundEffect()
        # You can use a system beep or a local .wav file
        # self.effect.setSource(QUrl.fromLocalFile("alert.wav")) 
        self.effect.setVolume(0.5)

        self.build_ui()
        
        self.worker = FetchWorker()
        self.worker.orders_fetched.connect(self.display_orders)
        
        # PRO FEATURE: Auto-Refresh Timer (Every 10 seconds)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_orders)
        self.refresh_timer.start(10000) 

        self.load_orders()

    def build_ui(self):
        self.main_layout = QVBoxLayout(self)

        # Tabs including "Ready" and "Served"
        tabs_layout = QHBoxLayout()
        self.filters = {
            "all": QPushButton("All"),
            "pending": QPushButton("Pending ⏳"),
            "preparing": QPushButton("Preparing 🔥"),
            "ready": QPushButton("Ready ✅"),
            "served": QPushButton("History 📁")
        }

        for key, btn in self.filters.items():
            btn.clicked.connect(lambda checked, k=key: self.set_filter(k))
            tabs_layout.addWidget(btn)

        self.main_layout.addLayout(tabs_layout)

        self.scroll = QScrollArea()
        self.container = QWidget()
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setAlignment(Qt.AlignTop)
        
        self.scroll.setWidget(self.container)
        self.scroll.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll)

    def set_filter(self, status):
        self.current_filter = status
        for card in self.cards.values():
            self.apply_filter_to_card(card)
        self.load_orders()

    def load_orders(self):
        if not self.worker.isRunning():
            self.worker.start()

    def apply_filter_to_card(self, card):
        # Logic for what to show in each tab
        if self.current_filter == "all":
            card.setVisible(card.order.status != "served")
        else:
            card.setVisible(card.order.status == self.current_filter)

    def display_orders(self, orders_data):
        incoming_ids = [o["orderNumber"] for o in orders_data]
        is_first_load = len(self.seen_ids) == 0

        for raw in orders_data:
            order = Order(raw)
            oid = order.order_number

            # PRO FEATURE: Sound Alert for new orders
            if oid not in self.seen_ids:
                self.seen_ids.add(oid)
                if not is_first_load:
                    self.effect.play() # "Ding!"
                    print(f"New Order Alert: #{oid}")

            if oid in self.cards:
                card = self.cards[oid]
                card.order = order 
                card.update_visuals()
            else:
                card = OrderCard(order, self.load_orders)
                self.cards[oid] = card
                self.list_layout.insertWidget(0, card) # Newest at top
            
            self.apply_filter_to_card(card)

        # Cleanup deleted orders
        for oid in list(self.cards.keys()):
            if oid not in incoming_ids:
                self.cards[oid].setParent(None)
                del self.cards[oid]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        with open("styles.qss", "r") as f:
            app.setStyleSheet(f.read())
    except:
        pass
    window = KitchenApp()
    window.show()
    sys.exit(app.exec())
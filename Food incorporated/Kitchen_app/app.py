import tkinter as tk
from tkinter import ttk 
# Added update_stock to the imports
from api import fetch_orders, update_order_status, fetch_stock, update_stock 

# --- TOOLS (Functions) ---

def handle_click(order_number, current_status, button_widget):
    button_widget.config(state="disabled", text="Updating...")
    new_status = "preparing" if current_status == "pending" else "ready"
    try:
        update_order_status(order_number, new_status)
    except Exception as e:
        print(f"Failed to update server: {e}")
    load_data()

def create_order_card(parent, order_number, table_name, items, status="pending"):
    colors = {"pending": "#facc15", "preparing": "#3b82f6", "ready": "#22c55e"}
    status_color = colors.get(status, "#9ca3af")
    card = tk.Frame(parent, bg="white", highlightbackground="#d1d5db", highlightthickness=1, bd=0)
    card.pack(fill="x", padx=10, pady=5)
    stripe = tk.Frame(card, bg=status_color, width=10)
    stripe.pack(side="left", fill="y")
    content = tk.Frame(card, bg="white")
    content.pack(side="left", fill="both", expand=True, padx=10, pady=5)
    tk.Label(content, text=f"Order #{order_number}", bg="white", fg="#0a2a66", font=("Arial", 12, "bold")).pack(anchor="w")
    tk.Label(content, text=f" TABLE {table_name} ", bg="#ffeeef", fg="#c8102e", font=("Arial", 10, "bold")).pack(anchor="w", pady=2)
    for item in items:
        item_text = item.get("name", "Unknown Item") if isinstance(item, dict) else item
        tk.Label(content, text=f"• {item_text}", bg="white", fg="#4b5563", font=("Arial", 10)).pack(anchor="w", padx=10)
    if status != "ready":
        btn_text = "Start Cooking" if status == "pending" else "Mark as Ready"
        action_btn = tk.Button(content, text=btn_text, bg="#0a2a66", fg="white")
        action_btn.config(command=lambda: handle_click(order_number, status, action_btn))
        action_btn.pack(pady=5, fill="x")
    return card

def load_data():
    try:
        orders = fetch_orders()
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        for o in orders:
            create_order_card(scrollable_frame, o.get("orderNumber", "???"), o.get("tableNumber", "N/A"), o.get("items", []), o.get("status", "pending"))
    except Exception as e:
        print(f"Order Connection Error: {e}")
    root.after(5000, load_data)
    root.after(30000, load_stock_data) # 30000 milliseconds = 30 seconds

def load_stock_data():
    try:
        for widget in stock_frame.winfo_children():
            widget.destroy()
        stock_list = fetch_stock()
        
        for i, item in enumerate(stock_list):
            # Logic: If stock is less than 5, use Red text
            qty_color = "red" if item["quantity"] < 5 else "black"
            
            tk.Label(stock_frame, text=item["name"], font=("Arial", 10, "bold"), bg="white").grid(row=i, column=0, padx=20, pady=10, sticky="w")
            
            tk.Button(stock_frame, text="-", width=3, bg="#ef4444", fg="white",
                    command=lambda i=item: [update_stock(i['id'], -1), load_stock_data()]).grid(row=i, column=1)
            
            # Apply the color to the quantity label
            tk.Label(stock_frame, text=f"{item['quantity']} {item['unit']}", bg="white", fg=qty_color, width=10, font=("Arial", 10, "bold")).grid(row=i, column=2)
            
            tk.Button(stock_frame, text="+", width=3, bg="#22c55e", fg="white",
                    command=lambda i=item: [update_stock(i['id'], 1), load_stock_data()]).grid(row=i, column=3)
    except Exception as e:
        print(f"Stock Connection Error: {e}")

# --- UI SETUP ---
root = tk.Tk()
root.title("Food.Inc Kitchen")
root.geometry("600x800")

top_bar = tk.Frame(root, bg="#0a2a66", height=60)
top_bar.pack(fill="x")
tk.Label(top_bar, text="KITCHEN SYSTEM", fg="white", bg="#0a2a66", font=("Arial", 16, "bold")).pack(pady=15)

notebook = ttk.Notebook(root)
order_frame = tk.Frame(notebook, bg="#f3f4f6")
stock_frame = tk.Frame(notebook, bg="white")
notebook.add(order_frame, text=" Orders ")
notebook.add(stock_frame, text=" Stock Management ")
notebook.pack(fill="both", expand=True)

container = tk.Frame(order_frame)
container.pack(fill="both", expand=True)
canvas = tk.Canvas(container, bg="#f3f4f6", highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)
scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)
scrollable_frame = tk.Frame(canvas, bg="#f3f4f6")
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=580)

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
scrollable_frame.bind("<Configure>", on_frame_configure)
def on_canvas_configure(event):
    canvas.itemconfig(1, width=event.width)
canvas.bind("<Configure>", on_canvas_configure)

load_data()
load_stock_data()
root.mainloop()
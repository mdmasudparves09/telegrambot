import json

ORDERS_FILE = "orders.json"

def get_orders():
    """Returns all orders from the database."""
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def add_order(order):
    """Adds an order to the database."""
    orders = get_orders()
    orders.append(order)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=4)

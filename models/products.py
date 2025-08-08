import json

PRODUCTS_FILE = "products.json"

def get_products():
    """Returns all products from the database."""
    try:
        with open(PRODUCTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def add_product(product):
    """Adds a product to the database."""
    products = get_products()
    products.append(product)
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=4)

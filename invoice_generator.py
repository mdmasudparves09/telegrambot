from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Order Invoice', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_invoice(order_details: dict, products: list) -> str:
    print("Attempting to generate invoice...")
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    order_id = order_details.get('order_id', 'N/A')
    pdf.cell(0, 10, f"Order ID: {order_id}", 0, 1)
    pdf.cell(0, 10, f"Customer Name: {order_details.get('name')}", 0, 1)
    pdf.cell(0, 10, f"Customer Phone: {order_details.get('phone')}", 0, 1)
    pdf.cell(0, 10, f"Customer Email: {order_details.get('email')}", 0, 1)
    pdf.ln(10)

    # Table Header
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(100, 10, 'Product', 1)
    pdf.cell(30, 10, 'Quantity', 1)
    pdf.cell(30, 10, 'Price', 1)
    pdf.ln()

    # Table Body
    pdf.set_font('Arial', '', 12)
    for pid, qty in order_details.get('cart', {}).items():
        prod = next((p for p in products if p['id'] == pid), None)
        if prod:
            pdf.cell(100, 10, prod['name'], 1)
            pdf.cell(30, 10, str(qty), 1)
            pdf.cell(30, 10, str(prod['price'] * qty), 1)
            pdf.ln()

    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Total Amount: {order_details.get('total_price')} BDT", 0, 1)

    # Ensure invoices directory exists
    if not os.path.exists('invoices'):
        os.makedirs('invoices')

    invoice_path = f"invoices/{order_id}.pdf"
    pdf.output(invoice_path)
    print(f"Invoice generated at: {invoice_path}")
    return invoice_path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from models.products import get_products
from config import ADMIN_CHAT_ID
from invoice_generator import generate_invoice
import datetime
import os

# Updated conversation states
NAME, PHONE, EMAIL, GET_TRANSACTION_ID = range(4)

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer("✅ Added to Cart!")
    product_id = int(query.data.split('_')[1])
    cart = context.user_data.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1
    context.user_data['cart'] = cart

async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query:
        await query.answer()
    cart = context.user_data.get('cart', {})
    if not cart:
        await (query.message if query else update.message).reply_text("🛒 Your cart is empty.")
        return

    products = get_products()
    message = "<b>✨ Your Shopping Cart ✨</b>\n" + "—"*20 + "\n"
    total_price = 0
    for product_id, quantity in cart.items():
        product = next((p for p in products if p['id'] == int(product_id)), None)
        if product:
            subtotal = product['price'] * quantity
            total_price += subtotal
            message += f"<b>{product['name']}</b>\n<i>(x{quantity})</i> - {subtotal} BDT\n\n"
    message += "—"*20 + "\n" + f"<b>Total Amount: {total_price} BDT</b>"
    context.user_data['total_price'] = total_price
    keyboard = [[InlineKeyboardButton("✅ Proceed to Checkout", callback_data='checkout')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if query:
        await query.edit_message_text(message, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)

async def start_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("First, what is your <b>full name</b>?", parse_mode='HTML')
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Next, what is your <b>contact phone number</b>?", parse_mode='HTML')
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Finally, what is your <b>email address</b>?", parse_mode='HTML')
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['email'] = update.message.text
    customer_details = {
        "name": context.user_data['name'],
        "phone": context.user_data['phone'],
        "email": context.user_data['email'],
        "cart": context.user_data.get('cart', {}),
        "total_price": context.user_data.get('total_price', 0),
        "chat_id": update.message.chat_id
    }
    context.user_data['customer_order'] = customer_details
    payment_keyboard = [
        [InlineKeyboardButton("bKash", callback_data="pay_bKash"), InlineKeyboardButton("Nagad", callback_data="pay_Nagad")],
        [InlineKeyboardButton("Bank Deposit", callback_data="pay_Bank"), InlineKeyboardButton("PayPal", callback_data="pay_PayPal")],
        [InlineKeyboardButton("Payoneer", callback_data="pay_Payoneer"), InlineKeyboardButton("Pyypl", callback_data="pay_Pyypl")]
    ]
    await update.message.reply_text("Thank you! Please choose your payment method:", reply_markup=InlineKeyboardMarkup(payment_keyboard))
    return ConversationHandler.END

async def show_payment_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    method = query.data.split('_')[1]
    context.user_data['payment_method'] = method
    details = {
        "bKash": "Use 'Send Money' to: <code>01234567890</code> (Personal)\nReference: Your Name",
        "Nagad": "Use 'Send Money' to: <code>01987654321</code> (Personal)\nReference: Your Name",
        "Bank": "Acc Name: Your Company\nAcc No: 123456789\nBank: The Bank Ltd\nBranch: Main Branch",
        "PayPal": "Send to: <code>yourpaypal@example.com</code>\nNote: Your Order",
        "Payoneer": "Send to: <code>yourpayoneer@example.com</code>",
        "Pyypl": "Top-up to: <code>+1234567890</code>"
    }
    keyboard = [[InlineKeyboardButton("✅ I have paid", callback_data="payment_done")]]
    await query.edit_message_text(f"<b>To pay with {method}:</b>\n\n{details.get(method)}\n\n<i>After paying, press the button below.</i>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def ask_for_transaction_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Please send the <b>Transaction ID</b> and a <b>Screenshot</b> of the payment confirmation.", parse_mode='HTML')
    return GET_TRANSACTION_ID

async def finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("Finalizing order...")
    order_details = context.user_data.get('customer_order', {})
    products = get_products()

    # Generate a unique Order ID
    order_id = f"ORDER-{update.effective_chat.id}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    order_details['order_id'] = order_id

    # Get Transaction ID and Screenshot
    order_details['transaction_id'] = update.message.text or "Not provided"
    order_details['screenshot_id'] = update.message.photo[-1].file_id if update.message.photo else "Not provided"

    invoice_path = None
    try:
        invoice_path = generate_invoice(order_details, products)
        print(f"Invoice generated successfully at: {invoice_path}")
    except Exception as e:
        print(f"ERROR: Failed to generate invoice: {e}")
        await update.message.reply_text("An error occurred while generating your invoice. Please contact support.")

    # --- Admin Notification ---
    admin_caption = f"<b>✅ New Order & Payment!</b>\n<b>Order ID:</b> <code>{order_id}</code>\n\n"
    admin_caption += f"<b>👤 Customer:</b> {order_details.get('name')} (<code>{order_details.get('chat_id')}</code>)\n"
    admin_caption += f"<b>📞 Phone:</b> {order_details.get('phone')}\n<b>📧 Email:</b> {order_details.get('email')}\n"
    admin_caption += f"<b>💳 Method:</b> {context.user_data.get('payment_method')}\n"
    admin_caption += f"<b>🧾 Transaction ID:</b> <code>{order_details['transaction_id']}</code>\n"

    delivery_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🚚 Deliver Product", callback_data=f"deliver_{order_details.get('chat_id')}")]])
    
    try:
        if invoice_path and os.path.exists(invoice_path):
            with open(invoice_path, 'rb') as f_invoice:
                await context.bot.send_document(chat_id=ADMIN_CHAT_ID, document=f_invoice, caption=admin_caption, parse_mode='HTML', reply_markup=delivery_markup)
            print("Admin notification (with invoice) sent.")
        else:
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_caption + "\n\n<i>(Invoice generation failed)</i>", parse_mode='HTML', reply_markup=delivery_markup)
            print("Admin notification (without invoice) sent.")

        if order_details['screenshot_id'] != "Not provided":
            await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=order_details['screenshot_id'], caption="Payment Screenshot")
            print("Payment screenshot sent to admin.")

    except Exception as e:
        print(f"CRITICAL ERROR: Failed to send admin notification or invoice: {e}")
        await update.message.reply_text("An error occurred while notifying the admin. Please contact support directly.")

    # --- Thank Customer & Send Invoice ---
    customer_message = "🎉 <b>Thank You!</b>\n\nYour order is complete. We will verify your payment and deliver your product shortly. Here is your invoice."
    try:
        await update.message.reply_text(customer_message, parse_mode='HTML')
        if invoice_path and os.path.exists(invoice_path):
            with open(invoice_path, 'rb') as f_invoice:
                await context.bot.send_document(chat_id=update.effective_chat.id, document=f_invoice)
            print("Invoice sent to customer.")
        else:
            await update.message.reply_text("<i>(Invoice could not be generated. Please contact support for your invoice.)</i>", parse_mode='HTML')
            print("Invoice not sent to customer (file missing).")

    except Exception as e:
        print(f"ERROR: Failed to send invoice to customer: {e}")
        await update.message.reply_text("An error occurred while sending your invoice. Please contact support.")

    # Clean up user data
    for key in list(context.user_data.keys()):
        del context.user_data[key]
            
    return ConversationHandler.END

async def cancel_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Order cancelled.")
    for key in list(context.user_data.keys()):
        del context.user_data[key]
    return ConversationHandler.END
from telegram import Update
from telegram.ext import ContextTypes

async def about_us(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends the detailed about us message."""
    message = (
        "<b>🌟 Welcome to Our Store! 🌟</b>\n\n"
        "We are a passionate team dedicated to bringing you high-quality products with a seamless shopping experience. "
        "Our mission is to blend style, quality, and affordability, ensuring you find something you love every time you visit.\n\n"
        "From hand-picked materials to exceptional customer service, we are committed to excellence in everything we do. "
        "Thank you for choosing to shop with us!"
    )
    await update.message.reply_text(message, parse_mode='HTML')

async def payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends the detailed payment information message."""
    message = (
        "<b>💳 Payment Information</b>\n\n"
        "We offer a variety of secure payment methods for your convenience. Below are the details for each:\n\n"
        "<b><u>Local Payments (Bangladesh):</u></b>\n"
        "- <b>bKash:</b> Use the 'Send Money' option to our Personal account: <code>01234567890</code>. Use your name as the reference.\n"
        "- <b>Nagad:</b> Use the 'Send Money' option to our Personal account: <code>01987654321</code>. Use your name as the reference.\n\n"
        "<b><u>International & Bank Payments:</u></b>\n"
        "- <b>Bank Deposit:</b> Account Name: Your Company Name, Account No: 123456789, Bank Name: The Bank Ltd, Branch: Main Branch.\n"
        "- <b>PayPal:</b> Send to our email: <code>yourpaypal@example.com</code>. Please use 'Friends & Family' or cover the transaction fee.\n"
        "- <b>Payoneer:</b> Send to our email: <code>yourpayoneer@example.com</code>.\n"
        "- <b>Pyypl:</b> Top-up to the phone number: <code>+1234567890</code>.\n\n"
        "After completing your payment, please take a screenshot and contact our support team with your transaction ID to confirm your order."
    )
    await update.message.reply_text(message, parse_mode='HTML')
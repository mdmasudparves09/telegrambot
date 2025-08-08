from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models.products import get_products

async def search_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Searches for products based on user's text input."""
    query = update.message.text.lower()
    products = get_products()

    # Find products where the query is in the product name
    results = [p for p in products if query in p['name'].lower()]

    if not results:
        await update.message.reply_text("😕 Sorry, I couldn't find any products matching that name.")
        return

    keyboard = []
    for product in results:
        button = [InlineKeyboardButton(f"{product['name']} - {product['price']} BDT", callback_data=f"product_{product['id']}")]
        keyboard.append(button)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Here are the products I found:", reply_markup=reply_markup)

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models.products import get_products

# Get the absolute path of the project's root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays a paginated menu of all available products."""
    products = get_products()
    if not products:
        await update.message.reply_text("There are no products available at the moment.")
        return

    keyboard = []
    for product in products:
        button = [InlineKeyboardButton(f"{product['name']} - {product['price']} BDT", callback_data=f"product_{product['id']}")]
        keyboard.append(button)
    
    keyboard.append([InlineKeyboardButton("🛒 Go to Cart", callback_data="view_cart")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please select a product to view details:", reply_markup=reply_markup)

async def view_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays details for a single product, including an image."""
    query = update.callback_query
    await query.answer()

    try:
        product_id = int(query.data.split('_')[1])
    except (IndexError, ValueError):
        await query.edit_message_text("Error: Invalid product data.")
        return

    products = get_products()
    product = next((p for p in products if p['id'] == product_id), None)

    if not product:
        await query.edit_message_text("Sorry, this product could not be found.")
        return

    caption = f"<b>{product['name']}</b>\n\n"
    caption += f"{product['description']}\n\n"
    caption += f"<b>Price:</b> {product['price']} BDT"

    keyboard = [
        [InlineKeyboardButton("➕ Add to Cart", callback_data=f"add_{product['id']}")],
        [InlineKeyboardButton("◀️ Back to Products", callback_data="list_products")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Construct absolute path for the image
    image_path = os.path.join(PROJECT_ROOT, 'images', product['image'])

    try:
        await query.message.delete() # Clean up the previous message first
        with open(image_path, 'rb') as image_file:
            await query.message.reply_photo(
                photo=image_file,
                caption=caption,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
    except FileNotFoundError:
        print(f"Image not found at path: {image_path}")
        await query.message.reply_text(
            f"🖼️ (Image for <b>{product['name']}</b> is missing)\n\n{caption}",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"An error occurred in view_product: {e}")
        await query.message.reply_text("Sorry, an error occurred while displaying this product.")

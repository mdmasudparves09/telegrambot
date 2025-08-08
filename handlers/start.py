from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message and the main menu."""
    keyboard = [
        ["🛍️ View Products", "🛒 My Cart"],
        ["ℹ️ About Us", "💳 Payment Info"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Welcome to your E-Commerce Assistant! 🤖\n\n"
        "How can I help you today?",
        reply_markup=reply_markup
    )
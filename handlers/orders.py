from telegram import Update
from telegram.ext import ContextTypes

async def view_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays all orders."""
    # This will be implemented later
    await update.message.reply_text("This is where the orders will be.")

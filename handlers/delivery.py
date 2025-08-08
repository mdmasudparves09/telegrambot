from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

# Conversation state
SEND_PRODUCT = range(1)

async def start_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the delivery process by asking the admin what to send."""
    query = update.callback_query
    await query.answer()

    customer_chat_id = query.data.split('_')[1]
    context.user_data['delivery_chat_id'] = customer_chat_id

    await query.message.reply_text(
        f"🚚 <b>Ready to Deliver</b>\n\nTo deliver the product to customer <code>{customer_chat_id}</code>, "
        "please send the file, text, photo, or link now.",
        parse_mode='HTML'
    )
    return SEND_PRODUCT

async def send_product_to_customer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Detects message type and sends it to the customer."""
    customer_chat_id = context.user_data.get('delivery_chat_id')
    if not customer_chat_id:
        await update.message.reply_text("Error: Customer ID not found.")
        return ConversationHandler.END

    message = update.message
    try:
        if message.text:
            await context.bot.send_message(chat_id=customer_chat_id, text=message.text)
        elif message.photo:
            await context.bot.send_photo(chat_id=customer_chat_id, photo=message.photo[-1].file_id, caption=message.caption)
        elif message.document:
            await context.bot.send_document(chat_id=customer_chat_id, document=message.document.file_id, caption=message.caption)
        elif message.video:
            await context.bot.send_video(chat_id=customer_chat_id, video=message.video.file_id, caption=message.video.caption)
        elif message.audio:
            await context.bot.send_audio(chat_id=customer_chat_id, audio=message.audio.file_id, caption=message.audio.caption)
        else:
            await update.message.reply_text("Sorry, I can't deliver this type of file.")
            return SEND_PRODUCT # Ask again

        await update.message.reply_text(f"✅ Product delivered successfully to customer <code>{customer_chat_id}</code>!", parse_mode='HTML')
        del context.user_data['delivery_chat_id']
        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text(f"Failed to deliver product. Error: {e}")
        return ConversationHandler.END

async def cancel_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the delivery process."""
    if 'delivery_chat_id' in context.user_data:
        del context.user_data['delivery_chat_id']
    await update.message.reply_text("Delivery cancelled.")
    return ConversationHandler.END
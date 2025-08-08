import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler,
)

from config import TELEGRAM_TOKEN
from handlers.start import start
from handlers.products import list_products, view_product
from handlers.cart import (
    add_to_cart, view_cart, start_checkout, get_name, get_phone, get_email,
    show_payment_details, ask_for_transaction_id, finalize_order, cancel_checkout,
    NAME, PHONE, EMAIL, GET_TRANSACTION_ID
)
from handlers.info import about_us, payment_info
from handlers.search import search_products
from handlers.delivery import (
    start_delivery, send_product_to_customer, cancel_delivery, SEND_PRODUCT
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Combined conversation handler for checkout, payment, and delivery
    main_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_checkout, pattern='^checkout$'),
            CallbackQueryHandler(ask_for_transaction_id, pattern='^payment_done$'),
            CallbackQueryHandler(start_delivery, pattern='^deliver_')
        ],
        states={
            # Checkout States
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            GET_TRANSACTION_ID: [MessageHandler(filters.TEXT | filters.PHOTO, finalize_order)],
            # Delivery State
            SEND_PRODUCT: [MessageHandler(filters.ALL & ~filters.COMMAND, send_product_to_customer)]
        },
        fallbacks=[
            CommandHandler('cancel', cancel_checkout), # General cancel command
            CallbackQueryHandler(cancel_delivery, pattern='^cancel_delivery$')
        ],
        allow_reentry=True
    )

    application.add_handler(main_conversation)

    # --- Top-Level Handlers ---
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^🛍️ View Products$"), list_products))
    application.add_handler(MessageHandler(filters.Regex("^🛒 My Cart$"), view_cart))
    application.add_handler(MessageHandler(filters.Regex("^ℹ️ About Us$"), about_us))
    application.add_handler(MessageHandler(filters.Regex("^💳 Payment Info$"), payment_info))
    
    # Callback handlers that are NOT part of a conversation
    application.add_handler(CallbackQueryHandler(list_products, pattern='^list_products$'))
    application.add_handler(CallbackQueryHandler(view_product, pattern='^product_'))
    application.add_handler(CallbackQueryHandler(add_to_cart, pattern='^add_'))
    application.add_handler(CallbackQueryHandler(view_cart, pattern='^view_cart$'))
    application.add_handler(CallbackQueryHandler(show_payment_details, pattern='^pay_'))

    # Search handler (must be last)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_products))

    application.run_polling()

if __name__ == "__main__":
    main()
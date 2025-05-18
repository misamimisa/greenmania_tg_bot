import asyncio
from aiogram import executor
from config import dp, logger, bot

# Import handler registration functions
from handlers.base import register_base
from handlers.booking import register_booking
from handlers.question import register_question
from handlers.admin import register_admin
from handlers.user_message import register_user_message
from handlers.broadcast import register_broadcast
from handlers.info import register_info
from handlers.users import register_users

async def drop_webhook():
    """
    Delete any existing webhook and drop pending updates
    to ensure polling receives all updates.
    """
    await bot.delete_webhook(drop_pending_updates=True)

# Function to register all handlers
def register_all_handlers():
    # Register base handlers (/start, menu, stop)
    register_base(dp)
    # Register booking flow handlers
    register_booking(dp)
    # Register question flow handlers
    register_question(dp)
    # Register admin reply handlers
    register_admin(dp)
    # Register user message fallback handlers
    register_user_message(dp)
    # Register broadcast message handlers
    register_broadcast(dp)
    # Register user info lookup handlers
    register_info(dp)
    # Register users listing handlers
    register_users(dp)

if __name__ == "__main__":
    # Remove existing webhook before starting polling
    asyncio.run(drop_webhook())

    # Log startup
    logger.info("Bot started")

    # Register all dispatcher handlers
    register_all_handlers()

    # Start long-polling to receive updates from Telegram
    executor.start_polling(dp, skip_updates=True)
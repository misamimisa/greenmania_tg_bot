import asyncio
import logging
from aiogram import executor
from config import bot, dp, logger
from handlers.base import register_base
from handlers.booking import register_booking
from handlers.question import register_question
from handlers.admin import register_admin
from handlers.user_message import register_user_message
from handlers.broadcast import register_broadcast
from handlers.info import register_info
from handlers.users import register_users

# === Delete any existing webhook before polling ===
async def drop_webhook():
    # Telegram allows only one getUpdates mechanism at a time.
    # Remove webhook to ensure polling works.
    await bot.delete_webhook(drop_pending_updates=True)
    
# === Ensure there is an asyncio event loop ===
# Create a new event loop and set it as the current one.
# This prevents "no current event loop" errors on start_polling.
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def register_all_handlers():
    register_base(dp)
    register_booking(dp)
    register_question(dp)
    register_admin(dp)
    register_user_message(dp)
    register_broadcast(dp)
    register_info(dp)
    register_users(dp)

if __name__ == "__main__":
    # Drop webhook to avoid ConflictError
    asyncio.run(drop_webhook())
    # Log that bot is starting
    logger.info("Bot started")
    # Register all message and callback handlers
    register_all_handlers()
    # Start polling updates (using the loop we just set)
    executor.start_polling(dp, skip_updates=True)

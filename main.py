import asyncio
import time
from aiogram import executor
from aiogram.utils.exceptions import TerminatedByOtherGetUpdates
from config import bot, dp, logger
from handlers.base import register_base
from handlers.booking import register_booking
from handlers.question import register_question
from handlers.admin import register_admin
from handlers.user_message import register_user_message
from handlers.broadcast import register_broadcast
from handlers.info import register_info
from handlers.users import register_users

# === 1) Create and set a new asyncio event loop ===
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


# === 2) Async function to drop any existing webhook ===
async def drop_webhook():
    # Remove webhook to ensure polling is the only update method
    await bot.delete_webhook(drop_pending_updates=True)

# === 3) Function to register all handlers ===
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
    # 4) Drop webhook using our custom loop
    loop.run_until_complete(drop_webhook())
    logger.info("Bot started; webhook cleared")

    # 5) Register all message & callback handlers
    register_all_handlers()

    # 6) Enter polling loop, retrying on conflict
    while True:
        try:
            executor.start_polling(dp, skip_updates=True)
            break # if start_polling ever returns normally, break out
        except TerminatedByOtherGetUpdates:
            # Telegram reports another getUpdates in progress
            logger.warning("Conflict detected: another getUpdates client, resetting webhook and retrying…")
            loop.run_until_complete(drop_webhook())
            # small delay to avoid tight loop
            time.sleep(1)
            continue
        except Exception as e:
            # catch-all to avoid crashing
            logger.exception("Unexpected error in polling loop, restarting in 5s", exc_info=e)
            time.sleep(5)
            continue
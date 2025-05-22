# handlers/working_hours.py

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram import types
from datetime import datetime, time
import pytz
from config import ADMIN_IDS, logger

class WorkingHoursMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        # Skip admin messages
        if message.from_user.id in ADMIN_IDS:
            return

        # Use pytz for reliable timezone handling
        moscow_tz = pytz.timezone("Europe/Moscow")
        now = datetime.now(moscow_tz)
        current_time = now.time()

        # Debug log to verify
        logger.info(f"⏱ Middleware: current Moscow time is {now.strftime('%Y-%m-%d %H:%M:%S')}")

        # If before 10:00 or at/after 20:00 — send auto-reply and cancel further handlers
        if current_time < time(10, 0) or current_time >= time(20, 0):
            await message.answer(
                "🕒 Мы работаем с 10:00 до 20:00. Мы ответим вам в рабочее время."
            )
            # Stop processing this update by other handlers
            raise CancelHandler()

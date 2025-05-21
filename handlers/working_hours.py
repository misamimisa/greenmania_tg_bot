# handlers/working_hours.py

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram import types
from datetime import datetime, time
from zoneinfo import ZoneInfo
from config import ADMIN_IDS

class WorkingHoursMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        # Skip admin messages
        if message.from_user.id in ADMIN_IDS:
            return

        # Get current time in Moscow
        tz = ZoneInfo("Europe/Moscow")
        now = datetime.now(tz).time()

        # If before 10:00 or at/after 20:00 — send auto-reply and cancel further handlers
        if now < time(10, 0) or now >= time(20, 0):
            await message.answer(
                "🕒 Мы работаем с 10:00 до 20:00. Мы ответим вам в рабочее время."
            )
            # Stop processing this update by other handlers
            raise CancelHandler()

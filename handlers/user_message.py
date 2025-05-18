# Updated handlers/user_message.py

from aiogram import types
from aiogram.dispatcher import Dispatcher
from config import ADMIN_IDS, bot, logger
from services.sheets import append_to_sheet
from state import (
    users_waiting_for_service,
    user_waiting_for_question,
    users_open_chat,
)
from keyboards import get_restart_keyboard, get_main_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# === Handle all text messages from non-admin users ===
async def handle_user_message(message: types.Message):
    user = message.from_user

    # Ignore admin messages
    if user.id in ADMIN_IDS:
        return

    # === Handle booking follow-up ===
    if user.id in users_waiting_for_service:
        logger.info(f"{user.first_name} (@{user.username}) chose service: {message.text}")
        await notify_admins(user, message.text, label="📌 ЗАПИСЬ")
        await message.answer("Спасибо! Администратор скоро свяжется с вами 😊", reply_markup=get_restart_keyboard())
        append_to_sheet(user, message.text, "запись")
        users_waiting_for_service.remove(user.id)
        return

    # === Handle question follow-up ===
    if user.id in user_waiting_for_question:
        logger.info(f"Question from {user.first_name} (@{user.username}): {message.text}")
        await notify_admins(user, message.text, label="❓ ВОПРОС")
        await message.answer("Вопрос получен. Мы скоро ответим 💬", reply_markup=get_restart_keyboard())
        append_to_sheet(user, message.text, "вопрос")
        user_waiting_for_question.discard(user.id)
        return

    # === Handle free chat after /start ===
    if user.id in users_open_chat:
        logger.info(f"{user.first_name} (@{user.username}) message after start: {message.text}")
        await notify_admins(user, message.text, label="💬 Сообщение")
        append_to_sheet(user, message.text, "сообщение после старта")
        return

    # === Fallback for unknown input ===
    # If the user sends text without pressing any buttons
    await message.answer(
        "❗️ Такой команды нет ❗️\n"
    "Пожалуйста, выберите один из пунктов меню ниже ⬇️",
        reply_markup=get_main_keyboard()
    )

# === Notify all admins with a message and reply button ===
async def notify_admins(user, text, label="💬 Сообщение"):
    for admin_id in ADMIN_IDS:
        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton("🔁 Ответить", callback_data=f"reply:{user.id}")
        )
        await bot.send_message(
            admin_id,
            f"{label} от {user.first_name} (@{user.username or 'нет username'}):\n{text}",
            reply_markup=markup
        )

# === Register handler only for non-admin users ===
def register_user_message(dp: Dispatcher):
    from state import users_waiting_for_service, user_waiting_for_question
    # Fallback handlers: only for non-admins NOT in any “waiting” state
    dp.register_message_handler(
        handle_user_message,
        lambda m: (
            m.from_user.id not in ADMIN_IDS
            and m.from_user.id not in users_waiting_for_service
            and m.from_user.id not in user_waiting_for_question
        )
    )


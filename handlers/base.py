from aiogram import types
from aiogram.dispatcher import Dispatcher
from config import logger, ADMIN_IDS, bot
from keyboards import get_main_keyboard, get_admin_keyboard
from services.sheets import append_to_sheet, get_all_user_ids
from state import stopped_users, users_open_chat
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# === Старт / Вернуться в начало ===
async def send_welcome(message: types.Message):
    user = message.from_user
    if user.id in stopped_users:
        stopped_users.remove(user.id)

    all_ids = get_all_user_ids()
    keyboard = get_admin_keyboard() if user.id in ADMIN_IDS else get_main_keyboard()

    if str(user.id) not in all_ids:
        await message.answer(
            f"""Привет, {user.first_name}! 👋 Добро пожаловать в Greenmania 🌿

Поздравляем! Вы поймали скидку 500₽ на массаж 🥳

У нас большой выбор: расслабляющий, антицеллюлитный, холистический и другие.

Сейчас вам напишет администратор и поможет выбрать идеальный вариант и удобное время 💆‍♀️""",
            reply_markup=keyboard
        )
        append_to_sheet(user, "", "старт")
        users_open_chat.add(user.id)

        for admin_id in ADMIN_IDS:
            markup = InlineKeyboardMarkup().add(
                InlineKeyboardButton("🔁 Ответить клиенту", callback_data=f"reply:{user.id}")
            )
            await bot.send_message(
                admin_id,
                f"👤 Новый пользователь: {user.first_name} (@{user.username or 'нет username'})\nID: {user.id}",
                reply_markup=markup
            )

        logger.info(f"Пользователь {user.first_name} (@{user.username}) запустил бота (/start)")
    else:
        await message.answer("Нажми одну из кнопок ниже 👇", reply_markup=keyboard)

# === Остановить бота ===
async def stop_bot(message: types.Message):
    user = message.from_user
    stopped_users.add(user.id)
    await message.answer("Бот остановлен. Чтобы вернуться — нажмите /start", reply_markup=types.ReplyKeyboardRemove())
    append_to_sheet(user, "остановка", "остановка")
    logger.info(f"{user.first_name} (@{user.username}) остановил бота")

# === Регистрация хендлеров ===
def register_base(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=["start"])
    dp.register_message_handler(send_welcome, lambda m: m.text == "↩️ Вернуться в начало")
    dp.register_message_handler(stop_bot, lambda m: m.text == "⛔️ Остановить бота")

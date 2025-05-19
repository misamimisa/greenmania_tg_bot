from aiogram import types
from aiogram.dispatcher import Dispatcher
from config import ADMIN_IDS, bot, logger
from services.sheets import append_to_sheet
from state import user_waiting_for_question
from keyboards import get_restart_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import ChatNotFound, TelegramAPIError

# === 1) Handle "❓ Задать вопрос" button press ===
async def handle_question_click(message: types.Message):
    user = message.from_user

    # mark user as waiting for question input
    user_waiting_for_question.add(user.id)
    logger.info(f"{user.first_name} (@{user.username}) clicked 'Задать вопрос'")

    # ask user to type their question without notifying admins yet
    await message.answer(
        "Напишите ваш вопрос. Мы на связи 👀",
        reply_markup=types.ReplyKeyboardRemove()
    )

# === 2) Handle actual question text input ===
async def handle_question_input(message: types.Message):
    user = message.from_user

    # process only if waiting, and ignore the button text itself
    if user.id not in user_waiting_for_question or message.text == "❓ Задать вопрос":
        return

    question_text = message.text
    logger.info(f"Вопрос от {user.first_name} (@{user.username}): {question_text}")

    # notify admins of the question
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔁 Ответить клиенту", callback_data=f"reply:{user.id}")
    )
    for admin_id in ADMIN_IDS:
        try:
            markup = InlineKeyboardMarkup().add(
                InlineKeyboardButton("🔁 Ответить клиенту", callback_data=f"reply:{user.id}")
            )
            await bot.send_message(
                admin_id,
                f"❓ ВОПРОС от {user.first_name} (@{user.username}):\n{question_text}",
                reply_markup=markup
            )
        except ChatNotFound:
            logger.warning(f"Admin {admin_id}: chat not found, skipping")
        except TelegramAPIError as e:
            logger.error(f"Admin {admin_id}: failed sending question: {e}")

    # record the actual question in Google Sheets
    append_to_sheet(user, question_text, "вопрос")

    # confirm to user
    await message.answer(
        "Ващ вопрос получен, спасибо, мы скоро ответим 💬",
        reply_markup=get_restart_keyboard()
    )

    # clear the waiting flag
    user_waiting_for_question.discard(user.id)

# === Register handlers ===
def register_question(dp: Dispatcher):
    dp.register_message_handler(handle_question_click, lambda m: m.text == "❓ Задать вопрос")
    dp.register_message_handler(
        handle_question_input,
        lambda m: m.from_user.id in user_waiting_for_question and m.text != "❓ Задать вопрос"
    )

from aiogram import types
from aiogram.dispatcher import Dispatcher
from config import ADMIN_IDS, bot, logger
from services.sheets import append_to_sheet
from state import users_waiting_for_service
from keyboards import get_restart_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import ChatNotFound, TelegramAPIError

# === 1) Handle "📝 Записаться" button press ===
async def handle_booking_click(message: types.Message):
    user = message.from_user

    # mark user as waiting for service input
    users_waiting_for_service.add(user.id)
    logger.info(f"{user.first_name} (@{user.username}) clicked 'Записаться'")

    # ask user for service choice without notifying admins yet
    await message.answer(
        "Отлично! На какую услугу вы хотите записаться? 💆‍♀️",
        reply_markup=get_restart_keyboard()
    )

# === 2) Handle actual service text input ===
async def handle_service_input(message: types.Message):
    user = message.from_user

    # process only if user was waiting, and ignore the button text itself
    if user.id not in users_waiting_for_service or message.text == "📝 Записаться":
        return

    service_text = message.text
    logger.info(f"{user.first_name} (@{user.username}) chose service: {service_text}")

    # notify admins of the chosen service
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
                f"📌 ЗАПИСЬ от {user.first_name} (@{user.username}):\n{service_text}",
                reply_markup=markup
            )
        except ChatNotFound:
            logger.warning(f"Admin {admin_id}: chat not found, skipping")
        except TelegramAPIError as e:
            logger.error(f"Admin {admin_id}: failed sending booking: {e}")

    # record the actual service in Google Sheets
    append_to_sheet(user, service_text, "запись")

    # confirm to user
    await message.answer(
        "Спасибо! Администратор скоро свяжется с вами 😊",
        reply_markup=get_restart_keyboard()
    )

    # clear the waiting flag
    users_waiting_for_service.remove(user.id)

# === Register handlers ===
def register_booking(dp: Dispatcher):
    dp.register_message_handler(handle_booking_click, lambda m: m.text == "📝 Записаться")
    dp.register_message_handler(
        handle_service_input,
        lambda m: m.from_user.id in users_waiting_for_service and m.text != "📝 Записаться"
    )

from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import ChatNotFound, TelegramAPIError
from datetime import datetime
from config import ADMIN_IDS, bot, logger
from services.sheets import sheet
from state import admin_reply_targets, admin_waiting_id_input, users_open_chat

# === 🔁 Admin clicked "Reply to client" inline button ===
async def handle_reply_button(callback_query: types.CallbackQuery):
    """Enter reply mode when admin clicks the inline 'Reply' button."""
    admin_id = callback_query.from_user.id
    if admin_id not in ADMIN_IDS:
        await callback_query.answer("⛔️ Нет доступа")
        return

    # Extract user ID and track reply target
    user_id = int(callback_query.data.split(":")[1])
    admin_reply_targets[admin_id] = user_id

    # Prompt admin to write their message
    await bot.send_message(admin_id, f"✍️ Напишите сообщение для пользователя ID: {user_id}")
    await callback_query.answer()

# === ✍️ Admin pressed "Write by ID" button ===
async def ask_user_id(message: types.Message):
    """Ask admin to manually input a Telegram user ID."""
    admin_id = message.from_user.id
    if admin_id not in ADMIN_IDS:
        return

    # Enter ID-input mode
    admin_waiting_id_input.add(admin_id)
    await message.answer("🔢 Введите Telegram ID пользователя, которому хотите написать:")

# === Admin entered a user ID manually ===
async def handle_user_id_input(message: types.Message):
    """Process the Telegram user ID entered by admin."""
    admin_id = message.from_user.id
    if admin_id not in admin_waiting_id_input:
        return

    # Exit ID-input mode
    admin_waiting_id_input.remove(admin_id)

    try:
        target_id = int(message.text.strip())
        admin_reply_targets[admin_id] = target_id
        await message.answer(
            f"✅ Готово. Напишите сообщение — оно будет отправлено пользователю ID {target_id}"
        )
    except ValueError:
        await message.answer("⚠️ Неверный формат. Введите только число (ID пользователя).")

# === Admin sends the actual reply to the selected user ===
async def handle_admin_reply(msg: types.Message):
    """
    Send admin's message to the user, log it in Google Sheets,
    enable free chat for the user, and broadcast the reply to other admins.
    """
    admin_id = msg.from_user.id
    if admin_id not in admin_reply_targets:
        return  # Not currently in reply mode

    user_id = admin_reply_targets.pop(admin_id)
    reply_text = msg.text

    # 1) Send the message to the target user
    try:
        await bot.send_message(user_id, reply_text)
        await msg.reply("✅ Отправлено.")
        logger.info(f"Admin {msg.from_user.full_name} replied to user {user_id}: {reply_text}")
    except Exception as e:
        await msg.reply(f"❌ Не удалось отправить сообщение пользователю: {e}")
        return

    # 2) Allow the user to reply freely (no buttons needed)
    users_open_chat.add(user_id)

    # 3) Record the admin's reply and timestamp in Google Sheets
    header = sheet.row_values(1)
    if "Ответ админа" in header:
        reply_col = header.index("Ответ админа") + 1
        all_rows = sheet.get_all_values()
        for idx, row in enumerate(reversed(all_rows[1:]), 1):
            row_index = len(all_rows) - idx + 1
            if str(user_id) == row[0] and (len(row) < reply_col or not row[reply_col - 1]):
                # write admin reply
                sheet.update_cell(row_index, reply_col, reply_text)
                # write timestamp in the next column
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sheet.update_cell(row_index, reply_col + 1, timestamp)
                break
    else:
        await msg.reply("⚠️ В таблице нет столбца 'Ответ админа'")

    # 4) Broadcast this reply to all other admins to share context
    for other_admin in ADMIN_IDS:
        if other_admin == admin_id:
            continue
        try:
            markup = InlineKeyboardMarkup().add(
                InlineKeyboardButton("🔁 Ответить", callback_data=f"reply:{user_id}")
            )
            await bot.send_message(
                other_admin,
                f"✉️ Админ {msg.from_user.full_name} ответил пользователю ID {user_id}:\n{reply_text}",
                reply_markup=markup
            )
        except ChatNotFound:
            logger.warning(f"Admin {other_admin}: chat not found, skipping broadcast")
        except TelegramAPIError as e:
            logger.error(f"Admin {other_admin}: failed to broadcast reply: {e}")

# === Register all admin-related handlers ===
def register_admin(dp: Dispatcher):
    """Register handlers for admin reply flows."""
    dp.register_callback_query_handler(handle_reply_button, lambda c: c.data.startswith("reply:"))
    dp.register_message_handler(ask_user_id, lambda m: m.text == "✍️ Написать по ID")
    dp.register_message_handler(handle_user_id_input, lambda m: m.from_user.id in admin_waiting_id_input)
    dp.register_message_handler(handle_admin_reply, lambda m: m.from_user.id in admin_reply_targets)
from aiogram import types
from aiogram.dispatcher import Dispatcher
from config import ADMIN_IDS, bot, logger
from services.sheets import sheet
from state import admin_reply_targets, admin_waiting_id_input

# === 🔁 Admin clicked "Ответить клиенту" (inline button) ===
async def handle_reply_button(callback_query: types.CallbackQuery):
    admin_id = callback_query.from_user.id
    if admin_id not in ADMIN_IDS:
        await callback_query.answer("⛔️ Нет доступа")
        return
    # Extract user ID and enter reply mode
    user_id = int(callback_query.data.split(":")[1])
    admin_reply_targets[admin_id] = user_id
    await bot.send_message(admin_id, f"✍️ Напишите сообщение для пользователя ID: {user_id}")
    await callback_query.answer()

# === ✍️ Admin pressed "Написать по ID" button ===
async def ask_user_id(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    admin_waiting_id_input.add(message.from_user.id)
    await message.answer("🔢 Введите Telegram ID пользователя, которому хотите написать:")

# === Admin entered a user ID manually ===
async def handle_user_id_input(message: types.Message):
    admin_id = message.from_user.id
    if admin_id not in admin_waiting_id_input:
        return
    # Exit ID-input mode
    admin_waiting_id_input.remove(admin_id)
    try:
        target_id = int(message.text.strip())
        admin_reply_targets[admin_id] = target_id
        await message.answer(f"✅ Готово. Напишите сообщение — оно будет отправлено пользователю ID {target_id}")
    except:
        await message.answer("⚠️ Неверный формат. Введите только число (ID пользователя).")

# === Admin sends a message to the selected user ===
async def handle_admin_reply(msg: types.Message):
    admin_id = msg.from_user.id
    if admin_id not in admin_reply_targets:
        return  # skip if not in reply mode
    user_id = admin_reply_targets.pop(admin_id)
    try:
        await bot.send_message(user_id, msg.text)
        await msg.reply("✅ Отправлено.")
        logger.info(f"Админ {msg.from_user.full_name} ответил пользователю {user_id}: {msg.text}")
        # Write reply into Google Sheet if column exists
        header = sheet.row_values(1)
        all_rows = sheet.get_all_values()
        if "Ответ админа" not in header:
            await msg.reply("⚠️ В таблице нет столбца 'Ответ админа'")
            return
        reply_col = header.index("Ответ админа") + 1
        for idx, row in enumerate(reversed(all_rows[1:]), 1):
            row_index = len(all_rows) - idx + 1
            if str(user_id) == row[0] and (len(row) < reply_col or not row[reply_col - 1]):
                sheet.update_cell(row_index, reply_col, msg.text)
                break
    except Exception as e:
        await msg.reply(f"❌ Ошибка при отправке: {e}")

# === Register admin-related handlers ===
def register_admin(dp: Dispatcher):
    dp.register_callback_query_handler(handle_reply_button, lambda c: c.data.startswith("reply:"))
    dp.register_message_handler(ask_user_id, lambda m: m.text == "✍️ Написать по ID")
    dp.register_message_handler(handle_user_id_input, lambda m: m.from_user.id in admin_waiting_id_input)
    dp.register_message_handler(handle_admin_reply, lambda m: m.from_user.id in admin_reply_targets)


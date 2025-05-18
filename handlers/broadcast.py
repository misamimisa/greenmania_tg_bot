from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from config import ADMIN_IDS, bot, logger
from services.sheets import sheet
import asyncio

# Temporary state for admins who are about to send a broadcast
admin_waiting_broadcast = set()

# === Step 1: Admin presses "📢 Рассылка" ===
async def ask_broadcast_message(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    admin_waiting_broadcast.add(message.from_user.id)
    await message.answer("✉️ Введите сообщение, которое вы хотите отправить всем пользователям:")

# === Step 2: Admin types the message to broadcast ===
async def handle_broadcast_text(message: types.Message):
    admin_id = message.from_user.id
    if admin_id not in admin_waiting_broadcast:
        return  # Ignore messages from admins not in broadcast mode

    admin_waiting_broadcast.remove(admin_id)
    text = message.text
    await message.answer("🚀 Рассылка запущена...")

    # Extract all user IDs from the spreadsheet
    all_rows = sheet.get_all_values()
    user_ids = {int(row[0]) for row in all_rows[1:] if row[0].isdigit()}
    success, failed = 0, 0

    # Send the message to each user
    for uid in user_ids:
        try:
            await bot.send_message(uid, text)
            await asyncio.sleep(0.2)  # pause to avoid hitting Telegram rate limits
            success += 1
        except Exception as e:
            logger.warning(f"Не удалось отправить пользователю {uid}: {e}")
            failed += 1

    # Notify the admin of results
    await message.answer(f"✅ Рассылка завершена.\nУспешно: {success}\nОшибки: {failed}")

# Targeted broadcast to 1 user
async def handle_single_broadcast(callback_query: types.CallbackQuery):
    admin_id = callback_query.from_user.id
    if admin_id not in ADMIN_IDS:
        await callback_query.answer("⛔️ Нет доступа")
        return

    target_id = int(callback_query.data.split(":")[1])
    from state import admin_reply_targets
    admin_reply_targets[admin_id] = target_id  # Reuse reply_targets

    await bot.send_message(admin_id, f"✍️ Напишите сообщение для рассылки пользователю ID {target_id}")
    await callback_query.answer()

# === Register handlers ===
def register_broadcast(dp: Dispatcher):
    dp.register_message_handler(ask_broadcast_message, lambda m: m.text == "📢 Рассылка")
    dp.register_message_handler(ask_broadcast_message, commands=["broadcast"])
    dp.register_message_handler(handle_broadcast_text, lambda m: m.from_user.id in admin_waiting_broadcast)
    dp.register_callback_query_handler(handle_single_broadcast, Text(startswith="broadcast_one:"))
 

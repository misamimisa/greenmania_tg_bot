from aiogram import types
from aiogram.dispatcher import Dispatcher
from config import ADMIN_IDS, sheet
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# === Admin runs /users to list recent users ===
async def handle_users_command(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    all_rows = sheet.get_all_values()
    header = all_rows[0]

    seen_ids = set()
    latest_users = []

    # === Collect last known entry per unique user ID ===
    for row in reversed(all_rows[1:]):
        uid = row[0]
        if uid not in seen_ids:
            latest_users.append(row)
            seen_ids.add(uid)
        if len(latest_users) >= 10:  # limit to 10
            break

    if not latest_users:
        await message.reply("❗️Пользователей в базе пока нет.")
        return

    # === Format and send info per user ===
    for row in latest_users:
        uid = row[0]
        name = row[1] if len(row) > 1 else "-"
        username = row[2] if len(row) > 2 else "-"
        date = row[5] if len(row) > 5 else "-"
        action = row[6] if len(row) > 6 else "-"

        msg = (
            f"👤 <b>{name}</b> (ID: <code>{uid}</code>)\n"
            f"🔗 @{username}\n"
            f"🕒 Последнее: {date}\n"
            f"📌 Тип: {action}"
        )

        # === Add buttons to reply or broadcast to that user ===
        buttons = InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("🔁 Ответить", callback_data=f"reply:{uid}"),
            InlineKeyboardButton("📢 Рассылка", callback_data=f"broadcast_one:{uid}")
        )

        await message.answer(msg, parse_mode="HTML", reply_markup=buttons)

# === Register the command ===
def register_users(dp: Dispatcher):
    dp.register_message_handler(handle_users_command, commands=["users"])

from aiogram import types
from aiogram.dispatcher import Dispatcher
from config import ADMIN_IDS, sheet
from state import admin_waiting_info_input
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# === Called when admin presses "📋 Поиск клиента" button ===
async def trigger_info_prompt(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    # enter info-input mode
    admin_waiting_info_input.add(message.from_user.id)
    await message.answer("🔎 Введите ID, @username или имя пользователя для поиска:")

# === Handle text input when admin is in info-input mode ===
async def handle_info_input(message: types.Message):
    admin_id = message.from_user.id
    if admin_id not in admin_waiting_info_input:
        return  # ignore if not in info mode

    # exit info mode
    admin_waiting_info_input.remove(admin_id)

    query = message.text.strip()
    all_rows = sheet.get_all_values()
    header = all_rows[0]
    matched = []

    # === Search by ID, username, or name ===
    for row in all_rows[1:]:
        uid, name, username = row[0], row[1] if len(row)>1 else "", row[2] if len(row)>2 else ""
        if query.isdigit() and uid == query:
            matched.append(row)
        elif query.lstrip("@").lower() == username.lower():
            matched.append(row)
        elif query.lower() in name.lower():
            matched.append(row)

    if not matched:
        await message.reply(f"⚠️ Пользователь по запросу «{query}» не найден.")
        return

    # === Keep latest per user and show up to 3 ===
    seen, latest = set(), []
    for row in reversed(matched):
        if row[0] not in seen:
            latest.append(row)
            seen.add(row[0])
        if len(latest) >= 3:
            break

    # === Reply with info + buttons ===
    for row in latest:
        uid = row[0]
        nm = row[1] if len(row)>1 else "-"
        un = row[2] if len(row)>2 else "-"
        dt = row[5] if len(row)>5 else "-"
        tp = row[6] if len(row)>6 else "-"
        txt = row[4] if len(row)>4 else ""

        resp = (
            f"📄 Информация о пользователе ID {uid}:\n"
            f"👤 Имя: {nm}\n"
            f"🔗 Username: @{un}\n"
            f"🕒 Последнее действие: {dt}\n"
            f"📌 Тип действия: {tp}\n"
        )
        if txt:
            resp += f"💬 Сообщение: {txt}"

        # inline buttons: reply or broadcast to this user
        kb = InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("🔁 Ответить", callback_data=f"reply:{uid}"),
            InlineKeyboardButton("📢 Рассылка", callback_data=f"broadcast_one:{uid}")
        )
        await message.reply(resp, reply_markup=kb)

# === Also allow /info and /find commands ===
async def handle_info_command(message: types.Message):
    # reuse same logic as handle_info_input
    await handle_info_input(message)

# === Register handlers ===
def register_info(dp: Dispatcher):
    dp.register_message_handler(trigger_info_prompt, lambda m: m.text == "📋 Поиск клиента")
    dp.register_message_handler(handle_info_input, lambda m: m.from_user.id in admin_waiting_info_input)
    dp.register_message_handler(handle_info_command, commands=["info", "find"])

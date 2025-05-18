from aiogram import types

def get_restart_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("↩️ Вернуться в начало") 
    # keyboard.add("⛔️ Остановить бота")
    return keyboard

def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("📝 Записаться")
    keyboard.add("❓ Задать вопрос") 
    # keyboard.add("⛔️ Остановить бота")
    return keyboard

def get_admin_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # keyboard.add("📝 Записаться")
    # keyboard.add("❓ Задать вопрос")
    # keyboard.add("⛔️ Остановить бота")
    keyboard.add("📋 Поиск клиента")
    keyboard.add("✍️ Написать по ID")
    keyboard.add("📢 Рассылка") 
    return keyboard
# Greenmania Telegram Bot

Телеграм-бот для общения с клиентами салона Greenmania.

---

## 📦 Структура проекта

greenmania_bot/
├── main.py # точка входа
├── config.py # конфигурация, токен, логгер, sheets
├── keyboards.py # кнопки ReplyKeyboard
├── state.py # состояния пользователей
├── services/
│ └── sheets.py # работа с Google Sheets
└── handlers/
  ├── base.py # старт, стоп, возврат
  ├── booking.py # кнопка "Записаться"
  ├── question.py # кнопка "Задать вопрос"
  ├── admin.py # ответы администратора
  ├── info.py # для администратора
  ├── broadcast.py # рассылка по базе бота
  ├── users.py # база пользователей
  └── user_message.py # сообщения пользователя

---

## ⚙️ Настройка окружения

Создайте файл `.env` в корне и добавьте:

```env
BOT_TOKEN=ваш_токен_бота
ADMIN_IDS=123456789,987654321

ADMIN_IDS — список Telegram ID администраторов, разделённый запятыми.

📝 Требования
Python 3.10+

Установить зависимости:
pip install -r requirements.txt

🚀 Запуск

python main.py

📊 Логирование
Все события логируются в bot.log (ротация по дням)

В режиме DEBUG = True (в config.py) логи также видны в терминале

Старые логи удаляются автоматически

☁️ Google Sheets
Файл credentials.json должен лежать в корне проекта.
Он используется для записи данных клиентов в таблицу Google Sheets.


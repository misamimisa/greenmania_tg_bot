import os
import json
import logging
import glob
from logging.handlers import TimedRotatingFileHandler
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

# Debug mode flag
DEBUG = False

# Clear old logs if in debug
if DEBUG:
    for old_log in glob.glob("bot.log.*"):
        try:
            os.remove(old_log)
        except Exception as e:
            print(f"Could not remove {old_log}: {e}")

# === Logging setup ===
log_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s",
    "%Y-%m-%d %H:%M:%S"
)

# File handler with daily rotation
file_handler = TimedRotatingFileHandler(
    "bot.log", when="midnight", interval=1, backupCount=14, encoding="utf-8"
)
file_handler.setFormatter(log_formatter)
file_handler.suffix = "%Y-%m-%d"

logger = logging.getLogger()
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
logger.addHandler(file_handler)

# Console handler (always enabled)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

# === Google Sheets scope & credentials ===
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Try to load credentials from ENV; fallback to credentials.json
creds_json = os.getenv("GSPREAD_JSON")
if creds_json:
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

# Authorize and open sheet
client = gspread.authorize(creds)
sheet = client.open("ClientsFromBot").sheet1

# === Telegram bot setup ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
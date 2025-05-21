from datetime import datetime
from zoneinfo import ZoneInfo  # Use standard library for IANA timezones
from config import sheet

def append_to_sheet(user, text, status):
    # Use Moscow timezone for timestamp
    tz = ZoneInfo("Europe/Moscow")
    now = datetime.now(moscow_tz).strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([
        user.id,
        user.first_name or "",
        user.username or "",
        user.language_code or "",
        text,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        status
    ])

def get_all_user_ids():
    all_rows = sheet.get_all_values()
    return [row[0] for row in all_rows]
from datetime import datetime
import pytz  # Reliable tz DB
from config import sheet, logger

def append_to_sheet(user, text, status):
    # Use pytz for Moscow timezone
    moscow_tz = pytz.timezone("Europe/Moscow")
    now = datetime.now(moscow_tz)
    logger.info(f"[DEBUG] Moscow time in append_to_sheet: {now.isoformat()}")

    sheet.append_row([
        user.id,
        user.first_name or "",
        user.username or "",
        user.language_code or "",
        text,
        now.strftime("%Y-%m-%d %H:%M:%S"),
        status
    ])

def get_all_user_ids():
    all_rows = sheet.get_all_values()
    return [row[0] for row in all_rows]
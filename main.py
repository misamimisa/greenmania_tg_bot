from config import dp, logger
from aiogram import executor

# Import handler registration functions
from handlers.base import register_base
from handlers.booking import register_booking
from handlers.question import register_question
from handlers.admin import register_admin
from handlers.user_message import register_user_message
from handlers.broadcast import register_broadcast
from handlers.info import register_info
from handlers.users import register_users

def register_all_handlers():
    register_base(dp)
    register_booking(dp)
    register_question(dp)
    register_admin(dp)
    register_user_message(dp)
    register_broadcast(dp)
    register_info(dp)
    register_users(dp)
    
if __name__ == "__main__":
    logger.info("Бот запущен")
    register_all_handlers()
    executor.start_polling(dp, skip_updates=True)

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import FSInputFile
from datetime import datetime
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Замените на свой токен бота
BOT_TOKEN = '7718633799:AAFcPG4zM5NBsf4QmIivleABBZrI5gmk6ww'
# Замените на ID вашего канала (например: '@channel_name' или '-100...')
CHANNEL_ID = '-1002343077086'
# Путь к файлу, который нужно отправлять
FILE_PATH = 'users.db'

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()  # Изменено здесь


# Функция отправки файла
async def send_file():
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file = FSInputFile(FILE_PATH)  # Изменено здесь

        await bot.send_document(
            chat_id=CHANNEL_ID,
            document=file,
            caption=f"Scheduled file send at {current_time}"
        )
        logging.info(f"File sent successfully at {current_time}")

    except Exception as e:
        logging.error(f"Error sending file: {e}")


# Функция запуска бота
async def main():
    # Инициализация планировщика
    scheduler = AsyncIOScheduler()

    # Добавление задачи отправки файла каждый час
    scheduler.add_job(send_file, 'interval', hours=1)

    # Запуск планировщика
    scheduler.start()

    try:
        # Отправка первого файла при запуске
        await send_file()

        # Запуск бота и диспетчера
        await dp.start_polling(bot)

    except Exception as e:
        logging.error(f"Bot error: {e}")

    finally:
        await bot.session.close()


def start():
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")

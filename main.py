import asyncio

from aiogram import Bot, F, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton
from database import database
from keyboard import online, inline
from aiogram.methods import SendPhoto

token = "7374319690:AAHLXuN-98UqMqJD0ZAkcLlrCRsoeQuGO4E"

bot = Bot(token)
dp = Dispatcher()
db = database("users.db")

@dp.message(Command("start"))
async def start_message(message: Message):
    user = db.get_user_cursor(message.from_user.id)
    
    if user is None:
        db.new_user(message.from_user.id)
        await message.answer(
            "👥 Добро пожаловать в Анонимный Чат Бот!\n"
            "🗣 Наш бот предоставляет возможность анонимного общения.",
            #reply_markup = online.builder("🔎 Найти чат")
            reply_markup= InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Я девушка', callback_data='gender_female')],
                [InlineKeyboardButton(text='Я мужчинка', callback_data='gender_male')]
            ])
        )
    else:
        await message.answer(
            "👥 Добро пожаловать в Анонимный Чат Бот!\n\n"
            "Вы уже зарегистрированы!",
            #f"👁‍🗨 Людей в поиске: {db.get_users_in_search()}",
            reply_markup = online.builder("🔎 Найти чат")
        )

@dp.message(F.text == "🔎 Найти чат")
async def search_chat(message: Message):
    user = db.get_user_cursor(message.from_user.id)

    if user is not None:
        rival = db.search(message.from_user.id)

        if rival is None:
            await message.answer(
                "🔎 Вы начали поиск сорола...",
                #f"👁‍🗨 Людей в поиске: {db.get_users_in_search()}",
                reply_markup = online.builder("❌ Завершить поиск сорола")
            )
        else:
            db.start_chat(message.from_user.id, rival["id"])

            string = "✅ Игрок найден!\n"
            string += "Чтобы завершить диалог, нажмите \"❌ Завершить диалог\""

            await message.answer(string, reply_markup = online.builder("❌ Завершить диалог"))
            await bot.send_message(rival["id"], string, reply_markup = online.builder("❌ Завершить диалог"))

@dp.message(F.text == "❌ Завершить поиск сорола")
async def stop_search(message: Message):
    user = db.get_user_cursor(message.from_user.id)

    if user is not None:
        if user["status"] == 1:
            db.stop_search(message.from_user.id)

            await message.answer(
                "✅ Вы закончили поиск сорола",
                reply_markup = online.builder("🔎 Найти чат")
            )

@dp.message(F.text == "❌ Завершить диалог")
async def stop_chat(message: Message):
    user = db.get_user_cursor(message.from_user.id)

    if user is not None:
        if user["status"] == 2:
            db.stop_chat(message.from_user.id, user["rid"])

            await message.answer(
                "✅ Вы завершили диалог с соролом.\n\n"
                "Для того, чтобы найти чат, нажмите \"🔎 Найти чат\"",
                reply_markup = online.builder("🔎 Найти чат")
            )

            await bot.send_message(user["rid"],
                "❌ С вами завершили диалог.\n\n"
                "Для того, чтобы найти чат, нажмите \"🔎 Найти чат\"",
                reply_markup = online.builder("🔎 Найти чат")
            )

@dp.message()
async def handler_message(message: Message):
    user = db.get_user_cursor(message.from_user.id)

    #if int(user["age"]) != 0:
    if user is not None:
        if user["status"] != 0:
            if user["status"] == 2:
                # await bot.send_message(1371198599, str(message))
                if message.photo is not None:
                    await bot.send_photo(chat_id=user["rid"], photo=message.photo[-1].file_id,
                                         caption = message.caption)
                elif message.text is not None:
                    await bot.send_message(user["rid"], message.text)
                elif message.voice is not None:
                    await bot.send_audio(chat_id=user["rid"], audio=message.voice.file_id,
                                            caption = message.caption)
                elif message.video_note is not None:
                    await bot.send_video_note(chat_id=user["rid"], video_note=message.video_note.file_id)
                elif message.sticker is not None:
                    await bot.send_sticker(chat_id=user["rid"], sticker = message.sticker.file_id)
        else:
            if message.text.isdigit() and 0 < int(message.text) < 80:
                age = int(message.text)
                db.update_user_age(message.from_user.id, age)
                await message.answer(f"✅ Ваш возраст {age} лет сохранен. Теперь вы можете искать соролера!",
                                       reply_markup = online.builder("🔎 Найти чат"))
            else:
                await message.answer("❌ Пожалуйста, введите корректный возраст (число от 1 до 80).")

# @dp.message()
# async def handle_age_input(message: Message):
#     user = db.get_user_cursor(message.from_user.id)
#
#     if user is not None and "gender" in user:
#         if message.text.isdigit() and 0 < int(message.text) < 80:
#             age = int(message.text)
#             db.update_user_age(message.from_user.id, age)
#             await message.answer(f"✅ Ваш возраст {age} лет сохранен. Теперь вы можете искать соролера!",
#                                   reply_markup = online.builder("🔎 Найти чат"))
#         else:
#             await message.answer("❌ Пожалуйста, введите корректный возраст (число от 1 до 80).")
                
@dp.callback_query(F.data.startswith("gender_"))
async def handle_gender_selection(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    gender = callback_query.data.split("_")[1]

    db.update_user_gender(user_id, gender)

    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(user_id, f"Спасибо, что выбрали: {gender.capitalize()}.\nТеперь введите свой возраст:")

    await bot.send_message(user_id, "Пожалуйста, введите свой возраст:")

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())





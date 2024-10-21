import asyncio

from aiogram import Bot, F, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from database import database
from keyboard import online, inline
from aiogram.methods import SendPhoto

token = "7374319690:AAHLXuN-98UqMqJD0ZAkcLlrCRsoeQuGO4E"

bot = Bot(token)
dp = Dispatcher()
db = database("users.db")
link_text_news = "- Новостной канал проекта"
url_news = "https://t.me/RP_Anon_ChatBot_News"
link_text_TS = "Техническая поддержка"
url_TS = "https://t.me/TS_RP_Anon_ChatBot"
link_text_Tayova = "- Tayova"
url_Tayova = "https://t.me/tayovamask"

Tayova = 1095086092
Bes = 1978805110
Serjantov = 686803928
Capcha = 931442055

user_states = {}
referal_codes = ["Tayova19", "Добрый"]

@dp.message(Command("start"))
async def start_message(message: Message):
    user = db.get_user_cursor(message.from_user.id)
    idinty = message.from_user.id

    if user is None:
        db.new_user(message.from_user.id)
        await message.answer(
            "👥 Добро пожаловать в Чат-бот ролевиков!\n"
            "🗣 Наш бот предоставляет возможность поиска соролеров.\n\n"
            "📢 Следите за новостями проекта: \n"
            f'<a href="{url_news}">{link_text_news}</a>\n\n'
            f'- Если у вас возникли вопросы или нужна помощь, не стесняйтесь обращаться к нам!\n'
            f'📞 <a href="{url_TS}">{link_text_TS}</a>\n\n'
            "🤝 Партнёры проекта:\n\n"
            f'<a href="{url_Tayova}">{link_text_Tayova}</a>', parse_mode='HTML',
            #reply_markup = online.builder("🔎 Найти чат")
            reply_markup= InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Я девушка', callback_data='gender_female')],
                [InlineKeyboardButton(text='Я мужчина', callback_data='gender_male')]
            ])
        )
    else:
        await message.answer(
            "👥 Добро пожаловать в Чат-бот ролевиков!\n\n"
            "Вы уже зарегистрированы! 🎉\n\n"
            "📢 Следите за новостями проекта: \n"
            f'<a href="{url_news}">{link_text_news}</a>\n\n'
            f'- Если у вас возникли вопросы или нужна помощь, не стесняйтесь обращаться к нам!\n'
            f'📞 <a href="{url_TS}">{link_text_TS}</a>\n\n'
            "🤝 Партнёры проекта:\n\n"
            f'<a href="{url_Tayova}">{link_text_Tayova}</a>', parse_mode='HTML',
            #f"👁‍🗨 Людей в поиске: {db.get_users_in_search()}",
            #reply_markup = online.builder("🔎 Найти чат")
            reply_markup = get_main_keyboard(idinty)
        )

@dp.message(F.text == "Реферальный код")
async def referral_code(message: Message):
    await message.answer("🆔 Пожалуйста, введите реферальный код:", reply_markup = get_back_keyboard())
    user_states[message.from_user.id] = 'awaiting_referral_code'  # Устанавливаем состояние ожидающих кодов

@dp.message(F.text == "Назад")
async def referral_code(message: Message):
    idinty = message.from_user.id
    await message.answer("Главное меню", reply_markup = get_main_keyboard(idinty))

@dp.message(F.text == "🔎 Найти чат")
async def search_chat(message: Message):
    user = db.get_user_cursor(message.from_user.id)

    if user is not None:
        rival = db.search(message.from_user.id)

        if rival is None:
            await message.answer(
                "🔎 Вы начали поиск сорола...",
                #f"👁‍🗨 Людей в поиске: {db.get_users_in_search()}",
                reply_markup = get_search_keyboard()
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
    idinty = message.from_user.id

    if user is not None:
        if user["status"] == 1:
            db.stop_search(message.from_user.id)

            await message.answer(
                "✅ Вы закончили поиск сорола",
                reply_markup = get_main_keyboard(idinty)
            )

@dp.message(F.text == "❌ Завершить диалог")
async def stop_chat(message: Message):
    user = db.get_user_cursor(message.from_user.id)
    idinty = message.from_user.id

    if user is not None:
        if user["status"] == 2:
            db.stop_chat(message.from_user.id, user["rid"])

            await message.answer(
                "✅ Вы завершили диалог с соролом.\n\n"
                "Для того, чтобы найти чат, нажмите \"🔎 Найти чат\"",
                reply_markup = get_main_keyboard(idinty)
            )

            await bot.send_message(user["rid"],
                "❌ С вами завершили диалог.\n\n"
                "Для того, чтобы найти чат, нажмите \"🔎 Найти чат\"",
                reply_markup = get_main_keyboard(idinty)
            )

@dp.message(F.text == "Мои рефералы")
async def check_referral(message: Message):
    idinty = message.from_user.id
    if idinty == Tayova:
        count = db.count_referral('Tayova19')
        count = str(count)[1] #Вывод значения пришедших рефералов
        await message.answer(f"Кол-во приведённых рефералов {count}", reply_markup = get_main_keyboard(idinty))
    elif idinty == Capcha:
        count = db.count_referral('Добрый')
        count = str(count)[1]
        await message.answer(f"Кол-во приведённых рефералов {count}", reply_markup=get_main_keyboard(idinty))
    elif idinty == Bes or idinty == Serjantov:
        TayovaCount = db.count_referral('Tayova19')
        TayovaCount = str(TayovaCount)[1]
        idTayovaRef = db.print_users_by_referral("Tayova19")
        CapchaCount = db.count_referral('Добрый')
        CapchaCount = str(CapchaCount)[1]
        idCapchaRef = db.print_users_by_referral("Добрый")
        await message.answer(f"Кол-во приведённых рефералов по коду Tayova19: {TayovaCount}\n"
                             f"Их id: {idTayovaRef}\n"
                             f"Кол-во приведённых рефералов по коду Добрый: {CapchaCount}\n"
                             f"Их id: {idCapchaRef}", reply_markup = get_main_keyboard(idinty))

@dp.message()
async def handler_message(message: Message):
    user = db.get_user_cursor(message.from_user.id)
    idinty = message.from_user.id
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
        elif db.check_user_age(message.from_user.id) == 0:
            if message.text.isdigit() and 0 < int(message.text) < 80:
                age = int(message.text)
                db.update_user_age(message.from_user.id, age)
                await message.answer(f"✅ Ваш возраст {age} лет сохранен. Теперь вы можете искать соролера!",
                                       reply_markup = get_main_keyboard(idinty))
            else:
                await message.answer("❌ Пожалуйста, введите корректный возраст (число от 1 до 80).")
        elif user_states.get(idinty) == 'awaiting_referral_code':
            referral_code = message.text.strip()  # Получаем текст сообщения
            if referral_code in referal_codes:
                db.update_user_referral(message.from_user.id, referral_code)
                await message.answer(f"✅ Реферальный код '{referral_code}' успешно обработан!", reply_markup = get_main_keyboard(idinty))

                # Очищаем состояние после обработки кода
                del user_states[idinty]
            else:
                await message.answer(f"❌ Реферальный код '{referral_code}' отсутствует!", reply_markup = get_main_keyboard(idinty))

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
    if gender.capitalize() == "Male":
        await bot.send_message(user_id, "Ваш пол мужской.\nТеперь введите свой возраст:")
    else: await bot.send_message(user_id, "Ваш пол женский.\nТеперь введите свой возраст:")

    await bot.send_message(user_id, "Пожалуйста, введите свой возраст:")

def get_main_keyboard(idinty):
    print(idinty)
    if idinty == Tayova or idinty == Bes or idinty == Serjantov:
        builder = ReplyKeyboardBuilder()
        builder.button(text = "🔎 Найти чат")
        builder.button(text = "Мои рефералы")
        return builder.as_markup(resize_keyboard=True)
    elif db.check_user_referral(idinty) == None:
        builder = ReplyKeyboardBuilder()
        builder.button(text = "🔎 Найти чат")
        builder.button(text = "Реферальный код")
        return builder.as_markup(resize_keyboard=True)
    else:
        builder = ReplyKeyboardBuilder()
        builder.button(text = "🔎 Найти чат")
        return builder.as_markup(resize_keyboard=True)

def get_back_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text = "Назад")
    return builder.as_markup(resize_keyboard=True)

def get_search_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Завершить поиск сорола")
    return builder.as_markup(resize_keyboard=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
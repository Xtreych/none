import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from aiogram import Bot, F, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database import database
from aiogram.methods import SendPhoto

import keyboard
import generator_scenary

from theme import get_themes_for_genre
from theme import get_full_theme_description

token = "2079887601:AAEvAOrx9696k0CVgL2SOTz_Cb5_O5qBoTo"

bot = Bot(token)
dp = Dispatcher()
db = database("users.db")
thread_pool = ThreadPoolExecutor(max_workers=100)  # Создаем пул потоков

link_text_news = "- Новостной канал проекта"
url_news = "https://t.me/RP_Anon_ChatBot_News"
link_text_TS = "Техническая поддержка"
url_TS = "https://t.me/TS_RP_Anon_ChatBot"
link_text_Tayova = "- Tayova"
url_Tayova = "https://t.me/tayovamask"

#Администрация
Bes = 1978805110

user_states = {}


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
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
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
            reply_markup=get_main_keyboard(idinty)
        )


@dp.message(F.text == "Реферальный код")
async def referral_code_request(message: Message):
    user_id = message.from_user.id
    owned_codes = db.get_user_referral_codes(user_id)

    if owned_codes:
        # Если пользователь владелец кода, показываем статистику
        response = "📊 Ваша реферальная статистика:\n\n"
        for code in owned_codes:
            count = db.count_referral(code[0])  # code[0], так как execute возвращает кортежи
            count = str(count)
            cleaned_count = re.sub(r"[(),]", "", count)
            response += f"Код: {code[0]}\n"
            response += f"Количество приглашенных: {cleaned_count}\n\n"

        await message.answer(
            response,
            reply_markup=get_main_keyboard(user_id)
        )
    else:
        # Если обычный пользователь, предлагаем ввести код
        await message.answer(
            "🆔 Пожалуйста, введите реферальный код:",
            reply_markup=keyboard.get_back_keyboard()
        )
        user_states[message.from_user.id] = 'awaiting_referral_code'

@dp.message(F.text == "👨‍💼 Админ-панель")
async def open_admin_panel(message: Message):
    if db.is_admin(message.from_user.id):
        await message.answer(
            "👨‍💼 Панель администратора\n\n"
            "Выберите действие:",
            reply_markup=keyboard.get_admin_keyboard()
        )

@dp.callback_query(F.data == "add_ref_code")
async def add_ref_code_start(callback: CallbackQuery):
    if not db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора!", show_alert=True)
        return

    user_states[callback.from_user.id] = "waiting_ref_code"
    await callback.message.edit_text(
        "Введите новый реферальный код и ID владельца в формате:\n"
        "код ID\n"
        "Например: Tayova19 1095086092",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Отмена", callback_data="back_to_admin")]
        ])
    )

@dp.callback_query(F.data == "remove_ref_code")
async def remove_ref_code_start(callback: CallbackQuery):
    if not db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора!", show_alert=True)
        return

    codes = db.get_all_referral_codes()
    keyboard = []
    for code, owner_id in codes:
        keyboard.append([InlineKeyboardButton(
            text=f"❌ {code} (ID: {owner_id})",
            callback_data=f"del_ref_{code}"
        )])
    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin")])

    await callback.message.edit_text(
        "Выберите код для удаления:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@dp.callback_query(F.data.startswith("del_ref_"))
async def remove_ref_code(callback: CallbackQuery):
    if not db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора!", show_alert=True)
        return

    code = callback.data.split("_")[2]
    if db.remove_referral_code(code):
        await callback.answer("✅ Код успешно удален!")
    else:
        await callback.answer("❌ Ошибка при удалении кода!")

    await callback.message.edit_text(
        "👨‍💼 Панель администратора",
        reply_markup=keyboard.get_admin_keyboard()
    )

@dp.callback_query(F.data == "manage_admins")
async def manage_admins(callback: CallbackQuery):
    if callback.from_user.id != Bes:
        await callback.answer("Только главный администратор может управлять администраторами!", show_alert=True)
        return

    await callback.message.edit_text(
        "Управление администраторами:",
        reply_markup=keyboard.get_manage_admins_keyboard()
    )

@dp.callback_query(F.data == "add_admin")
async def add_admin_start(callback: CallbackQuery):
    if callback.from_user.id != Bes:
        await callback.answer("Только главный администратор может добавлять администраторов!", show_alert=True)
        return

    user_states[callback.from_user.id] = "waiting_admin_id"
    await callback.message.edit_text(
        "Введите ID нового администратора:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Отмена", callback_data="back_to_admin")]
        ])
    )

@dp.callback_query(F.data == "ref_stats")
async def show_ref_stats(callback: CallbackQuery):
    user_id = callback.from_user.id

    if db.is_admin(user_id):
        all_codes = db.get_all_referral_codes()
        response = "📊 Статистика реферальных кодов:\n\n"

        for code, owner_id in all_codes:
            users = db.print_users_by_referral(code)
            count = len(users) if users else 0
            response += f"Код: {code}\nВладелец ID: {owner_id}\n"
            response += f"Использований: {count}\n"
            response += f"ID пользователей: {users}\n\n"
    else:
        all_codes = db.get_all_referral_codes()
        response = "📊 Ваша реферальная статистика:\n\n"

        for code, owner_id in all_codes:
            if owner_id == user_id:
                count = db.count_referral(code)
                response += f"Код: {code}\n"
                response += f"Приглашено: {count}\n\n"

    await callback.message.edit_text(
        response,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin")]
        ])
    )

@dp.message(F.text == "Назад")
async def referral_code(message: Message):
    idinty = message.from_user.id
    await message.answer("Главное меню", reply_markup=get_main_keyboard(idinty))


@dp.message(F.text == "🔎 Найти чат")
async def search_chat(message: Message):
    user = db.get_user_cursor(message.from_user.id)

    if user is not None:
        rival = db.search(message.from_user.id)

        if rival is None:
            await message.answer(
                "🔎 Вы начали поиск сорола...",
                reply_markup=keyboard.get_search_keyboard()
            )
        else:
            db.start_chat(message.from_user.id, rival["id"])

            string = "✅ Игрок найден!\n"
            string += "Чтобы завершить диалог, нажмите \"❌ Завершить диалог\""

            await message.answer(string, reply_markup=keyboard.get_cancel_keyboard())
            await bot.send_message(rival["id"], string, reply_markup=keyboard.get_cancel_keyboard())


@dp.message(F.text == "Сценарий")
async def check_referral(message: Message):
    await message.answer(
        "Выберите жанр сценария:",
        reply_markup=keyboard.get_genre_keyboard()
    )

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

@dp.callback_query(F.data.startswith("genre_"))
async def handle_genre_selection(callback_query: CallbackQuery):
    genre = callback_query.data.split("_")[1]
    genre_names = {
        "post": "Постапокалипсис",
        "romance": "Романтика",
        "cyber": "Киберпанк",
        "fantasy": "Фэнтези",
        "mystic": "Мистика",
        "history": "Историческая",
        "scifi": "Научная Фантастика",
        "horror": "Хоррор",
        "super": "Супергероика",
        "terror": "Ужасы",
        "detective": "Детектив",
        "dystopia": "Дисутопия"
    }

    selected_genre = genre_names.get(genre, "Неизвестный жанр")
    await callback_query.message.edit_text(
        f"Вы выбрали жанр: {selected_genre}\nТеперь выберите тему:",
        reply_markup=keyboard.get_theme_keyboard(genre)
    )


@dp.callback_query(F.data.startswith("theme_"))
async def handle_theme_selection(callback_query: CallbackQuery):
    theme_data = callback_query.data.split("_")
    genre = theme_data[1]
    theme_number = int(theme_data[2])
    user_id = callback_query.from_user.id

    # Получаем информацию о пользователе
    user = db.get_user_cursor(user_id)

    full_theme = get_full_theme_description(genre, theme_number)

    # Отправляем сообщение о начале генерации обоим пользователям
    await callback_query.message.edit_text(
        "⏳ Генерирую сценарий... Пожалуйста, подождите.",
        reply_markup=None
    )

    if user and user["status"] == 2 and user["rid"] != 0:
        await bot.send_message(
            user["rid"],
            "⏳ Ваш собеседник генерирует сценарий... Пожалуйста, подождите."
        )

    try:
        # Выполняем генерацию сценария в отдельном потоке
        scenario = await asyncio.get_event_loop().run_in_executor(
            thread_pool,
            generator_scenary.main,
            genre,
            full_theme
        )

        # Отправляем сценарий инициатору
        await callback_query.message.edit_text(
            f"Ваш сценарий:\n\n{scenario}"
        )

        # Если пользователь в чате с кем-то, отправляем сценарий и собеседнику
        if user and user["status"] == 2 and user["rid"] != 0:
            await bot.send_message(
                user["rid"],
                f"⏳ Ваш собеседник сгенерировал сценарий:\n\n{scenario}"
            )

    except Exception as e:
        error_message = "❌ Произошла ошибка при генерации сценария. Пожалуйста, попробуйте еще раз."
        print(f"Error generating scenario: {e}")

        # Отправляем сообщение об ошибке инициатору
        await callback_query.message.edit_text(
            error_message,
            reply_markup=keyboard.get_genre_keyboard()
        )

        # Если пользователь в чате с кем-то, отправляем сообщение об ошибке и собеседнику
        if user and user["status"] == 2 and user["rid"] != 0:
            await bot.send_message(
                user["rid"],
                error_message,
                reply_markup=keyboard.get_genre_keyboard()
            )


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

@dp.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery):
    await callback.message.edit_text(
        "👨‍💼 Панель администратора\n\n"
        "Выберите действие:",
        reply_markup=keyboard.get_admin_keyboard()
    )

@dp.callback_query(F.data == "remove_admin")
async def remove_admin_start(callback: CallbackQuery):
    if callback.from_user.id != Bes:
        await callback.answer("Только главный администратор может удалять администраторов!",
                              show_alert=True)
        return

    admins = db.get_admin_list()
    keyboard = []
    for admin_id in admins:
        if admin_id[0] != Bes:  # Не показываем главного администратора
            keyboard.append([InlineKeyboardButton(
                text=f"❌ Админ ID: {admin_id[0]}",
                callback_data=f"del_admin_{admin_id[0]}"
            )])
    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin")])

    await callback.message.edit_text(
        "Выберите администратора для удаления:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@dp.callback_query(F.data.startswith("del_admin_"))
async def remove_admin_confirm(callback: CallbackQuery):
    if callback.from_user.id != Bes:
        await callback.answer("Только главный администратор может удалять администраторов!",
                              show_alert=True)
        return

    admin_id = int(callback.data.split("_")[2])
    if db.remove_admin(admin_id):
        await callback.answer("✅ Администратор успешно удален!")
    else:
        await callback.answer("❌ Ошибка при удалении администратора!")

    await callback.message.edit_text(
        "👨‍💼 Панель администратора",
        reply_markup=keyboard.get_admin_keyboard()
    )

# Обработчик для проверки введенного реферального кода
async def handle_referral_input(message: Message):
    code = message.text.strip()
    owner_id = db.get_referral_code_owner(code)

    if owner_id is not None:
        db.update_user_referral(message.from_user.id, code)
        await message.answer(
            "✅ Реферальный код успешно применён!",
            reply_markup=get_main_keyboard(message.from_user.id)
        )
    else:
        await message.answer(
            "❌ Неверный реферальный код!",
            reply_markup=get_main_keyboard(message.from_user.id)
        )
    user_states[message.from_user.id] = None

# Добавим обработчик для проверки статуса пользователя
@dp.callback_query(F.data == "check_status")
async def check_user_status(callback: CallbackQuery):
    user_id = callback.from_user.id
    if db.is_admin(user_id):
        await callback.answer("Вы являетесь администратором!", show_alert=True)
    else:
        await callback.answer("Вы обычный пользователь", show_alert=True)

@dp.message()
async def handler_message(message: Message):
    user = db.get_user_cursor(message.from_user.id)
    idinty = message.from_user.id
    state = user_states.get(message.from_user.id)

    if user is not None:
        if user["status"] != 0:
            if user["status"] == 2:
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
        if state == "waiting_ref_code":
            try:
                code, owner_id = message.text.split()
                owner_id = int(owner_id)
                if db.add_referral_code(code, owner_id):
                    await message.answer("✅ Реферальный код успешно добавлен!")
                else:
                    await message.answer("❌ Ошибка при добавлении кода!")
            except:
                await message.answer("❌ Неверный формат! Используйте: код ID")

            user_states[message.from_user.id] = None
            await message.answer(
                "Панель администратора",
                reply_markup=keyboard.get_admin_keyboard()
            )
        elif state == "waiting_admin_id":
            try:
                new_admin_id = int(message.text)
                if db.add_admin(new_admin_id):
                    await message.answer(f"✅ Администратор (ID: {new_admin_id}) успешно добавлен!")
                else:
                    await message.answer("❌ Ошибка при добавлении администратора!")
            except:
                await message.answer("❌ Неверный формат ID!")

            user_states[message.from_user.id] = None
            await message.answer(
                "Панель администратора",
                reply_markup=keyboard.get_admin_keyboard()
            )
        elif state == "awaiting_referral_code":
            await handle_referral_input(message)

def get_main_keyboard(user_id):
    buttons = []
    buttons.append([KeyboardButton(text="🔎 Найти чат")])

    if not db.check_user_referral(user_id) and not db.is_admin(user_id):
        buttons.append([KeyboardButton(text="Реферальный код")])

    if db.is_admin(user_id):
        buttons.append([KeyboardButton(text="👨‍💼 Админ-панель")])

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
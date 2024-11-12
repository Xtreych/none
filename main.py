import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from aiogram import Bot, F, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardMarkup
from database import database
from aiogram.exceptions import TelegramBadRequest

import keyboard
import generator_scenary
import backup

from theme import get_full_theme_description

atoken = input("Какой токен используем?\n"
      "1 - тест-бот\n"
      "2 - основной бот\n")

if atoken == "1":
    token = "2079887601:AAEvAOrx9696k0CVgL2SOTz_Cb5_O5qBoTo"
else:
    token = "7374319690:AAHLXuN-98UqMqJD0ZAkcLlrCRsoeQuGO4E"

aexecutor = input("Бекап запускать?\n"
                  "1 - не запускать\n"
                  "2 - запускать\n")

bot = Bot(token)
dp = Dispatcher()
db = database("users.db")
thread_pool = ThreadPoolExecutor(max_workers=100)  # Создаем пул потоков
executor = ThreadPoolExecutor(max_workers=2)

if aexecutor != "1":
    backup_future = executor.submit(backup.start)

link_text_news = "- Новостной канал проекта"
url_news = "https://t.me/RP_Anon_ChatBot_News"
link_text_TS = "Техническая поддержка"
url_TS = "https://t.me/TS_RP_Anon_ChatBot"
link_text_Tayova = "- Tayova"
url_Tayova = "https://t.me/tayovamask"

#Администрация
Bes = 1978805110
Besovskaya = 1171214769
Serj = 686803928

user_states = {}

# Функция для проверки блокировки и отправки сообщения
async def check_user_block(user_id: int, message: Message = None, callback: CallbackQuery = None) -> bool:
    is_blocked, reason = db.is_user_blocked(user_id)
    if is_blocked:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ℹ️ Информация о блокировке", callback_data="block_info")]
        ])
        
        text = "⛔️ Ваш аккаунт заблокирован.\nНажмите кнопку ниже для получения информации о блокировке."
        
        if message:
            await message.answer(text, reply_markup=keyboard)
        elif callback:
            await callback.message.edit_text(text, reply_markup=keyboard)
            
        return True
    return False

# Обработчик информации о блокировке
@dp.callback_query(F.data == "block_info")
async def show_block_info(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_blocked, reason = db.is_user_blocked(user_id)
    
    if not is_blocked:
        await callback.message.edit_text(
            "✅ Ваш аккаунт не заблокирован.",
            reply_markup=get_main_keyboard(user_id)
        )
        return

    block_info = db.get_block_info(user_id)
    if not block_info:
        await callback.answer("Ошибка получения информации о блокировке", show_alert=True)
        return

    blocked_until, reason, complaint_id = block_info
    
    # Вычисляем оставшееся время с учетом часового пояса
    current_time = datetime.now()
    block_until = datetime.strptime(blocked_until, '%Y-%m-%d %H:%M:%S')
    time_left = block_until - current_time
    
    # Округляем время до ближайшей минуты
    total_minutes = int(time_left.total_seconds() / 60)
    hours_left = total_minutes // 60
    minutes_left = total_minutes % 60

    message_text = (
        f"⛔️ Информация о блокировке:\n\n"
        f"📝 Причина: {reason}\n"
        f"🔢 Номер жалобы: #{complaint_id if complaint_id else 'Н/Д'}\n"
        f"⏳ Осталось времени: {hours_left}ч {minutes_left}мин\n"
        f"📅 Разблокировка: {block_until.strftime('%d.%m.%Y %H:%M')}"
    )

    try:
        await callback.message.edit_text(
            message_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Обновить", callback_data="block_info")]
            ])
        )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await callback.answer("Информация актуальна", show_alert=True)

@dp.message(Command("start"))
async def start_message(message: Message):
    user = db.get_user_cursor(message.from_user.id)
    idinty = message.from_user.id
    if await check_user_block(message.from_user.id, message=message):
        return
    elif user is None:
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
        response = "📊 Ваша реферальная статисика:\n\n"
        for code in owned_codes:
            count = db.count_referral(code[0])  # code[0], так как execute возвращае кортежи
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
            "�� Пожалуйста, введите реферальный код:",
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
        await callback.answer("У вас нет прав администраора!", show_alert=True)
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
    if callback.from_user.id not in [Bes, Besovskaya, Serj]:
        await callback.answer("Только главный администратор может управлять адмнистраторами!", show_alert=True)
        return

    await callback.message.edit_text(
        "Управление администраторами:",
        reply_markup=keyboard.get_manage_admins_keyboard()
    )

@dp.callback_query(F.data == "add_admin")
async def add_admin_start(callback: CallbackQuery):
    if callback.from_user.id not in [Bes, Besovskaya, Serj]:
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
        response = "📊 Ваша рефральная сттсика:\n\n"

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
    # Проверяем блокировку
    is_blocked, reason = db.is_user_blocked(message.from_user.id)
    user = db.get_user_cursor(message.from_user.id)

    if user is not None:
        if is_blocked:
            await message.answer(
                f"❌ Вы заблокированы!\nПричина: {reason}\n"
                "Попробуйте позже."
            )
            return
        elif user["status"] == 0:  # Проверяем, что пользователь не в поиске и не в чате
            rival = db.search(message.from_user.id)

            if rival is None:
                await message.answer(
                    "🔎 Вы начали поиск сорола...",
                    reply_markup=keyboard.get_search_keyboard()
                )
            else:
                # Отправляем сообщение обоим пользователям
                string = "✅ Игрок найден!\n"
                string += "Чтобы завершить диалог, нажм��те \"❌ Завершить диалог\""

                await message.answer(string, reply_markup=keyboard.get_cancel_keyboard())
                try:
                    await bot.send_message(rival["id"], string, reply_markup=keyboard.get_cancel_keyboard())
                except Exception as e:
                    print(f"Error sending message to rival: {e}")
                    # озможно, стоит откатить соединение, если сообщение не удалось отправить
                    db.stop_chat(message.from_user.id, rival["id"])
                    await message.answer("Произошла ошибка при подключении к собеседнику. Попробуйте еще раз.")
        else:
            await message.answer("Вы уже находитесь в поиске или чате!")
    else:
        await message.answer("Произошла ошибка. Попробуйте позже.")


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
        "super": "Сугероика",
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

    # Получаем информацию о пользоватее
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
                f"⏳ Ва собеседник сгенеривал сценарий:\n\n{scenario}"
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

    if user is not None and user["status"] == 2 and user["rid"] != 0:
        rival_id = user["rid"]

        print(f"Debug: Stopping chat between {idinty} and {rival_id}")

        # Проверяем данные перед обновлением
        before_update = db.database.execute(
            "SELECT id, status, rid FROM users WHERE id IN (?, ?)",
            (idinty, rival_id)
        )
        print(f"Debug: Before update - Users data: {before_update}")

        # Останавливаем чат
        success = db.stop_chat(idinty, rival_id)

        if success:
            # Проверяем данные после обновления
            after_update = db.database.execute(
                "SELECT id, status, rid FROM users WHERE id IN (?, ?)",
                (idinty, rival_id)
            )
            print(f"Debug: After update - Users data: {after_update}")

            await message.answer(
                "✅ Вы завершили диалог с соролом.\n\n"
                "Для того, чтобы найти чат, нажмите \"🔎 Найти чат\"",
                reply_markup=get_main_keyboard(idinty)
            )

            try:
                await bot.send_message(
                    rival_id,
                    "❌ С вами завершили диалог.\n\n"
                    "Для того, чтобы найти чат, нажмите \"🔎 Найти чат\"",
                    reply_markup=get_main_keyboard(rival_id)
                )
            except Exception as e:
                print(f"Error sending message to rival: {e}")
        else:
            await message.answer(
                "Произошла ошибка при завершении диалога. Пожалуйста, попробуйте еще раз."
            )

@dp.message(F.text == "⚙️ Параметры поиска")
async def parameters(message: Message):

    await message.answer(
        "⚙️ Настройки поиска:\n\n"
        "Выберите параметры для поиска собеседника:",
        reply_markup=keyboard.get_selected_parameters_keyboard()
    )


@dp.callback_query(F.data == "set_preferred_gender")
async def set_preferred_gender(callback: CallbackQuery):

    await callback.message.edit_text(
        "Выберите предпочитаемый пол собеседника:",
        reply_markup=keyboard.get_gender_choose_keyboard()
    )


@dp.callback_query(F.data == "set_age_range")
async def set_age_range(callback: CallbackQuery):
    user_states[callback.from_user.id] = "waiting_min_age"
    await callback.message.edit_text(
        "Введите минимальный возраст (или введите 0 для любого возраста):"
    )


@dp.callback_query(F.data.startswith("pref_gender_"))
async def handle_preferred_gender(callback: CallbackQuery):
    gender = callback.data.split("_")[2]
    db.update_search_preferences(callback.from_user.id, preferred_gender=gender)

    await callback.answer("Предпочитаемый пол успешно установлен!")
    await callback.message.edit_text(
        f"✅ Установлен предпочитаемый пол: {'Любой' if gender == 'any' else 'Мужской' if gender == 'male' else 'Женский'}"
    )

@dp.callback_query(F.data.startswith("reset_preferences"))
async def set_reset_preferences(callback: CallbackQuery):
    user_id = callback.from_user.id
    db.update_search_preferences(user_id, min_age=0)
    db.update_search_preferences(user_id, max_age=0)
    db.update_search_preferences(callback.from_user.id, preferred_gender='any')
    await callback.message.edit_text(
        "✅ Настройки сбошены"
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
    if callback.from_user.id not in [Bes, Besovskaya, Serj]:
        await callback.answer("То��ько главный администратор может удалять администраторов!",
                              show_alert=True)
        return

    admins = db.get_admin_list()
    keyboard = []
    protected_admins = [Bes, Besovskaya, Serj]  # список защищенных администраторов

    for admin_id in admins:
        if admin_id[0] not in protected_admins:  # проверяем, не входит ли админ в список защищенных
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
    if callback.from_user.id not in [Bes, Besovskaya, Serj]:
        await callback.answer("Только главный администратор может удалять адмнистраторов!",
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

# Обработчик для проверки введенного реферального код
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

# Об
@dp.callback_query(F.data == "check_status")
async def check_user_status(callback: CallbackQuery):
    user_id = callback.from_user.id
    if db.is_admin(user_id):
        await callback.answer("Вы являетесь администратором!", show_alert=True)
    else:
        await callback.answer("Вы обычный пользователь", show_alert=True)

#Об
@dp.message(F.text == "⚠️ Пожаловаться")
async def handle_complaint(message: Message):
    user = db.get_user_cursor(message.from_user.id)
    
    if user and user["status"] == 2 and user["rid"] != 0:
        user_states[message.from_user.id] = "awaiting_complaint"
        await message.answer(
            "📝 Опишите причину жалобы на пльзоватея:",
            reply_markup=keyboard.get_back_keyboard()
        )
    else:
        await message.answer(
            "❌ Вы можете отправить жалобу только во время активного диалога.",
            reply_markup=get_main_keyboard(message.from_user.id)
        )

@dp.message()
async def handler_message(message: Message):
    user = db.get_user_cursor(message.from_user.id)
    idinty = message.from_user.id
    state = user_states.get(message.from_user.id)

    if await check_user_block(message.from_user.id, message=message):
        return

    if state and state.startswith("awaiting_block_hours_"):
        try:
            hours = int(message.text)
            if 1 <= hours <= 168:  # Проверяем, что часы в допустимом диапазоне
                complaint_id = int(state.split('_')[-1])
                
                # Получаем информацию о жалобе
                complaints = db.get_pending_complaints()
                complaint = next((c for c in complaints if c[0] == complaint_id), None)
                
                if complaint:
                    against_user = complaint[2]
                    # Блокируем пользователя
                    if db.block_user(against_user, hours, f"Заблокирован по жалобе #{complaint_id}"):
                        # Обновляем статус жалобы
                        db.update_complaint_status(complaint_id, "approved", f"Пользователь заблокирован на {hours} часов")
                        await message.answer(f"✅ Пользователь заблокирован на {hours} часов")
                    else:
                        await message.answer("❌ Ошибка при блокировке пользователя")
                else:
                    await message.answer("❌ Жалоба не найдена")
            else:
                await message.answer("❌ Пожалуйста, введите число от 1 до 168 (часов)")
        except ValueError:
            await message.answer("❌ Пожалуйст��, введите корректное число часов")
        
        user_states[message.from_user.id] = None
        await message.answer(
            "Панель администратора",
            reply_markup=keyboard.get_admin_keyboard()
        )

    if user is not None:
        if user["status"] == 2 and user["rid"] != 0:
            if state == "awaiting_complaint":
                if db.add_complaint(message.from_user.id, user["rid"], message.text):
                    await message.answer(
                        "✅ Жалоба отправлена администрации.",
                        reply_markup=keyboard.get_cancel_keyboard()
                    )
                else:
                    await message.answer(
                        "❌ Произошла ошибка при отправке жалобы.",
                        reply_markup=keyboard.get_cancel_keyboard()
                    )
                user_states[message.from_user.id] = None
                return
            
            try:
                # Сохраняем текстовое сообщение
                if message.text and not state:
                    db.save_message(message.from_user.id, user["rid"], message.text)
                    await bot.send_message(
                        chat_id=user["rid"],
                        text=message.text
                    )
                # Для фото сохраняем caption или пометку [Photo]
                elif message.photo:
                    caption = message.caption if message.caption else "[Photo]"
                    db.save_message(message.from_user.id, user["rid"], caption)
                    await bot.send_photo(
                        chat_id=user["rid"],
                        photo=message.photo[-1].file_id,
                        caption=caption
                    )
                # Для голосовых сообщений
                elif message.voice:
                    db.save_message(message.from_user.id, user["rid"], "[Voice message]")
                    await bot.send_voice(
                        chat_id=user["rid"],
                        voice=message.voice.file_id
                    )
                # Для видео-кружков
                elif message.video_note:
                    db.save_message(message.from_user.id, user["rid"], "[Video note]")
                    await bot.send_video_note(
                        chat_id=user["rid"],
                        video_note=message.video_note.file_id
                    )
                # Для стикеров
                elif message.sticker:
                    db.save_message(message.from_user.id, user["rid"], "[Sticker]")
                    await bot.send_sticker(
                        chat_id=user["rid"],
                        sticker=message.sticker.file_id
                    )
            except Exception as e:
                print(f"Error sending message: {e}")
                await message.answer(
                    "❌ Оибка при отправке сообщения. Возможно, собеседник покинул чат.",
                    reply_markup=get_main_keyboard(idinty)
                )
                db.stop_chat(message.from_user.id, user["rid"])
                return

        elif state == "waiting_ref_code":
            try:
                code, owner_id = message.text.split()
                owner_id = int(owner_id)
                if db.add_referral_code(code, owner_id):
                    await message.answer("✅ Реферальный код успешно добавлен!")
                else:
                    await message.answer("❌ Ошибка при добавлении кода!")
            except:
                await message.answer("❌ Неерный формат! Используйте: код ID")

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
                    await message.answer("Ошибк при добавлении администратора!")
            except:
                await message.answer("❌ Неверный формат ID!")

            user_states[message.from_user.id] = None
            await message.answer(
                "Панель администратора",
                reply_markup=keyboard.get_admin_keyboard()
            )

        # Обработка остальных состояний
        elif state == "waiting_min_age":
            if message.text.isdigit() and 0 <= int(message.text) <= 100:
                min_age = int(message.text)
                user_states[idinty] = "waiting_max_age"
                db.update_search_preferences(idinty, min_age=min_age)
                await message.answer("Теперь введите максимальный возраст:")
            else:
                await message.answer("Пожалуйста, введите корректный возраст (0-100)")

        elif state == "waiting_max_age":
            if message.text.isdigit() and 0 <= int(message.text) <= 100:
                max_age = int(message.text)
                min_age = db.get_search_preferences(idinty)["min_age"]

                if max_age >= min_age:
                    db.update_search_preferences(idinty, max_age=max_age)
                    user_states[idinty] = None
                    await message.answer(
                        f"✅ Возрастной диапазон установлен: {min_age}-{max_age} лет",
                        reply_markup=get_main_keyboard(idinty)
                    )
                else:
                    await message.answer("Максимальный возраст должен быть больше минимального")
            else:
                await message.answer("Пожалуйста, введите корректный возраст (0-100)")

        # Проверка возраста при регистрации
        elif db.check_user_age(message.from_user.id) == 0:
            if message.text.isdigit() and 0 < int(message.text) < 80:
                age = int(message.text)
                db.update_user_age(message.from_user.id, age)
                await message.answer(
                    f"✅ Ваш возраст {age} лет сохранен. Теперь вы можете искать соролера!",
                    reply_markup=get_main_keyboard(idinty)
                )
            else:
                await message.answer("Пожалуйста, введите корректный возраст (1-79)")

        # Обработка реерального кода
        elif state == "awaiting_referral_code":
            await handle_referral_input(message)

        elif state == "awaiting_complaint":
            if user and user["status"] == 2 and user["rid"] != 0:
                if db.add_complaint(message.from_user.id, user["rid"], message.text):
                    await message.answer(
                        "✅ Жалоба отправлена администрации.",
                        reply_markup=keyboard.get_cancel_keyboard()
                    )
                else:
                    await message.answer(
                        "❌ Произошла ошибка при отправке жалобы.",
                        reply_markup=keyboard.get_cancel_keyboard()
                    )
            else:
                await message.answer(
                    "Вы можете отправить жалобу только во время активного дилога.",
                    reply_markup=keyboard.get_cancel_keyboard()
                )
            user_states[message.from_user.id] = None

@dp.callback_query(F.data == "view_complaints")
async def view_complaints(callback: CallbackQuery):
    if not db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора!", show_alert=True)
        return

    complaints = db.get_pending_complaints()
    if not complaints:
        await callback.message.edit_text(
            "📝 Нет активных жалоб.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin")]
            ])
        )
        return

    keyboard = []
    for complaint in complaints:
        # Безопасное получение значений из кортежа
        complaint_id = complaint[0]
        from_user = complaint[1]
        text = complaint[3] if len(complaint) > 3 else "Нет текста"
        
        short_text = text[:30] + "..." if len(text) > 30 else text
        keyboard.append([InlineKeyboardButton(
            text=f"#{complaint_id} от {from_user}: {short_text}",
            callback_data=f"complaint_{complaint_id}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin")])
    
    # Используем edit_text для callback и send_message для обычного сообщения
    if isinstance(callback, CallbackQuery):
        await callback.message.edit_text(
            "📋 Список активных жалоб:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    else:
        await bot.send_message(
            callback.from_user.id,
            "📋 ��писок активных жалоб:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )

@dp.callback_query(F.data.startswith("complaint_"))
async def handle_complaint_action(callback: CallbackQuery):
    complaint_id = int(callback.data.split('_')[1])
    complaints = db.get_pending_complaints()
    complaint = next((c for c in complaints if c[0] == complaint_id), None)
    
    if not complaint:
        await callback.answer("Жалоба не найдена", show_alert=True)
        return

    # Безопасное плучение значений из кортежа
    complaint_id = complaint[0]
    from_user = complaint[1]
    against_user = complaint[2]
    complaint_text = complaint[3]
    status = complaint[4]
    timestamp = complaint[5]
    admin_comment = complaint[6] if len(complaint) > 6 else None

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"approve_complaint_{complaint_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_complaint_{complaint_id}")
        ],
        [
            InlineKeyboardButton(text="🚫 Заблокировать пользователя", 
                               callback_data=f"block_user_{against_user}")
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="view_complaints")]
    ])

    message_text = (
        f"📝 Жалоба #{complaint_id}\n"
        f"О: {from_user}\n"
        f"На: {against_user}\n"
        f"Текст: {complaint_text}\n"
        f"Статус: {status}\n"
        f"Время: {timestamp}\n"
    )
    if admin_comment:
        message_text += f"Комментарий админа: {admin_comment}"

    await callback.message.edit_text(message_text, reply_markup=keyboard)

@dp.callback_query(F.data.startswith(("approve_complaint_", "reject_complaint_")))
async def process_complaint(callback: CallbackQuery):
    if not db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора!", show_alert=True)
        return

    action, complaint_id = callback.data.split("_")[1:3]
    complaint_id = int(complaint_id)
    
    if action == "reject":
        if db.update_complaint_status(complaint_id, "rejected", "Отклонено администратором"):
            await callback.answer("Жалоба отклонена!")
            await view_complaints(callback)
        else:
            await callback.answer("Ошибка при обработке жалобы!")
    else:  # approve
        # Сохраняем ID жалобы в состоянии пользователя
        user_states[callback.from_user.id] = f"awaiting_block_hours_{complaint_id}"
        
        await callback.message.edit_text(
            "Введите количество часов блокировки (от 1 до 168 часов):",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Отмена", callback_data="view_complaints")]
            ])
        )

@dp.callback_query(F.data == "archived_complaints")
async def view_archived_complaints(callback: CallbackQuery):
    if not db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора!", show_alert=True)
        return

    complaints = db.get_archived_complaints()
    if not complaints:
        await callback.message.edit_text(
            "📁 Архив жалоб пуст.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin")]
            ])
        )
        return

    keyboard = []
    for complaint in complaints:
        complaint_id = complaint[0]
        status = complaint[4]
        status_emoji = "✅" if status == "approved" else "❌"
        keyboard.append([InlineKeyboardButton(
            text=f"{status_emoji} Жалоба #{complaint_id}",
            callback_data=f"archived_complaint_{complaint_id}"
        )])

    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin")])
    await callback.message.edit_text(
        "📁 Архив жалоб:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@dp.callback_query(F.data == "manage_blocks")
async def manage_blocks(callback: CallbackQuery):
    if not db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора!", show_alert=True)
        return

    blocked_users = db.get_blocked_users()
    if not blocked_users:
        await callback.message.edit_text(
            "🔓 Нет заблокированных пользователей.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin")]
            ])
        )
        return

    keyboard = []
    current_time = datetime.now()
    
    for user_id, blocked_until, reason, complaint_id in blocked_users:
        # Конвертируем строку времени в объект datetime
        block_until = datetime.strptime(blocked_until, '%Y-%m-%d %H:%M:%S')
        # Вычисляем оставшееся время
        time_left = block_until - current_time
        hours_left = int(time_left.total_seconds() / 3600)
        
        # Форматируем текст кнопки
        button_text = (
            f"🔓 ID: {user_id} | "
            f"Жалоба #{complaint_id if complaint_id else 'Н/Д'} | "
            f"Осталось {hours_left}ч"
        )
        
        keyboard.append([InlineKeyboardButton(
            text=button_text,
            callback_data=f"unblock_user_{user_id}"
        )])

    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin")])
    
    await callback.message.edit_text(
        "🔓 Управление блокировками:\n"
        "Нажмите на пользователя для досроч��ой разблокировки",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@dp.callback_query(F.data.startswith("unblock_user_"))
async def unblock_user(callback: CallbackQuery):
    if not db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора!", show_alert=True)
        return

    user_id = int(callback.data.split("_")[2])
    if db.unblock_user(user_id):
        await callback.answer(f"✅ Пользователь {user_id} разблокирован!")
    else:
        await callback.answer("❌ Ошибка при разблокировке пользователя!")
    
    await manage_blocks(callback)

@dp.callback_query(F.data.startswith("archived_complaint_"))
async def view_archived_complaint(callback: CallbackQuery):
    if not db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора!", show_alert=True)
        return

    complaint_id = int(callback.data.split('_')[2])
    complaints = db.get_archived_complaints()
    complaint = next((c for c in complaints if c[0] == complaint_id), None)

    if not complaint:
        await callback.answer("Жалоба не найдена", show_alert=True)
        return

    # Распаковываем данные жалобы
    complaint_id, from_user, against_user, text, status, timestamp, admin_comment = complaint[:7]
    chat_history = complaint[7:] if len(complaint) > 7 else None

    status_emoji = "✅" if status == "approved" else "❌"
    message_text = (
        f"📝 Архивная жалоба #{complaint_id}\n"
        f"От: {from_user}\n"
        f"На: {against_user}\n"
        f"Текст жалобы: {text}\n"
        f"Статус: {status_emoji} {status}\n"
        f"Время: {timestamp}\n"
    )

    if admin_comment:
        message_text += f"\nКомментарий администратора: {admin_comment}"

    if chat_history and chat_history[0]:  # Если есть история чата
        message_text += "\n\n📨 История чата:\n"
        message_text += f"Сообщение: {chat_history[0]}\n"
        message_text += f"Время: {chat_history[1]}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="archived_complaints")]
    ])

    await callback.message.edit_text(
        message_text,
        reply_markup=keyboard
    )

def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    is_blocked, _ = db.is_user_blocked(user_id)
    
    if is_blocked:
        buttons = [[KeyboardButton(text="ℹ️ Информация о блокировке")]]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    
    buttons = []
    buttons.append([KeyboardButton(text="🔎 Найти чат")])

    if not db.check_user_referral(user_id) and not db.is_admin(user_id):
        buttons.append([KeyboardButton(text="Реферальный код")])

    if db.is_admin(user_id):
        buttons.append([KeyboardButton(text="👨‍💼 Админ-панель")])

    buttons.append([KeyboardButton(text="⚙️ Параметры поиска")])

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message(F.text == "ℹ️ Информация о блокировке")
async def show_block_info_button(message: Message):
    user_id = message.from_user.id
    is_blocked, reason = db.is_user_blocked(user_id)
    
    if not is_blocked:
        await message.answer(
            "✅ Ваш аккаунт не заблокирован.",
            reply_markup=get_main_keyboard(user_id)
        )
        return

    block_info = db.get_block_info(user_id)
    if not block_info:
        await message.answer("Ошибка получения информации о блокировке")
        return

    blocked_until, reason, complaint_id = block_info
    
    current_time = datetime.now()
    block_until = datetime.strptime(blocked_until, '%Y-%m-%d %H:%M:%S')
    time_left = block_until - current_time
    
    total_minutes = int(time_left.total_seconds() / 60)
    hours_left = total_minutes // 60
    minutes_left = total_minutes % 60

    message_text = (
        f"⛔️ Информация о блокировке:\n\n"
        f"📝 Причина: {reason}\n"
        f"🔢 Номер жалобы: #{complaint_id if complaint_id else 'Н/Д'}\n"
        f"⏳ Осталось времени: {hours_left}ч {minutes_left}мин\n"
        f"📅 Разблокировка: {block_until.strftime('%d.%m.%Y %H:%M')}"
    )

    await message.answer(message_text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
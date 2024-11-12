from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from theme import get_themes_for_genre

def get_admin_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить реферальный код", callback_data="add_ref_code")],
        [InlineKeyboardButton(text="➖ Удалить реферальный код", callback_data="remove_ref_code")],
        [InlineKeyboardButton(text="👥 Управление администраторами", callback_data="manage_admins")],
        [InlineKeyboardButton(text="📊 Статистика рефералов", callback_data="ref_stats")],
        [InlineKeyboardButton(text="📋 Рассмотреть жалобы", callback_data="view_complaints")],
        [InlineKeyboardButton(text="📁 Архив жалоб", callback_data="archived_complaints")],
        [InlineKeyboardButton(text="🔓 Управление блокировками", callback_data="manage_blocks")]
    ])
    return keyboard

def get_manage_admins_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить администратора", callback_data="add_admin")],
        [InlineKeyboardButton(text="➖ Удалить администратора", callback_data="remove_admin")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin")]
    ])
    return keyboard

def get_back_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text = "Назад")
    return builder.as_markup(resize_keyboard=True)

def get_search_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Завершить поиск сорола")
    return builder.as_markup(resize_keyboard=True)

def get_cancel_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Завершить диалог")
    builder.button(text="Сценарий")
    builder.button(text="⚠️ Пожаловаться")
    return builder.as_markup(resize_keyboard=True)

def get_genre_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выберите жанр", callback_data="select_genre")],
        [InlineKeyboardButton(text="Постапокалипсис", callback_data="genre_post")],
        [InlineKeyboardButton(text="Романтика", callback_data="genre_romance")],
        [InlineKeyboardButton(text="Киберпанк", callback_data="genre_cyber")],
        [InlineKeyboardButton(text="Фэнтези", callback_data="genre_fantasy")],
        [InlineKeyboardButton(text="Мистика", callback_data="genre_mystic")],
        [InlineKeyboardButton(text="Историческая", callback_data="genre_history")],
        [InlineKeyboardButton(text="Научная Фантастика", callback_data="genre_scifi")],
        [InlineKeyboardButton(text="Хоррор", callback_data="genre_horror")],
        [InlineKeyboardButton(text="Супергероика", callback_data="genre_super")],
        [InlineKeyboardButton(text="Ужасы", callback_data="genre_terror")],
        [InlineKeyboardButton(text="Детектив", callback_data="genre_detective")],
        [InlineKeyboardButton(text="Дисутопия", callback_data="genre_dystopia")]
    ])
    return keyboard

def get_theme_keyboard(genre):
    themes = get_themes_for_genre(genre)
    keyboard = []
    for i, theme in enumerate(themes, 1):
        # Разбиваем длинный текст на две строки
        theme_text = f"Тема {i}:\n{theme}"
        keyboard.append([InlineKeyboardButton(
            text=theme_text,
            callback_data=f"theme_{genre}_{i}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_selected_parameters_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбрать пол", callback_data="set_preferred_gender")],
        [InlineKeyboardButton(text="Указать возрастной диапазон", callback_data="set_age_range")],
        [InlineKeyboardButton(text="Сбросить настройки", callback_data="reset_preferences")]
    ])
    return keyboard

def get_gender_choose_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мужской", callback_data="pref_gender_male")],
        [InlineKeyboardButton(text="Женский", callback_data="pref_gender_female")],
        [InlineKeyboardButton(text="Любой", callback_data="pref_gender_any")]
    ])
    return keyboard

def get_complaint_reasons_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1. Нарушение анонимности", callback_data="complaint_1")],
        [InlineKeyboardButton(text="2. Откровенные материалы", callback_data="complaint_2")],
        [InlineKeyboardButton(text="3. Оскорбления", callback_data="complaint_3")],
        [InlineKeyboardButton(text="4. Отклонение от тематики", callback_data="complaint_4")],
        [InlineKeyboardButton(text="5. Спам/реклама", callback_data="complaint_5")],
        [InlineKeyboardButton(text="6. Угрозы/агрессия", callback_data="complaint_6")],
        [InlineKeyboardButton(text="7. Игнорирование жалоб", callback_data="complaint_7")],
        [InlineKeyboardButton(text="8. Негатив к креативности", callback_data="complaint_8")],
        [InlineKeyboardButton(text="9. Игнорирование администрации", callback_data="complaint_9")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_complaint")]
    ])
    return keyboard
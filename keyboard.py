from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from theme import get_themes_for_genre

def get_admin_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить реферальный код", callback_data="add_ref_code")],
        [InlineKeyboardButton(text="➖ Удалить реферальный код", callback_data="remove_ref_code")],
        [InlineKeyboardButton(text="👥 Управление администраторами", callback_data="manage_admins")],
        [InlineKeyboardButton(text="📊 Статистика рефералов", callback_data="ref_stats")],
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
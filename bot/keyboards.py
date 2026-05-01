from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang_kz")],
    ])


def level_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Лёгкий", callback_data="level_easy")],
        [InlineKeyboardButton(text="🟡 Средний", callback_data="level_medium")],
        [InlineKeyboardButton(text="🔴 Сложный", callback_data="level_hard")],
    ])


def count_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="5", callback_data="count_5"),
            InlineKeyboardButton(text="10", callback_data="count_10"),
        ],
        [
            InlineKeyboardButton(text="15", callback_data="count_15"),
            InlineKeyboardButton(text="20", callback_data="count_20"),
        ],
    ])


def stop_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛑 Стоп", callback_data="stop")]
    ])

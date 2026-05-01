from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def language_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🇷🇺 Русский")],
        [KeyboardButton(text="🇬🇧 English")],
        [KeyboardButton(text="🇰🇿 Қазақша")],
    ], resize_keyboard=True)


def level_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🟢 Лёгкий")],
        [KeyboardButton(text="🟡 Средний")],
        [KeyboardButton(text="🔴 Сложный")],
    ], resize_keyboard=True)


def count_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="5"), KeyboardButton(text="10")],
        [KeyboardButton(text="15"), KeyboardButton(text="20")],
    ], resize_keyboard=True)


def stop_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛑 Стоп")]
    ], resize_keyboard=True)

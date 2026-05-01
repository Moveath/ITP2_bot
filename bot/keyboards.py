from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def language_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Русский"), KeyboardButton(text="English")],
    ], resize_keyboard=True)


def level_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Лёгкий")],
        [KeyboardButton(text="Средний")],
        [KeyboardButton(text="Сложный")],
    ], resize_keyboard=True)


def stop_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Стоп")]
    ], resize_keyboard=True)

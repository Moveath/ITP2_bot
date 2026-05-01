from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang_kz")],
    ])


def level_keyboard(lang="lang_ru"):
    levels = {
        "lang_ru": ["🟢 Лёгкий", "🟡 Средний", "🔴 Сложный"],
        "lang_en": ["🟢 Easy", "🟡 Medium", "🔴 Hard"],
        "lang_kz": ["🟢 Жеңіл", "🟡 Орташа", "🔴 Қиын"],
    }
    texts = levels.get(lang, levels["lang_ru"])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts[0], callback_data="level_easy")],
        [InlineKeyboardButton(text=texts[1], callback_data="level_medium")],
        [InlineKeyboardButton(text=texts[2], callback_data="level_hard")],
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


def stop_keyboard(lang="lang_ru"):
    texts = {"lang_ru": "🛑 Стоп", "lang_en": "🛑 Stop", "lang_kz": "🛑 Тоқта"}
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.get(
            lang, "🛑 Стоп"), callback_data="stop")]
    ])

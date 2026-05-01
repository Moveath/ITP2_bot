from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states import QuizStates
from bot.keyboards import language_keyboard, level_keyboard, count_keyboard, stop_keyboard
from core.session import UserSession

router = Router()
sessions = {}

LANGUAGES = ["🇷🇺 Русский", "🇬🇧 English", "🇰🇿 Қазақша"]
LEVELS = ["🟢 Лёгкий", "🟡 Средний", "🔴 Сложный"]
COUNTS = ["5", "10", "15", "20"]


@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await message.answer(
        "👋 Привет! Я *QuizMind* — твой умный помощник для учёбы!\n\n"
        "📚 Загрузи файл (PDF или PPTX) и я составлю тест по его содержимому.\n"
        "После каждого раунда я буду делать упор на твои слабые места.\n\n"
        "Для начала выбери язык:",
        parse_mode="Markdown",
        reply_markup=language_keyboard()
    )
    await state.set_state(QuizStates.waiting_for_language)


@router.message(QuizStates.waiting_for_language, F.text)
async def got_language(message: Message, state: FSMContext):
    if message.text not in LANGUAGES:
        await message.answer("Пожалуйста выбери язык кнопкой ниже 👇", reply_markup=language_keyboard())
        return
    sessions[message.from_user.id] = UserSession(message.from_user.id)
    sessions[message.from_user.id].language = message.text
    await message.answer("Теперь загрузи файл PDF или PPTX 📎")
    await state.set_state(QuizStates.waiting_for_file)


@router.message(QuizStates.waiting_for_file, F.document)
async def got_file(message: Message, state: FSMContext):
    await state.update_data(file_id=message.document.file_id)
    await message.answer("Сколько вопросов хочешь?", reply_markup=count_keyboard())
    await state.set_state(QuizStates.waiting_for_count)


@router.message(QuizStates.waiting_for_file)
async def wrong_file(message: Message):
    await message.answer("Пожалуйста загрузи файл PDF или PPTX 📎")


@router.message(QuizStates.waiting_for_count, F.text)
async def got_count(message: Message, state: FSMContext):
    if message.text not in COUNTS:
        await message.answer("Выбери количество кнопкой 👇", reply_markup=count_keyboard())
        return
    sessions[message.from_user.id].question_count = int(message.text)
    await message.answer("Выбери сложность:", reply_markup=level_keyboard())
    await state.set_state(QuizStates.waiting_for_level)


@router.message(QuizStates.waiting_for_level, F.text)
async def got_level(message: Message, state: FSMContext):
    if message.text not in LEVELS:
        await message.answer("Выбери сложность кнопкой 👇", reply_markup=level_keyboard())
        return
    user_id = message.from_user.id
    sessions[user_id].level = message.text
    await message.answer("⏳ Генерирую вопросы...", reply_markup=stop_keyboard())
    # ← сюда 3-й человек вставит extract_text(...)
    # ← сюда 2-й человек вставит generate_questions(...)
    await state.set_state(QuizStates.answering)


@router.message(QuizStates.answering, F.text)
async def got_answer(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "🛑 Стоп":
        total = len(sessions[user_id].answers)
        await message.answer(
            f"Сессия завершена!\n✅ Правильных: 0/{total}\n❌ Неправильных: {total}/{total}"
        )
        await state.clear()
        return
    sessions[user_id].answers.append(message.text)
    sessions[user_id].current_index += 1
    await message.answer("Ответ записан ✅")

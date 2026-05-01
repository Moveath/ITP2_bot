from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states import QuizStates
from bot.keyboards import language_keyboard, level_keyboard, count_keyboard, stop_keyboard
from core.session import UserSession

router = Router()
sessions = {}


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


@router.callback_query(F.data.startswith("lang_"))
async def got_language(call: CallbackQuery, state: FSMContext):
    lang_map = {"lang_ru": "🇷🇺 Русский",
                "lang_en": "🇬🇧 English", "lang_kz": "🇰🇿 Қазақша"}
    user_id = call.from_user.id
    sessions[user_id] = UserSession(user_id)
    sessions[user_id].language = lang_map[call.data]
    await call.message.edit_text(f"Язык: {lang_map[call.data]} ✅\n\nТеперь загрузи файл PDF или PPTX 📎")
    await state.set_state(QuizStates.waiting_for_file)
    await call.answer()


@router.message(QuizStates.waiting_for_file, F.document)
async def got_file(message: Message, state: FSMContext):
    await state.update_data(file_id=message.document.file_id)
    await message.answer("Сколько вопросов хочешь?", reply_markup=count_keyboard())
    await state.set_state(QuizStates.waiting_for_count)


@router.message(QuizStates.waiting_for_file)
async def wrong_file(message: Message):
    await message.answer("Пожалуйста загрузи файл PDF или PPTX 📎")


@router.callback_query(F.data.startswith("count_"))
async def got_count(call: CallbackQuery, state: FSMContext):
    count = int(call.data.split("_")[1])
    sessions[call.from_user.id].question_count = count
    await call.message.edit_text(f"Количество вопросов: {count} ✅\n\nВыбери сложность:", reply_markup=level_keyboard())
    await state.set_state(QuizStates.waiting_for_level)
    await call.answer()


@router.callback_query(F.data.startswith("level_"))
async def got_level(call: CallbackQuery, state: FSMContext):
    level_map = {"level_easy": "🟢 Лёгкий",
                 "level_medium": "🟡 Средний", "level_hard": "🔴 Сложный"}
    user_id = call.from_user.id
    sessions[user_id].level = level_map[call.data]
    await call.message.edit_text(f"Сложность: {level_map[call.data]} ✅\n\n⏳ Генерирую вопросы...")
    await call.answer()
    # ← сюда 3-й человек вставит extract_text(...)
    # ← сюда 2-й человек вставит generate_questions(...)
    await state.set_state(QuizStates.answering)


@router.callback_query(F.data == "stop")
async def got_stop(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    total = len(sessions[user_id].answers)
    await call.message.edit_text(
        f"Сессия завершена!\n✅ Правильных: 0/{total}\n❌ Неправильных: {total}/{total}"
    )
    await state.clear()
    await call.answer()


@router.message(QuizStates.answering, F.text)
async def got_answer(message: Message, state: FSMContext):
    user_id = message.from_user.id
    sessions[user_id].answers.append(message.text)
    sessions[user_id].current_index += 1
    await message.answer("Ответ записан ✅")

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states import QuizStates
from bot.keyboards import language_keyboard, level_keyboard, stop_keyboard
from core.session import UserSession

router = Router()
sessions = {}


@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Загрузи файл PDF или PPTX")
    await state.set_state(QuizStates.waiting_for_file)


@router.message(QuizStates.waiting_for_file, F.document)
async def got_file(message: Message, state: FSMContext):
    user_id = message.from_user.id
    sessions[user_id] = UserSession(user_id)
    await state.update_data(file_id=message.document.file_id)
    await message.answer("Сколько вопросов? (например: 5)")
    await state.set_state(QuizStates.waiting_for_count)


@router.message(QuizStates.waiting_for_count, F.text)
async def got_count(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введи число, например: 5")
        return
    sessions[message.from_user.id].question_count = int(message.text)
    await message.answer("Выбери язык:", reply_markup=language_keyboard())
    await state.set_state(QuizStates.waiting_for_language)


@router.message(QuizStates.waiting_for_language, F.text)
async def got_language(message: Message, state: FSMContext):
    sessions[message.from_user.id].language = message.text
    await message.answer("Выбери сложность:", reply_markup=level_keyboard())
    await state.set_state(QuizStates.waiting_for_level)


@router.message(QuizStates.waiting_for_level, F.text)
async def got_level(message: Message, state: FSMContext):
    user_id = message.from_user.id
    sessions[user_id].level = message.text
    await message.answer("Генерирую вопросы... ⏳", reply_markup=stop_keyboard())
    # ← сюда 3-й человек вставит extract_text(...)
    # ← сюда 2-й человек вставит generate_questions(...)
    await state.set_state(QuizStates.answering)


@router.message(QuizStates.answering, F.text)
async def got_answer(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "Стоп":
        total = len(sessions[user_id].answers)
        await message.answer(
            f"Стоп!\n✅ Правильных: 0/{total}\n❌ Неправильных: {total}/{total}"
        )
        await state.clear()
        return
    sessions[user_id].answers.append(message.text)
    sessions[user_id].current_index += 1
    await message.answer("Ответ записан, следующий вопрос скоро...")

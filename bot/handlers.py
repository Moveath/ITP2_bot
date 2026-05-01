from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states import QuizStates
from bot.keyboards import language_keyboard, level_keyboard, count_keyboard, stop_keyboard
from core.session import UserSession

router = Router()
sessions = {}

TEXTS = {
    "lang_ru": {
        "welcome": "👋 Привет! Я *QuizMind* — твой умный помощник для учёбы!\n\n📚 Загрузи файл (PDF или PPTX) и я составлю тест по его содержимому.\nПосле каждого раунда я буду делать упор на твои слабые места.",
        "upload": "Теперь загрузи файл PDF или PPTX 📎",
        "wrong_file": "Пожалуйста загрузи файл PDF или PPTX 📎",
        "how_many": "Сколько вопросов хочешь?",
        "choose_level": "Выбери сложность:",
        "generating": "⏳ Генерирую вопросы...",
        "answer_saved": "Ответ записан ✅",
        "session_done": "Сессия завершена!\n✅ Правильных: 0/{total}\n❌ Неправильных: {total}/{total}",
    },
    "lang_en": {
        "welcome": "👋 Hi! I'm *QuizMind* — your smart study assistant!\n\n📚 Upload a file (PDF or PPTX) and I'll create a quiz based on it.\nAfter each round I'll focus on your weak spots.",
        "upload": "Now upload a PDF or PPTX file 📎",
        "wrong_file": "Please upload a PDF or PPTX file 📎",
        "how_many": "How many questions do you want?",
        "choose_level": "Choose difficulty:",
        "generating": "⏳ Generating questions...",
        "answer_saved": "Answer saved ✅",
        "session_done": "Session finished!\n✅ Correct: 0/{total}\n❌ Wrong: {total}/{total}",
    },
    "lang_kz": {
        "welcome": "👋 Сәлем! Мен *QuizMind* — сенің ақылды оқу көмекшің!\n\n📚 PDF немесе PPTX файлын жүктей — тест құрастырамын.\nӘр раундта қателерінді талдаймын.",
        "upload": "PDF немесе PPTX файлын жүктеңіз 📎",
        "wrong_file": "PDF немесе PPTX файлын жүктеңіз 📎",
        "how_many": "Қанша сұрақ қалайсыз?",
        "choose_level": "Қиындық деңгейін таңдаңыз:",
        "generating": "⏳ Сұрақтар құрылуда...",
        "answer_saved": "Жауап сақталды ✅",
        "session_done": "Сессия аяқталды!\n✅ Дұрыс: 0/{total}\n❌ Қате: {total}/{total}",
    },
}


@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await message.answer(
        "🌐 Выбери язык / Choose language / Тілді таңдаңыз:",
        reply_markup=language_keyboard()
    )
    await state.set_state(QuizStates.waiting_for_language)


@router.callback_query(F.data.startswith("lang_"))
async def got_language(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    sessions[user_id] = UserSession(user_id)
    sessions[user_id].language = call.data
    t = TEXTS[call.data]
    await call.message.edit_text(
        t["welcome"] + "\n\n" + t["upload"],
        parse_mode="Markdown"
    )
    await state.set_state(QuizStates.waiting_for_file)
    await call.answer()


@router.message(QuizStates.waiting_for_file, F.document)
async def got_file(message: Message, state: FSMContext):
    user_id = message.from_user.id
    t = TEXTS[sessions[user_id].language]
    await state.update_data(file_id=message.document.file_id)
    await message.answer(t["how_many"], reply_markup=count_keyboard())
    await state.set_state(QuizStates.waiting_for_count)


@router.message(QuizStates.waiting_for_file)
async def wrong_file(message: Message, state: FSMContext):
    user_id = message.from_user.id
    t = TEXTS[sessions[user_id].language]
    await message.answer(t["wrong_file"])


@router.callback_query(F.data.startswith("count_"))
async def got_count(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    t = TEXTS[sessions[user_id].language]
    count = int(call.data.split("_")[1])
    sessions[user_id].question_count = count
    await call.message.edit_text(f"{count} ✅\n\n{t['choose_level']}", reply_markup=level_keyboard())
    await state.set_state(QuizStates.waiting_for_level)
    await call.answer()


@router.callback_query(F.data.startswith("level_"))
async def got_level(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    t = TEXTS[sessions[user_id].language]
    sessions[user_id].level = call.data
    await call.message.edit_text(t["generating"])
    await call.answer()
    # ← сюда 3-й человек вставит extract_text(...)
    # ← сюда 2-й человек вставит generate_questions(...)
    await state.set_state(QuizStates.answering)


@router.callback_query(F.data == "stop")
async def got_stop(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    t = TEXTS[sessions[user_id].language]
    total = len(sessions[user_id].answers)
    await call.message.edit_text(t["session_done"].format(total=total))
    await state.clear()
    await call.answer()


@router.message(QuizStates.answering, F.text)
async def got_answer(message: Message, state: FSMContext):
    user_id = message.from_user.id
    t = TEXTS[sessions[user_id].language]
    sessions[user_id].answers.append(message.text)
    sessions[user_id].current_index += 1
    await message.answer(t["answer_saved"])

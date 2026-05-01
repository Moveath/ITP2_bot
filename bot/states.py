from aiogram.fsm.state import State, StatesGroup


class QuizStates(StatesGroup):
    waiting_for_file = State()
    waiting_for_count = State()
    waiting_for_language = State()
    waiting_for_level = State()
    answering = State()

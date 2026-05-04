import csv
from core.question import Question

class CSVManager:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def save_questions(self, questions: list[Question]):
        pass

    def save_answer(self, question_id: int, user_answer: int):
        pass

    def get_all_data(self) -> list[dict]:
        return []
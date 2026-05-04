from core.question import Question
from data.csv_manager import CSVManager

class AdaptiveTest:
    def __init__(self, source_text: str, adapt_step: int,
                 llm_generator, csv_manager=None, language="lang_kz"):
        self.source_text = source_text
        self.adapt_step = adapt_step
        self.llm = llm_generator
        self.csv = csv_manager or CSVManager("default.csv")
        self.language = language
        self.current_level = 1
        self.answers_buffer = []

    def generate_next_questions(self, count=1, language=None):
        lang = language or self.language
        questions = self.llm.generate_questions(
            text=self.source_text,
            level=self.current_level,
            num_questions=count,
            previous_answers=self.answers_buffer,
            language=lang
        )
        self.csv.save_questions(questions)
        return questions

    def process_answer(self, question: Question, user_answer: int):
        is_correct = (user_answer == question.correct_option)
        self.answers_buffer.append({
            "question": question.text,
            "selected": user_answer,
            "correct": is_correct,
            "level": question.level
        })
        self.csv.save_answer(question.question_id, user_answer)
        if len(self.answers_buffer) >= self.adapt_step:
            self._update_level()
            self.answers_buffer.clear()

    def _update_level(self):
        correct = sum(1 for a in self.answers_buffer if a["correct"])
        if correct == 0:
            self.current_level = max(1, self.current_level - 2)
        elif correct == 1:
            self.current_level = max(1, self.current_level - 1)
        elif correct == 2:
            self.current_level += 1
        else:
            self.current_level += 2

    def get_final_report(self, language=None):
        lang = language or self.language
        all_data = self.csv.get_all_data()
        if not all_data:
            return "No data for report."
        return self.llm.generate_final_report(all_data, language=lang)
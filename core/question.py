from dataclasses import dataclass

@dataclass
class Question:
    question_id: int
    text: str
    options: list[str]
    correct_option: int       # 0-ден бастап индекс
    level: int                # 1..5
    explanation: str = ""
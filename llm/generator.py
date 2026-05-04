# llm/generator.py
import json
import logging
from typing import List
from openai import OpenAI
from core.question import Question
from config import LLM_API_KEY, LLM_MODEL

logger = logging.getLogger(__name__)

class LLMGenerator:
    def __init__(self, api_key: str = None):
        self.client = OpenAI(
            api_key=api_key or LLM_API_KEY,
            base_url="https://openrouter.ai/api/v1"   # OpenRouter
        )
        self.model = LLM_MODEL

    def generate_questions(self, text: str, level: int, num_questions: int = 1,
                           previous_answers: list = None) -> List[Question]:
        from llm.prompts import build_prompt

        prev_context = ""
        if previous_answers:
            prev_context = json.dumps(previous_answers, ensure_ascii=False, indent=2)

        prompt = build_prompt(text, level, prev_context)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Сен сарапшы оқытушысың. MCQ тест сұрақтарын құрастырасың. Жауапты тек JSON форматында қайтар."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2048,
                extra_headers={
                    "HTTP-Referer": "http://localhost",   # OpenRouter ережесі бойынша
                    "X-Title": "ITP2_bot",
                }
            )
            raw = response.choices[0].message.content
            logger.debug(f"OpenRouter жауабы: {raw}")
            return self._parse_questions(raw, level)

        except Exception as e:
            logger.error(f"Сұрақ генерациясы қатесі: {e}")
            return [Question(
                question_id=0,
                text=f"API қатесі: {str(e)[:150]}",
                options=["A) Иә", "B) Жоқ", "C) Мүмкін", "D) Басқа"],
                correct_option=0,
                level=level,
                explanation=""
            )]

    def analyze_answer(self, question_text: str, user_answer: int,
                       correct_answer: int, options: list) -> dict:
        from llm.prompts import ANALYSIS_PROMPT
        prompt = ANALYSIS_PROMPT.format(
            question=question_text,
            options=json.dumps(options, ensure_ascii=False),
            user_answer=user_answer,
            correct_answer=correct_answer
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=200,
                extra_headers={"HTTP-Referer": "http://localhost", "X-Title": "ITP2_bot"}
            )
            raw = response.choices[0].message.content
            return json.loads(raw)
        except:
            return {"error_type": "unknown", "comment": ""}

    def generate_final_report(self, all_data: list) -> str:
        from llm.prompts import FINAL_REPORT_PROMPT
        prompt = FINAL_REPORT_PROMPT.format(
            data=json.dumps(all_data, ensure_ascii=False, indent=2)
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
                extra_headers={"HTTP-Referer": "http://localhost", "X-Title": "ITP2_bot"}
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Қате: {e}"

    def _parse_questions(self, raw: str, level: int) -> List[Question]:
        json_str = raw
        if "```json" in raw:
            json_str = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            json_str = raw.split("```")[1].split("```")[0].strip()

        data = json.loads(json_str)
        if isinstance(data, dict) and "questions" in data:
            items = data["questions"]
        elif isinstance(data, list):
            items = data
        else:
            raise ValueError(f"Күтілмеген JSON құрылымы: {data}")

        questions = []
        for i, item in enumerate(items):
            q = Question(
                question_id=abs(hash(item["text"])) % 100000 + i,
                text=item["text"],
                options=item["options"],
                correct_option=item.get("correct", 0),
                level=level,
                explanation=item.get("explanation", "")
            )
            questions.append(q)
        return questions
import json
import logging
from typing import List
from openai import OpenAI
from core.question import Question
from config import LLM_API_KEY, LLM_MODEL
from llm.prompts import build_prompt, get_system_prompt, get_analysis_prompt, get_final_report_prompt

logger = logging.getLogger(__name__)

class LLMGenerator:
    def __init__(self, api_key: str = None):
        self.client = OpenAI(
            api_key=api_key or LLM_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = LLM_MODEL

    def generate_questions(self, text: str, level: int, num_questions: int = 1,
                           previous_answers: list = None, language: str = "lang_kz") -> List[Question]:
        prev_context = ""
        if previous_answers:
            prev_context = json.dumps(previous_answers, ensure_ascii=False, indent=2)

        system_msg = get_system_prompt(language)
        user_msg = build_prompt(text, level, language, prev_context)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.7,
                max_tokens=2048,
                extra_headers={"HTTP-Referer": "http://localhost", "X-Title": "ITP2_bot"}
            )
            raw = response.choices[0].message.content
            logger.debug(f"Raw LLM response: {raw}")
            return self._parse_questions(raw, level)
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return [Question(0, f"API error: {str(e)[:150]}",
                             ["A) Yes", "B) No", "C) Maybe", "D) Other"], 0, level, "")]

    def analyze_answer(self, question_text: str, user_answer: int,
                       correct_answer: int, options: list, language: str = "lang_kz") -> dict:
        prompt = get_analysis_prompt(language).format(
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
            data = self._extract_json(response.choices[0].message.content)
            return data if isinstance(data, dict) else {"error_type": "unknown", "comment": ""}
        except Exception as e:
            logger.warning(f"Analysis error: {e}")
            return {"error_type": "unknown", "comment": ""}

    def generate_final_report(self, all_data: list, language: str = "lang_kz") -> str:
        prompt = get_final_report_prompt(language).format(
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
            logger.error(f"Report error: {e}")
            return f"Error: {e}"

    def _parse_questions(self, raw: str, level: int) -> List[Question]:
        data = self._extract_json(raw)
        if not data:
            raise ValueError("No valid JSON found")

        if isinstance(data, dict) and "questions" in data:
            items = data["questions"]
        elif isinstance(data, list):
            items = data
        else:
            raise ValueError(f"Unexpected JSON structure: {data}")

        questions = []
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            q = Question(
                question_id=abs(hash(item.get("text", ""))) % 100000 + i,
                text=item.get("text", ""),
                options=item.get("options", ["A", "B", "C", "D"]),
                correct_option=item.get("correct", 0),
                level=level,
                explanation=item.get("explanation", "")
            )
            questions.append(q)
        return questions if questions else [Question(0, "No questions parsed", [], 0, level, "")]

    def _extract_json(self, text: str):
        """Извлекает JSON из любого текста, обрезая всё до первой '{' и после последней '}'."""
        if not text:
            return None
        # убираем ```json ... ``` если есть
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        # пытаемся найти JSON объект/массив
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
        try:
            return json.loads(text)
        except:
            # иногда модель возвращает несколько объектов — пробуем найти первый валидный
            for i in range(len(text)):
                if text[i] in '{[':
                    try:
                        return json.loads(text[i:])
                    except:
                        continue
            return None
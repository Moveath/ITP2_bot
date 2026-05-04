# llm/prompts.py

LEVEL_DESCRIPTIONS = {
    1: {"lang_ru": "очень лёгкий, только базовые факты", "lang_kz": "өте оңай, тек негізгі фактілер", "lang_en": "very easy, basic facts only"},
    2: {"lang_ru": "средний, проверка понимания", "lang_kz": "орташа, түсінікті тексеру", "lang_en": "medium, understanding check"},
    3: {"lang_ru": "сложный, требует аналитического мышления", "lang_kz": "қиын, аналитикалық ойлауды қажет етеді", "lang_en": "hard, requires analytical thinking"},
    4: {"lang_ru": "очень сложный, сравнение нескольких концепций", "lang_kz": "өте қиын, бірнеше концепцияны салыстыру", "lang_en": "very hard, comparing multiple concepts"},
    5: {"lang_ru": "экспертный, требует глубоких знаний", "lang_kz": "эксперт деңгей, терең білімді талап етеді", "lang_en": "expert level, requires deep knowledge"}
}

LANGUAGE_NAMES = {
    "lang_ru": "русском",
    "lang_kz": "қазақша",
    "lang_en": "English"
}

def build_prompt(text: str, level: int, language: str = "lang_kz", previous_context: str = "") -> str:
    lang_name = LANGUAGE_NAMES.get(language, "русском")
    difficulty = LEVEL_DESCRIPTIONS.get(level, LEVEL_DESCRIPTIONS[2]).get(language, "средний")

    prompt = (
        f"Создай MCQ тест **строго на {lang_name} языке** на основе текста ниже.\n"
        f"Сложность: {difficulty} (уровень {level}).\n"
        f"4 варианта ответа, один правильный (индекс 0-3).\n"
        f"Добавь поле 'explanation' с кратким пояснением.\n"
        f"Ответ верни **ТОЛЬКО** в виде JSON без дополнительного текста:\n"
        f'{{"questions":[{{"text":"...","options":["A) ...","B) ...","C) ...","D) ..."],"correct":0,"explanation":"..."}}]}}'
    )
    if previous_context:
        prompt += f"\n\nУчти предыдущие ответы пользователя:\n{previous_context}"
    prompt += f"\n\nТекст:\n{text}"
    return prompt

def get_system_prompt(language: str = "lang_kz") -> str:
    lang_name = LANGUAGE_NAMES.get(language, "русском")
    return f"Ты преподаватель. Отвечай только на {lang_name} языке. Генерируй MCQ строго в JSON формате без дополнительных комментариев."

def get_analysis_prompt(language: str = "lang_kz") -> str:
    lang_name = LANGUAGE_NAMES.get(language, "русском")
    return (
        f"Ты преподаватель. Проанализируй ответ студента:\n"
        f" - 'major' — полностью неверный или абсурдный\n"
        f" - 'minor' — близок к правильному, но ошибочен\n"
        f" - 'none' — верный\n"
        f"Ответ дай **строго на {lang_name} языке** в JSON: {{{{'error_type':'major','comment':'...'}}}}\n\n"
        f"Вопрос: {{question}}\nВарианты: {{options}}\nОтвет пользователя (индекс): {{user_answer}}\nПравильный (индекс): {{correct_answer}}"
    )

def get_final_report_prompt(language: str = "lang_kz") -> str:
    lang_name = LANGUAGE_NAMES.get(language, "русском")
    return (
        f"Ты опытный преподаватель. Напиши итоговый анализ **строго на {lang_name} языке** на основе данных сессии.\n"
        f"1. Общий уровень студента.\n2. Какие темы усвоены, какие нет.\n3. Типичные ошибки.\n4. Рекомендации.\n"
        f"Обращайся к студенту на «ты».\n\nДанные:\n{{data}}"
    )
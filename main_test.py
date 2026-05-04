import sys
sys.path.append(".")

from llm.generator import LLMGenerator
from core.adaptive_test import AdaptiveTest
from data.csv_manager import CSVManager

llm = LLMGenerator()
source_text = ("Елұрдың жасы 17 де"
               "Ол Университетте оқиды"
               "Пайтонды жақсы көреді"
               "Шахмат ойнай алады"
               "Ол боксты жақсы көреді")
csv_mgr = CSVManager("test_ru.csv")
test = AdaptiveTest(source_text, adapt_step=3, llm_generator=llm, csv_manager=csv_mgr, language="lang_kz")
print(f"Уровень: {test.current_level}")

qs = test.generate_next_questions(1)
if qs:
    q = qs[0]
    print(f"Вопрос: {q.text}")
    print(f"Варианты: {q.options}")


    wrong = (q.correct_option + 1) % 4
    analysis = llm.analyze_answer(q.text, wrong, q.correct_option, q.options, language="lang_ru")
    print(f"Ошибка: {analysis.get('error_type')}, комментарий: {analysis.get('comment')}")

    for i in range(3):
        qs = test.generate_next_questions(1)
        q = qs[0]
        test.process_answer(q, wrong)
        print(f"Шаг {i+1}: {q.text} (уровень {q.level})")
    print(f"После 3 ошибок уровень: {test.current_level}")

    test.current_level = 2
    test.answers_buffer.clear()
    for i in range(3):
        qs = test.generate_next_questions(1)
        q = qs[0]
        test.process_answer(q, q.correct_option)
        print(f"Верно {i+1} (уровень {q.level})")
    print(f"После 3 правильных уровень: {test.current_level}")

    print("\n=== Итоговый отчёт ===")
    print(test.get_final_report())
else:
    print("Вопросы не получены.")
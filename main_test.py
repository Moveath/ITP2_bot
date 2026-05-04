import sys
sys.path.append(".")

from llm.generator import LLMGenerator
from core.adaptive_test import AdaptiveTest
from data.csv_manager import CSVManager

print("=== Hugging Face нақты API тесті ===")

llm = LLMGenerator()

source_text = ("Python — интерпретацияланатын, жоғары деңгейлі бағдарламалау тілі. "
               "Ол 1991 жылы Гвидо ван Россуммен жасалған. "
               "Python динамикалық типтеу мен автоматты жады басқаруды қолдайды.")

csv_mgr = CSVManager("test.csv")
test = AdaptiveTest(source_text, adapt_step=3, llm_generator=llm, csv_manager=csv_mgr)

print(f"Бастапқы деңгей: {test.current_level}")

try:
    qs = test.generate_next_questions(1)
    if qs:
        q = qs[0]
        print(f"Сұрақ: {q.text}")
        print(f"Нұсқалар: {q.options}")
        print(f"Дұрыс жауап индексі: {q.correct_option}")

        wrong = (q.correct_option + 1) % 4
        analysis = llm.analyze_answer(q.text, wrong, q.correct_option, q.options)
        print(f"Қате түрі: {analysis.get('error_type')}, Түсіндірме: {analysis.get('comment')}")

        for i in range(3):
            qs = test.generate_next_questions(1)
            q = qs[0]
            test.process_answer(q, wrong)
            print(f"Қадам {i+1}: {q.text} (деңгей {q.level})")
        print(f"3 қатеден соңғы деңгей: {test.current_level}")

        test.current_level = 2
        test.answers_buffer.clear()
        for i in range(3):
            qs = test.generate_next_questions(1)
            q = qs[0]
            test.process_answer(q, q.correct_option)
            print(f"Дұрыс қадам {i+1} (деңгей {q.level})")
        print(f"3 дұрыстан соңғы деңгей: {test.current_level}")

        print("\n=== Қорытынды талдау ===")
        print(test.get_final_report())
    else:
        print("Сұрақ алынбады.")

except Exception as e:
    print(f"Тестілеу барысында қате: {e}")
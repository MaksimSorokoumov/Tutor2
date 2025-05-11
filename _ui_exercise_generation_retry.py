from _13_generate_exercises import generate_exercises as _llm_generate_exercises
from _15_log_error import log_error

def generate_exercises(section_text, difficulty, section_title, stage, previous_questions, settings_path="settings.json"):
    """Wrapper для генерации упражнений с retry и проверкой корректности ответов для multiple-choice"""
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            exercises = _llm_generate_exercises(
                section_text,
                difficulty,
                section_title,
                stage,
                previous_questions,
                settings_path
            )
            # Нормализация правильного ответа: если строка содержит запятые, преобразуем в список
            if stage == 1:
                for ex in exercises:
                    ca = ex.get('correct_answer')
                    if isinstance(ca, str) and ',' in ca:
                        items = [item.strip() for item in ca.split(',') if item.strip()]
                        ex['correct_answer'] = items
            # Валидация для тестов с несколькими правильными ответами
            if stage == 1:
                all_valid = True
                for ex in exercises:
                    ca = ex.get('correct_answer')
                    if not (isinstance(ca, list) and len(ca) > 1):
                        all_valid = False
                        break
                if not all_valid:
                    raise ValueError(f"Некорректное количество правильных ответов на попытке {attempt}")
            return exercises
        except Exception as e:
            log_error(e)
            if attempt == max_retries:
                # Передаем окончательную ошибку
                raise ValueError(f"Не удалось сгенерировать корректные упражнения после {max_retries} попыток: {e}")
            # повтор попытки
            continue 
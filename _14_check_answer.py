"""Модуль для проверки ответов пользователя на упражнения."""
from typing import Dict, Any, List, Optional
import json

from _4_load_settings import load_settings
from _11_send_chat_completion import send_chat_completion, get_completion_text
from _13_generate_exercises import check_single_choice_answer, check_multiple_choice_answer

def check_answer(
    exercise: Dict[str, Any],
    user_answer: str,
    user_comment: str = "",
    settings_path: str = "settings.json"
) -> Dict[str, Any]:
    """Проверяет правильность ответа пользователя.
    
    Args:
        exercise: Словарь с данными упражнения
        user_answer: Ответ пользователя
        user_comment: Комментарий пользователя к ответу (для этапов 1 и 2)
        settings_path: Путь к файлу настроек
        
    Returns:
        Словарь с результатами проверки:
        - is_correct: boolean - правильный ли ответ
        - feedback: str - отзыв/объяснение
        - correct_answer: правильный ответ (для сравнения)
        
    Raises:
        ValueError: При ошибке проверки ответа
        FileNotFoundError: Если файл настроек не найден
    """
    # Определяем этап упражнения
    stage = exercise.get("stage", 0)
    
    # Для тестов с единственным правильным ответом (этап 0) используем локальную проверку
    if stage == 0 and exercise.get("type") in ["тесты с единственным правильным ответом", 
                                             "тест с единственным правильным ответом"]:
        return check_single_choice_answer(exercise, user_answer)
    
    # Для тестов с множественным выбором (этап 1) сначала выполняем локальную проверку
    if stage == 1 and exercise.get("type") in ["тесты с несколькими правильными ответами",
                                              "тест с несколькими правильными ответами"]:
        local = check_multiple_choice_answer(exercise, user_answer)
        # Если локально правильно — возвращаем результат
        if local["is_correct"]:
            return local
        # Если есть комментарий — доверяем LLM для финальной оценки с учётом учебного материала
        if user_comment.strip():
            try:
                mm_context = exercise.get("context", "")
                system_message = {
                    "role": "system",
                    "content": "Ты — опытный преподаватель, проверяющий тесты с несколькими правильными ответами. Учитывай учебный материал и комментарий студента. Если аргументы студента обоснованы и верны по материалу, ответ считаем правильным. Формат: {'is_correct': true/false, 'feedback': 'объяснение'}"
                }
                user_content = (
                    f"Учебный материал:\n{mm_context}\n\n"
                    f"Вопрос: {exercise.get('question')}\n"
                    "Варианты:\n"
                    + "".join(f"{i}. {opt}\n" for i, opt in enumerate(exercise.get('options', []), 1))
                    + f"Правильный ответ: {exercise.get('correct_answer')}\n"
                    f"Ответ студента: {user_answer}\n"
                    f"Комментарий студента: {user_comment}\n\n"
                    "Оцени, правильно ли ответил студент и дай подробный, но лаконичный отзыв."
                )
                user_message = {"role": "user", "content": user_content}
                settings = load_settings(settings_path)
                resp = send_chat_completion(
                    api_endpoint=settings["api_endpoint"], model=settings["model"],
                    messages=[system_message, user_message],
                    max_tokens=settings["max_tokens"], temperature=0.3
                )
                text = get_completion_text(resp)
                json_text = text.strip()
                if json_text.startswith("```json"):
                    json_text = json_text.split("```json", 1)[1]
                if json_text.startswith("```"):
                    json_text = json_text.split("```", 1)[1]
                if json_text.endswith("```"):
                    json_text = json_text.rsplit("```", 1)[0]
                try:
                    llm_res = json.loads(json_text)
                    return llm_res
                except Exception:
                    pass
            except Exception as e:
                print(f"Ошибка при полной LLM-проверке: {e}")
        # Иначе — возвращаем локальный с добавлением пояснения
        try:
            explanation = get_llm_explanation_for_wrong_answer(exercise, user_answer, user_comment, settings_path)
            if explanation:
                local["feedback"] += "\n\n" + explanation
        except Exception as e:
            print(f"Ошибка при получении объяснения от нейросети: {e}")
        return local
    
    # Для открытых вопросов (этап 2) используем проверку через нейросеть
    # Загружаем настройки
    settings = load_settings(settings_path)
    
    # Формируем системное сообщение в зависимости от этапа
    if stage == 1:  # Тесты с несколькими правильными ответами (используется только для объяснения ошибок)
        system_message = {
            "role": "system",
            "content": """Ты - опытный преподаватель, проверяющий ответы студентов на тесты с несколькими правильными ответами.

Оцени, правильно ли студент выбрал все верные варианты. Учитывай следующие моменты:
1. Правильный ответ должен содержать ВСЕ верные варианты и НЕ содержать неверные
2. Если студент выбрал только часть правильных вариантов - ответ неполный и считается неверным
3. Если студент выбрал все правильные варианты, но добавил хотя бы один неверный - ответ неверный
4. Учитывай комментарий студента при оценке ответа - возможно, он объясняет свой выбор или указывает на неоднозначность вопроса

Формат ответа строго в виде JSON:
```json
{"is_correct": true/false, "feedback": "подробное объяснение с указанием правильных вариантов и ошибок студента"}
```"""
        }
    else:  # Открытые вопросы (этап 2)
        system_message = {
            "role": "system",
            "content": """Ты - опытный преподаватель, проверяющий ответы студентов на открытые вопросы.

Оцени ответ студента по следующим критериям:
1. Полнота ответа - покрывает ли все аспекты вопроса
2. Точность - соответствует ли фактам из учебного материала
3. Глубина понимания - демонстрирует ли студент понимание темы
4. Структура и логика - насколько логично выстроен ответ
5. Применение знаний - может ли студент применить знания в контексте

Предоставь подробную, но доброжелательную обратную связь. Объясни, что было сделано хорошо,
а что можно улучшить. Помоги студенту лучше понять тему.

Формат ответа строго в виде JSON:
```json
{
  "is_correct": true/false,
  "feedback": "подробная обратная связь",
  "strengths": ["сильные стороны ответа"],
  "areas_for_improvement": ["области для улучшения"]
}
```"""
        }
    
    # Формируем сообщение с упражнением и ответом пользователя
    content = f"Тип упражнения: {exercise.get('type')}\nВопрос: {exercise.get('question')}\n\n"
    
    # Добавляем варианты ответов, если они есть
    if 'options' in exercise and exercise['options']:
        content += "Варианты ответов:\n"
        for i, option in enumerate(exercise['options'], 1):
            content += f"{i}. {option}\n"
        content += "\n"
    
    if 'correct_answer' in exercise:
        content += f"Правильный ответ: {exercise['correct_answer']}\n\n"
    elif 'model_answer' in exercise:
        content += f"Модельный ответ: {exercise['model_answer']}\n\n"
    
    content += f"Ответ студента: {user_answer}\n"
    
    # Добавляем комментарий пользователя, если он есть
    if user_comment:
        content += f"\nКомментарий студента: {user_comment}\n"
    
    content += "\nОцени, правильно ли ответил студент."
    
    user_message = {
        "role": "user",
        "content": content
    }
    
    try:
        # Отправляем запрос к API
        response = send_chat_completion(
            api_endpoint=settings["api_endpoint"],
            model=settings["model"],
            messages=[system_message, user_message],
            max_tokens=settings["max_tokens"],
            temperature=0.2  # Меньшая температура для более точных ответов
        )
        
        # Извлекаем текст из ответа
        check_text = get_completion_text(response)
        
        if not check_text:
            raise ValueError("Не удалось получить результат проверки от нейросети")
        
        # Извлекаем JSON из текста ответа
        json_text = check_text.strip()
        if json_text.startswith("```json"):
            json_text = json_text.split("```json", 1)[1]
        if json_text.startswith("```"):
            json_text = json_text.split("```", 1)[1]
        if json_text.endswith("```"):
            json_text = json_text.rsplit("```", 1)[0]
        
        # Парсим JSON
        check_result = json.loads(json_text)
        
        # Добавляем правильный ответ или модельный ответ для открытых вопросов
        check_result["correct_answer"] = exercise.get("correct_answer", exercise.get("model_answer", ""))
        
        return check_result
    
    except json.JSONDecodeError as e:
        print(f"Ошибка разбора JSON результата проверки: {e}")
        print(f"Полученный текст: {check_text}")
        
        # Возвращаем базовый результат в случае ошибки
        return {
            "is_correct": False,
            "feedback": "Не удалось автоматически проверить ответ. Пожалуйста, сравните с правильным ответом.",
            "correct_answer": exercise.get("correct_answer", exercise.get("model_answer", "")),
            "error": str(e)
        }
    
    except Exception as e:
        print(f"Ошибка при проверке ответа: {e}")
        
        # Возвращаем базовый результат в случае ошибки
        return {
            "is_correct": False,
            "feedback": "Произошла ошибка при проверке ответа. Пожалуйста, попробуйте еще раз.",
            "correct_answer": exercise.get("correct_answer", exercise.get("model_answer", "")),
            "error": str(e)
        }

def get_llm_explanation_for_wrong_answer(
    exercise: Dict[str, Any],
    user_answer: str,
    user_comment: str = "",
    settings_path: str = "settings.json"
) -> str:
    """Получает объяснение от нейросети, почему ответ пользователя неверен.
    
    Args:
        exercise: Словарь с данными упражнения
        user_answer: Ответ пользователя
        user_comment: Комментарий пользователя к ответу
        settings_path: Путь к файлу настроек
        
    Returns:
        Текст объяснения от нейросети или пустая строка в случае ошибки
    """
    # Загружаем настройки
    settings = load_settings(settings_path)
    
    # Преобразуем числовые ответы пользователя в текстовые варианты для лучшего понимания нейросетью
    user_answer_text = []
    correct_answer_text = []
    options = exercise.get("options", [])
    
    # Преобразуем ответ пользователя в текстовые варианты
    try:
        user_indices = [int(idx.strip()) for idx in user_answer.split(',')]
        for idx in user_indices:
            if 1 <= idx <= len(options):
                user_answer_text.append(options[idx-1])
    except ValueError:
        user_answer_text = [user_answer]  # Если не удалось разобрать как числа
    
    # Преобразуем правильный ответ в текстовые варианты
    correct_answer = exercise["correct_answer"]
    if isinstance(correct_answer, list):
        correct_answer_text = correct_answer
    else:
        # Пытаемся разобрать строку с запятыми
        try:
            correct_indices = [int(idx.strip()) for idx in correct_answer.split(',')]
            for idx in correct_indices:
                if 1 <= idx <= len(options):
                    correct_answer_text.append(options[idx-1])
        except ValueError:
            # Если не удалось разобрать как числа, используем оригинальный правильный ответ
            correct_answer_text = [ans.strip() for ans in correct_answer.split(',')]
    
    # Формируем системное сообщение
    system_message = {
        "role": "system",
        "content": """Ты - опытный преподаватель, объясняющий студентам их ошибки в тестах с несколькими правильными ответами.
Твоя задача - объяснить студенту, почему его ответ неверен, и почему правильные варианты являются верными.
Объяснение должно быть подробным, но при этом кратким и понятным.
Не используй фразы вроде "Ваш ответ неверен" или "Правильный ответ", а сразу переходи к объяснению.
"""
    }
    
    # Формируем сообщение с упражнением и ответом пользователя
    content = f"Вопрос: {exercise.get('question')}\n\n"
    
    # Добавляем варианты ответов
    content += "Варианты ответов:\n"
    for i, option in enumerate(options, 1):
        content += f"{i}. {option}\n"
    content += "\n"
    
    # Добавляем правильный ответ и ответ пользователя в текстовом виде
    content += f"Правильный ответ: {', '.join(correct_answer_text)}\n"
    content += f"Ответ студента: {', '.join(user_answer_text)}\n\n"
    
    # Добавляем комментарий пользователя, если он есть
    if user_comment:
        content += f"Комментарий студента: {user_comment}\n\n"
    
    content += "Объясни, почему правильными являются указанные варианты, и почему выбор студента неверен."
    
    user_message = {
        "role": "user",
        "content": content
    }
    
    try:
        # Отправляем запрос к API
        response = send_chat_completion(
            api_endpoint=settings["api_endpoint"],
            model=settings["model"],
            messages=[system_message, user_message],
            max_tokens=settings["max_tokens"],
            temperature=0.3
        )
        
        # Извлекаем текст из ответа
        explanation = get_completion_text(response)
        
        return explanation if explanation else ""
    
    except Exception as e:
        print(f"Ошибка при получении объяснения от нейросети: {e}")
        return "" 
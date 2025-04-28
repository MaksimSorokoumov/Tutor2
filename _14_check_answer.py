"""Модуль для проверки ответов пользователя на упражнения."""
from typing import Dict, Any, List, Optional
import json

from _4_load_settings import load_settings
from _11_send_chat_completion import send_chat_completion, get_completion_text

def check_answer(
    exercise: Dict[str, Any],
    user_answer: str,
    settings_path: str = "settings.json"
) -> Dict[str, Any]:
    """Проверяет правильность ответа пользователя.
    
    Args:
        exercise: Словарь с данными упражнения
        user_answer: Ответ пользователя
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
    # Загружаем настройки
    settings = load_settings(settings_path)
    
    # Проверка ответа через нейросеть для всех типов упражнений
    system_message = {
        "role": "system",
        "content": f"""Ты - опытный преподаватель, проверяющий ответы студентов на упражнения следующих типов:
- тест с единственным правильным ответом
- тест с несколькими правильными ответами
- открытый вопрос
- заполнение пропущенных слов в предложении

Вопрос и правильный ответ переданы. Оцени, является ли ответ студента правильным, учитывая возможные варианты формулировок и несколько правильных ответов.
Дай подробный отзыв по ошибкам или подтверждение правильности.
Формат ответа строго в виде JSON:
```json
{{"is_correct": true/false, "feedback": "подробное объяснение"}}
```"""
    }
    user_message = {
        "role": "user",
        "content": f"Тип упражнения: {exercise.get('type')}\nВопрос: {exercise.get('question')}\n\nПравильный ответ: {exercise.get('correct_answer')}\n\nОтвет студента: {user_answer}\nОцени, правильно ли ответ." 
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
        
        # Добавляем правильный ответ к результату
        check_result["correct_answer"] = exercise["correct_answer"]
        
        return check_result
    
    except json.JSONDecodeError as e:
        print(f"Ошибка разбора JSON результата проверки: {e}")
        print(f"Полученный текст: {check_text}")
        
        # Возвращаем базовый результат в случае ошибки
        return {
            "is_correct": False,
            "feedback": "Не удалось автоматически проверить ответ. Пожалуйста, сравните с правильным ответом.",
            "correct_answer": exercise["correct_answer"],
            "error": str(e)
        }
    
    except Exception as e:
        print(f"Ошибка при проверке ответа: {e}")
        
        # Возвращаем базовый результат в случае ошибки
        return {
            "is_correct": False,
            "feedback": "Произошла ошибка при проверке ответа. Пожалуйста, попробуйте еще раз.",
            "correct_answer": exercise["correct_answer"],
            "error": str(e)
        } 
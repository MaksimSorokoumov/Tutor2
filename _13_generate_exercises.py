"""Модуль для генерации упражнений к тексту с помощью нейросети."""
from typing import List, Dict, Any, Optional
import json

from _4_load_settings import load_settings
from _11_send_chat_completion import send_chat_completion, get_completion_text

def generate_exercises(
    section_text: str,
    difficulty: str = "средний",
    settings_path: str = "settings.json"
) -> List[Dict[str, Any]]:
    """Генерирует упражнения по тексту через LLM.
    
    Args:
        section_text: Текст раздела для генерации упражнений
        difficulty: Сложность упражнений (начальный, средний, продвинутый)
        settings_path: Путь к файлу настроек
        
    Returns:
        Список словарей с упражнениями, каждое упражнение содержит:
        - id: уникальный идентификатор
        - type: тип упражнения
        - question: текст вопроса
        - options: список вариантов ответа (для тестов)
        - correct_answer: правильный ответ или ответы
        
    Raises:
        ValueError: При ошибке генерации упражнений
        FileNotFoundError: Если файл настроек не найден
    """
    # Загружаем настройки
    settings = load_settings(settings_path)
    
    # Формируем системное сообщение
    system_message = {
        "role": "system",
        "content": f"""Ты – опытный преподаватель, создающий эффективные учебные упражнения.
Твоя задача – сгенерировать 3-5 упражнений следующих типов для текста уровня сложности {difficulty}:

1. Тест с единственным правильным ответом
2. Тест с несколькими правильными ответами
3. Открытый вопрос
4. Заполнение пропущенных слов в предложении

Ответ должен быть строго в виде JSON-массива:
```json
[
  {{
    "id": 1,
    "type": "тип упражнения (тест с единственным правильным ответом, тест с несколькими правильными ответами, открытый вопрос, заполнение пропущенных слов)",
    "question": "текст вопроса",
    "options": ["вариант 1", "вариант 2", ...],  // для тестов
    "correct_answer": "правильный ответ или массив правильных ответов"
  }},
  ...
]
```"""
    }
    
    # Формируем сообщение с текстом для генерации упражнений
    user_message = {
        "role": "user",
        "content": f"Создай упражнения по следующему тексту с уровнем сложности {difficulty}: \n\n{section_text}"
    }
    
    try:
        # Отправляем запрос к API
        response = send_chat_completion(
            api_endpoint=settings["api_endpoint"],
            model=settings["model"],
            messages=[system_message, user_message],
            max_tokens=settings["max_tokens"],
            temperature=settings["temperature"]
        )
        
        # Извлекаем текст из ответа
        exercises_text = get_completion_text(response)
        
        if not exercises_text:
            raise ValueError("Не удалось получить упражнения от нейросети")
        
        # Извлекаем JSON из текста ответа
        # Может быть обернут в тройные бэктики, так что удаляем их
        json_text = exercises_text.strip()
        if json_text.startswith("```json"):
            json_text = json_text.split("```json", 1)[1]
        if json_text.startswith("```"):
            json_text = json_text.split("```", 1)[1]
        if json_text.endswith("```"):
            json_text = json_text.rsplit("```", 1)[0]
        
        # Парсим JSON
        exercises = json.loads(json_text)
        
        # Проверяем, что получили список
        if not isinstance(exercises, list):
            raise ValueError(f"Некорректный формат упражнений: {exercises}")
        
        return exercises
    
    except json.JSONDecodeError as e:
        print(f"Ошибка разбора JSON упражнений: {e}")
        print(f"Полученный текст: {exercises_text}")
        raise ValueError(f"Не удалось разобрать упражнения: {str(e)}")
    
    except Exception as e:
        print(f"Ошибка при генерации упражнений: {e}")
        raise ValueError(f"Не удалось сгенерировать упражнения: {str(e)}") 
"""Модуль для генерации упражнений к тексту с помощью нейросети."""
from typing import List, Dict, Any, Optional
import json
import re

from _4_load_settings import load_settings
from _11_send_chat_completion import send_chat_completion, get_completion_text

def generate_exercises(
    section_text: str,
    difficulty: str = "средний",
    section_title: str = "",
    stage: int = 0,
    previous_questions: List[str] = None,
    settings_path: str = "settings.json"
) -> List[Dict[str, Any]]:
    """Генерирует упражнения по тексту через LLM.
    
    Args:
        section_text: Текст раздела для генерации упражнений
        difficulty: Сложность упражнений (начальный, средний, продвинутый)
        section_title: Заголовок раздела (для контекста)
        stage: Этап обучения (0-2):
            0 - тесты с одним правильным ответом
            1 - тесты с несколькими правильными ответами
            2 - открытые вопросы
        previous_questions: Список ранее заданных вопросов для избежания повторений
        settings_path: Путь к файлу настроек
        
    Returns:
        Список словарей с упражнениями, каждое упражнение содержит:
        - id: уникальный идентификатор
        - type: тип упражнения
        - question: текст вопроса
        - options: список вариантов ответа (для тестов)
        - correct_answer: правильный ответ или ответы
        - stage: этап обучения
        
    Raises:
        ValueError: При ошибке генерации упражнений
        FileNotFoundError: Если файл настроек не найден
    """
    # Загружаем настройки
    settings = load_settings(settings_path)
    
    # Инициализируем список предыдущих вопросов, если он не передан
    if previous_questions is None:
        previous_questions = []
        
    # Определяем тип упражнений в зависимости от этапа
    if stage == 0:
        exercise_type = "тесты с единственным правильным ответом"
        count = 3
    elif stage == 1:
        exercise_type = "тесты с несколькими правильными ответами"
        count = 2
    else:  # stage == 2
        exercise_type = "открытые вопросы"
        count = 1
    
    # Строим контекст с названием темы, если оно есть
    context = f"Тема: {section_title}\n\n" if section_title else ""
    context += section_text
        
    # Формируем системное сообщение
    system_message = {
        "role": "system",
        "content": f"""Ты – опытный преподаватель, создающий эффективные учебные упражнения.
Твоя задача – сгенерировать {count} упражнения типа "{exercise_type}" для текста уровня сложности {difficulty}.

ВАЖНЫЕ ТРЕБОВАНИЯ:
1. Правильные ответы ДОЛЖНЫ однозначно следовать из предоставленного текста учебного материала
2. Вопросы должны быть разнообразными и охватывать разные аспекты текста
3. Избегай создания слишком похожих вопросов или вариантов ответов
4. Формулируй вопросы четко и однозначно
5. Никогда не создавай вопросы, которые уже были в списке предыдущих вопросов
6. Для тестов с одним правильным ответом создавай 4-5 вариантов ответа
7. Для тестов с несколькими правильными ответами создавай 5-7 вариантов, из которых 2-3 правильные
8. Для открытых вопросов предоставь модельный ответ и критерии оценки

Ответ должен быть строго в виде JSON-массива:
```json
[
  {{
    "id": 1,
    "type": "{exercise_type}",
    "question": "текст вопроса",
    "options": ["вариант 1", "вариант 2", ...],  // для тестов
    "correct_answer": "правильный ответ или массив правильных ответов",
    "stage": {stage}
  }},
  ...
]
```"""
    }
    
    # Формируем сообщение с текстом для генерации упражнений
    user_message_content = f"Создай {count} упражнения типа \"{exercise_type}\" по следующему учебному материалу с уровнем сложности {difficulty}: \n\n{context}"
    
    # Если есть предыдущие вопросы, добавляем их в запрос для избежания повторений
    if previous_questions:
        user_message_content += "\n\nИзбегай следующих вопросов (они уже были заданы):\n"
        for i, q in enumerate(previous_questions, 1):
            if i <= 10:  # Ограничиваем количество передаваемых предыдущих вопросов
                user_message_content += f"{i}. {q}\n"
    
    user_message = {
        "role": "user",
        "content": user_message_content
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
        
        # Добавляем этап в каждое упражнение, если его нет
        for ex in exercises:
            if "stage" not in ex:
                ex["stage"] = stage
                
        return exercises
    
    except json.JSONDecodeError as e:
        print(f"Ошибка разбора JSON упражнений: {e}")
        print(f"Полученный текст: {exercises_text}")
        raise ValueError(f"Не удалось разобрать упражнения: {str(e)}")
    
    except Exception as e:
        print(f"Ошибка при генерации упражнений: {e}")
        raise ValueError(f"Не удалось сгенерировать упражнения: {str(e)}")

def check_single_choice_answer(exercise: Dict[str, Any], user_answer: str) -> Dict[str, Any]:
    """Проверяет ответ на тест с единственным правильным ответом без использования LLM.
    
    Args:
        exercise: Словарь с данными упражнения
        user_answer: Ответ пользователя (номер или текст ответа)
        
    Returns:
        Словарь с результатами проверки:
        - is_correct: boolean - правильный ли ответ
        - feedback: str - отзыв/объяснение
        - correct_answer: правильный ответ (для сравнения)
    """
    correct_answer = exercise["correct_answer"]
    options = exercise.get("options", [])
    
    # Определяем, передан ли ответ как номер варианта или как текст
    try:
        # Если передан номер варианта
        answer_index = int(user_answer.strip()) - 1
        if 0 <= answer_index < len(options):
            user_answer_text = options[answer_index]
        else:
            return {
                "is_correct": False,
                "feedback": f"Вариант ответа с номером {answer_index + 1} не существует. Выберите от 1 до {len(options)}.",
                "correct_answer": correct_answer
            }
    except ValueError:
        # Если передан текст ответа
        user_answer_text = user_answer.strip()
    
    # Сравниваем ответ с правильным (нечувствительно к регистру)
    is_correct = user_answer_text.lower() == correct_answer.lower()
    
    # Также проверяем, совпадает ли ответ с номером правильного варианта
    if not is_correct and user_answer.strip().isdigit():
        correct_index = next((i for i, opt in enumerate(options) if opt.lower() == correct_answer.lower()), -1)
        if correct_index != -1 and int(user_answer.strip()) == correct_index + 1:
            is_correct = True
            user_answer_text = options[correct_index]
    
    if is_correct:
        feedback = "Правильный ответ."
    else:
        feedback = f"Неправильный ответ. Верный вариант: {correct_answer}"
    
    return {
        "is_correct": is_correct,
        "feedback": feedback,
        "correct_answer": correct_answer
    } 
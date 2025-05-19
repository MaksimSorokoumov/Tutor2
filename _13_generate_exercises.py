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
        count = 4
    elif stage == 1:
        exercise_type = "тесты с несколькими правильными ответами"
        count = 2
    else:  # stage == 2
        exercise_type = "открытые вопросы"
        count = 1
    
    # Строим контекст с названием темы, если оно есть
    context = f"Тема: {section_title}\n\n" if section_title else ""
    context += section_text
        
    # Формируем системное сообщение в зависимости от этапа
    if stage == 0:
        system_content = f"""Твоя задача – сгенерировать {count} вопросов с единственным правильным ответом. Уровень сложности вопросов - {difficulty}. На основании следующего учебного материала:
        Учебный материал:\n\n{context}\n\n

Напомню, Твоя задача – сгенерировать {count} вопросов с единственным правильным ответом. Уровень сложности вопросов - {difficulty}.
Требования:
1. Каждый вопрос должен иметь 4-5 вариантов ответа, включая ровно один правильный ответ.
2. Правильно овтетить на вопрос можно толко прочитав и поняв учебный материал.
3. Вопросы должны быть разнообразными и не повторять предыдущие.

Твой ответ должен быть строго в виде JSON-массива:
```json
[
  {{
    "id": 1,
    "type": "тесты с единственным правильным ответом",
    "question": "текст вопроса",
    "options": ["вариант 1", "вариант 2", "...", "..."],
    "correct_answer": "правильный ответ",
    "stage": {stage}
  }},
  ...
]
```"""
    elif stage == 1:
        system_content = f"""Ты – опытный преподаватель-методист, создающий тесты с несколькими правильными ответами на основе учебного материала.
Твоя задача – сгенерировать {count} вопроса с несколькими правильными ответами. Уровнь сложности вопросов - {difficulty}. На основании следующего учебного материала:
        Учебный материал:\n\n{context}\n\n

Напомню, твоя задача – сгенерировать {count} вопроса с несколькими правильными ответами. Уровнь сложности вопросов - {difficulty}. 
Требования:
1. Каждый вопрос должен иметь 5-7 вариантов ответа, из которых 2-3 правильные.
2. Правильно овтетить на вопрос можно толко прочитав и поняв учебный материал.
3. Вопросы должны быть разнообразными и не повторять предыдущие.

Ответ должен быть строго в виде JSON-массива:
```json
[
  {{
    "id": 1,
    "type": "тесты с несколькими правильными ответами",
    "question": "текст вопроса",
    "options": ["вариант 1", "...", "...", "...", "..."],
    "correct_answer": ["правильный1", "правильный2"],
    "stage": {stage}
  }},
  ...
]
```"""
    else:
        system_content = f"""Твоя задача – сгенерировать {count} открытый вопрос уровня сложности {difficulty}. На основании следующего учебного материала:
Учебный материал:\n\n{context}\n\n

Напомнию, твоя задача – сгенерировать {count} открытый вопрос уровня сложности {difficulty}. На основании предоставленного учебного материала.
Требования:
1. Вопросы должны быть разнообразными и не повторять предыдущие.
2. Для вопроса предоставь модельный ответ и критерии оценки.
3. Правильный ответ на вопрос должен прямо следовать из учебного материала. 
4. Сложность вопроса должна соответствовать уровню сложности, объему и детализации предоставленного Учебного материала.

Ответ должен быть строго в виде JSON-массива:
```json
[
  {{
    "id": 1,
    "type": "открытые вопросы",
    "question": "текст вопроса",
    "model_answer": "текст модельного ответа",
    "evaluation_criteria": ["критерий1", "критерий2"],
    "stage": {stage}
  }},
  ...
]
```"""

    system_message = {"role": "system", "content": "Ты – опытный преподаватель-методист, создающий вопросы на проверку изученного материала."}
    
    # Stage-specific инструкции как пользовательский промпт
    user_message_content = system_content
    if previous_questions:
        user_message_content += "\n\nИзбегай следующих вопросов (они уже были заданы):\n"
        for i, q in enumerate(previous_questions, 1):
            if i <= 10:
                user_message_content += f"{i}. {q}\n"
    user_message = {"role": "user", "content": user_message_content}
    
    try:
        # Подготовка параметров в зависимости от провайдера LLM
        if settings.get("llm_provider") == "openrouter":
            api_endpoint = "https://openrouter.ai/api/v1"
            model = settings.get("selected_openrouter_model")
            api_key = settings.get("openrouter_api_key")
        else:
            api_endpoint = settings["api_endpoint"]
            model = settings["model"]
            api_key = None
        # Отправляем запрос к API
        response = send_chat_completion(
            api_endpoint=api_endpoint,
            model=model,
            messages=[system_message, user_message],
            max_tokens=settings["max_tokens"],
            temperature=settings["temperature"],
            api_key=api_key
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

def check_multiple_choice_answer(exercise: Dict[str, Any], user_answer: str) -> Dict[str, Any]:
    """Проверяет ответ на тест с несколькими правильными ответами без использования LLM.
    
    Args:
        exercise: Словарь с данными упражнения
        user_answer: Ответ пользователя (строка с номерами вариантов через запятую)
        
    Returns:
        Словарь с результатами проверки:
        - is_correct: boolean - правильный ли ответ
        - feedback: str - отзыв/объяснение
        - correct_answer: правильный ответ или ответы (для сравнения)
    """
    correct_answer = exercise["correct_answer"]
    options = exercise.get("options", [])
    
    # Преобразуем правильный ответ в список индексов опций
    correct_indices = []
    
    # Если правильный ответ представлен в виде списка строк
    if isinstance(correct_answer, list):
        for answer in correct_answer:
            for i, option in enumerate(options):
                if option.lower() == answer.lower():
                    correct_indices.append(i + 1)  # Индексы с 1
                    break
    # Если правильный ответ представлен в виде строки с перечислением
    else:
        for answer in correct_answer.split(','):
            answer = answer.strip()
            for i, option in enumerate(options):
                if option.lower() == answer.lower():
                    correct_indices.append(i + 1)  # Индексы с 1
                    break
    
    # Получаем ответ пользователя как список индексов
    try:
        user_indices = [int(idx.strip()) for idx in user_answer.split(',')]
    except ValueError:
        return {
            "is_correct": False,
            "feedback": "Некорректный формат ответа. Укажите номера вариантов через запятую.",
            "correct_answer": correct_answer
        }
    
    # Проверяем, что все выбранные индексы существуют
    if any(idx <= 0 or idx > len(options) for idx in user_indices):
        return {
            "is_correct": False,
            "feedback": f"Некоторые варианты ответа не существуют. Допустимые значения от 1 до {len(options)}.",
            "correct_answer": correct_answer
        }
    
    # Сортируем индексы для корректного сравнения
    correct_indices.sort()
    user_indices.sort()
    
    # Основная проверка совпадения ответов
    is_correct = correct_indices == user_indices
    
    # Формируем отзыв
    if is_correct:
        feedback = "Правильный ответ. Вы выбрали все верные варианты."
    else:
        # Подготовка строки с правильными вариантами для отзыва
        correct_options_text = []
        for idx in correct_indices:
            correct_options_text.append(f"{idx}. {options[idx-1]}")
        
        # Формируем подробный отзыв
        feedback = "Неправильный ответ. "
        
        # Поиск несовпадений
        missing = [idx for idx in correct_indices if idx not in user_indices]
        extra = [idx for idx in user_indices if idx not in correct_indices]
        
        if missing:
            feedback += f"Вы не выбрали следующие правильные варианты: {', '.join(map(str, missing))}. "
        
        if extra:
            feedback += f"Вы выбрали следующие неправильные варианты: {', '.join(map(str, extra))}. "
        
        feedback += f"Правильными вариантами являются: {', '.join(map(str, correct_indices))}."
    
    return {
        "is_correct": is_correct,
        "feedback": feedback,
        "correct_answer": correct_answer
    } 
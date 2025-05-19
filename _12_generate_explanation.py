"""Модуль для генерации пояснений к тексту с помощью нейросети."""
from typing import Optional, Dict, Any, List
import json
import os
import re

from _4_load_settings import load_settings
from _11_send_chat_completion import send_chat_completion, get_completion_text

def analyze_text_complexity(text: str) -> Dict[str, Any]:
    """Анализирует сложность и объем исходного текста.
    
    Args:
        text: Анализируемый текст
        
    Returns:
        Словарь с метриками текста
    """
    # Разбиваем текст на абзацы и считаем их
    paragraphs = [p for p in re.split(r'\n\s*\n', text) if p.strip()]
    paragraph_count = len(paragraphs)
    
    # Определяем общую длину текста
    text_length = len(text)
    
    # Считаем среднюю длину абзаца
    avg_paragraph_length = text_length / paragraph_count if paragraph_count > 0 else 0
    
    # Находим списки в тексте
    list_items = re.findall(r'^[\s]*[-•*]\s+.*$', text, re.MULTILINE)
    has_lists = len(list_items) > 0
    
    # Ищем специальные термины (выделенные кавычками, заглавными буквами и т.д.)
    special_terms = re.findall(r'«[^»]+»|"[^"]+"|\b[А-Я]{2,}\b', text)
    term_count = len(special_terms)
    
    # Определяем общую детализацию текста
    if paragraph_count <= 3 and avg_paragraph_length < 500 and term_count < 5:
        detail_type = "обзорный"
    elif paragraph_count > 7 or (avg_paragraph_length > 800 and paragraph_count > 4) or term_count > 10:
        detail_type = "подробный"
    else:
        detail_type = "средний"
    
    return {
        "paragraphs": paragraph_count,
        "length": text_length,
        "avg_paragraph_length": avg_paragraph_length,
        "has_lists": has_lists,
        "terms": term_count,
        "detail_type": detail_type
    }

def generate_explanation(
    section_text: str,
    detail_level: str = "средний",
    user_feedback: Optional[str] = None,
    settings_path: str = "settings.json"
) -> str:
    """Генерирует пояснение к тексту раздела через LLM.
    
    Args:
        section_text: Текст раздела для объяснения
        detail_level: Уровень детализации пояснения (базовый, средний, подробный)
        user_feedback: Отзыв пользователя для уточнения объяснения
        settings_path: Путь к файлу настроек
        
    Returns:
        Текст пояснения от нейросети
        
    Raises:
        ValueError: При ошибке генерации пояснения
        FileNotFoundError: Если файл настроек не найден
    """
    # Загружаем настройки
    settings = load_settings(settings_path)
    
    # Анализируем сложность и объем исходного текста
    text_analysis = analyze_text_complexity(section_text)
    
    # Формируем системное сообщение в зависимости от уровня детализации и анализа текста
    system_message = {
        "role": "system",
        "content": f"""Ты - опытный преподаватель, который объясняет сложные темы простым и понятным языком. 
Твоя задача - объяснить предоставленный текст с уровнем детализации: {detail_level}.

Уровни детализации:
- базовый: короткое объяснение основных идей, не более 3-4 абзацев
- средний: подробное объяснение основных и второстепенных идей, примеры, до 6-7 абзацев
- подробный: всестороннее объяснение с глубокими примерами, аналогиями и контекстом, до 10 абзацев

Анализ исходного текста:
- Тип текста: {text_analysis["detail_type"]} (обзорный, средний или подробный)
- Количество абзацев: {text_analysis["paragraphs"]}
- Наличие списков: {"да" if text_analysis["has_lists"] else "нет"}
- Количество специальных терминов: {text_analysis["terms"]}

ВАЖНО: Соблюдай уровень детализации исходного текста!
1. Если исходный текст обзорный (краткий, поверхностный), не расширяй темы, которые лишь кратко упомянуты.
2. Если в тексте концепция лишь перечислена без подробностей, не давай развернутых объяснений.
3. Соотноси объем своего объяснения с объемом исходного текста.
4. Если автор описывает что-то подробно, ты тоже можешь дать подробное объяснение этих конкретных аспектов.
5. Никогда не добавляй существенную информацию, которой нет в исходном тексте.
6. Выдавай результат в HTML: используй теги <h2> для заголовков, <p> для абзацев, <ul>/<li> для списков, <strong> для выделений, без внешних обёрток <html>, <body>.

Используй следующие приёмы объяснения:
1. Начни с общего объяснения, затем переходи к деталям (только если они есть в исходном тексте)
2. Используй примеры из обычной жизни для сложных концепций
3. Выделяй ключевые понятия и определения
4. Перефразируй сложные идеи своими словами
5. Используй аналогии для объяснения концепций"""
    }
    
    # Формируем сообщение с текстом для объяснения
    user_message = {
        "role": "user",
        "content": f"Объясни мне следующий текст с уровнем детализации {detail_level}, сохраняя уровень обобщения исходного материала: \n\n{section_text}"
    }
    
    # Если есть отзыв пользователя, добавляем его как дополнительное сообщение
    messages = [system_message, user_message]
    if user_feedback:
        messages.append({
            "role": "user",
            "content": f"Я не понял следующие моменты в твоем объяснении: {user_feedback}. Пожалуйста, объясни подробнее, но не расширяй темы за пределы исходного текста."
        })
    
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
            messages=messages,
            max_tokens=settings["max_tokens"],
            temperature=settings["temperature"],
            api_key=api_key
        )
        
        # Извлекаем текст из ответа
        explanation_text = get_completion_text(response)
        
        if not explanation_text:
            raise ValueError("Не удалось получить объяснение от нейросети")
        
        return explanation_text
    
    except Exception as e:
        print(f"Ошибка при генерации объяснения: {e}")
        raise ValueError(f"Не удалось сгенерировать объяснение: {str(e)}") 
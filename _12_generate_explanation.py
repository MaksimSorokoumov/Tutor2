"""Модуль для генерации пояснений к тексту с помощью нейросети."""
from typing import Optional, Dict, Any, List
import json
import os

from _4_load_settings import load_settings
from _11_send_chat_completion import send_chat_completion, get_completion_text

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
    
    # Формируем системное сообщение в зависимости от уровня детализации
    system_message = {
        "role": "system",
        "content": f"""Ты - опытный преподаватель, который объясняет сложные темы простым и понятным языком. 
Твоя задача - объяснить предоставленный текст с уровнем детализации: {detail_level}.

Уровни детализации:
- базовый: короткое объяснение основных идей, не более 3-4 абзацев
- средний: подробное объяснение основных и второстепенных идей, примеры, до 6-7 абзацев
- подробный: всестороннее объяснение с глубокими примерами, аналогиями и контекстом, до 10 абзацев

Используй следующие приёмы объяснения:
1. Начни с общего объяснения, затем переходи к деталям
2. Используй примеры из обычной жизни для сложных концепций
3. Выделяй ключевые понятия и определения
4. Перефразируй сложные идеи своими словами
5. Используй аналогии"""
    }
    
    # Формируем сообщение с текстом для объяснения
    user_message = {
        "role": "user",
        "content": f"Объясни мне следующий текст с уровнем детализации {detail_level}: \n\n{section_text}"
    }
    
    # Если есть отзыв пользователя, добавляем его как дополнительное сообщение
    messages = [system_message, user_message]
    if user_feedback:
        messages.append({
            "role": "user",
            "content": f"Я не понял следующие моменты в твоем объяснении: {user_feedback}. Пожалуйста, объясни подробнее."
        })
    
    try:
        # Отправляем запрос к API
        response = send_chat_completion(
            api_endpoint=settings["api_endpoint"],
            model=settings["model"],
            messages=messages,
            max_tokens=settings["max_tokens"],
            temperature=settings["temperature"]
        )
        
        # Извлекаем текст из ответа
        explanation_text = get_completion_text(response)
        
        if not explanation_text:
            raise ValueError("Не удалось получить объяснение от нейросети")
        
        return explanation_text
    
    except Exception as e:
        print(f"Ошибка при генерации объяснения: {e}")
        raise ValueError(f"Не удалось сгенерировать объяснение: {str(e)}") 
"""Модуль для форматирования текста разделов через LLM и обновления structure.json."""
import json
from typing import List, Dict, Any
from _4_load_settings import load_settings
from _11_send_chat_completion import send_chat_completion, get_completion_text
import re


def format_sections(
    structure_path: str,
    settings_path: str = "settings.json"
) -> None:
    """
    Форматирует текст всех разделов в файле structure.json через LLM
    и записывает отформатированный текст обратно в тот же файл.

    Args:
        structure_path: путь к файлу structure.json
        settings_path: путь к файлу настроек
    """
    # Загружаем настройки и структуру
    settings = load_settings(settings_path)
    with open(structure_path, 'r', encoding='utf-8') as f:
        sections: List[Dict[str, Any]] = json.load(f)

    # Системное сообщение с правилами форматирования
    system_message = {
        "role": "system",
        "content": (
            "Ты – опытный редактор учебных материалов. Приведи текст раздела к единому,"
            " читабельному и структурированному виду, соблюдая следующие принципы:\n"
            "1. Согласованность оформления во всех разделах.\n"
            "2. Читаемость: чёткие абзацы, списки, выделение ключевых идей.\n"
            "3. Структура: при необходимости используй списки и подзаголовки.\n"
            "4. Умеренность: выделяй только важные элементы, без перегрузки.\n"
            "5. Выделяй ключевые концепции и определения, сохраняя исходный текст без добавления новой информации.\n"
            "6. Сохраняй содержание, орфографию и пунктуацию оригинального текста, не изменяй авторскую стилистику.\n"
            "7. Не добавляй в текст никаких комментариев, пояснений, объяснений, не относящихся к тексту.\n"
            "8. Выдавай результат в HTML: используй теги <h2> для заголовков, <p> для абзацев, <ul>/<li> для списков, <strong> для выделений, без внешних обёрток <html>, <body>."
        )
    }

    # Обрабатываем каждый раздел отдельно
    for section in sections:
        title = section.get('title', '')
        raw_text = section.get('content', '')
        # Сообщение пользователя с текстом раздела
        user_message = {
            "role": "user",
            "content": (
                f"Заголовок раздела: {title}\n\n"
                f"Исходный текст:\n{raw_text}\n\n"
                "Отформатируй этот текст по указанным правилам."
            )
        }

        # Запрос к LLM
        try:
            # Подготовка параметров в зависимости от провайдера LLM
            if settings.get("llm_provider") == "openrouter":
                api_endpoint = "https://openrouter.ai/api/v1"
                model = settings.get("selected_openrouter_model")
                api_key = settings.get("openrouter_api_key")
            else:
                api_endpoint = settings['api_endpoint']
                model = settings['model']
                api_key = None
            resp = send_chat_completion(
                api_endpoint=api_endpoint,
                model=model,
                messages=[system_message, user_message],
                max_tokens=settings['max_tokens'],
                temperature=settings.get('temperature', 0.5),
                api_key=api_key
            )
            formatted = get_completion_text(resp) or ''
        except Exception as e:
            # Если ошибка, оставляем оригинальный текст
            formatted = raw_text

        # Убираем возможные обёртки из ```
        formatted = formatted.strip()
        if formatted.startswith('```'):
            formatted = formatted.strip('`')
        # Удаляем теги <think> и <thinking> и их содержимое
        formatted = re.sub(r'<think>.*?</think>|<thinking>.*?</thinking>', '', formatted, flags=re.DOTALL)
        section['content'] = formatted.strip()

    # Записываем обновленную структуру обратно
    with open(structure_path, 'w', encoding='utf-8') as f:
        json.dump(sections, f, ensure_ascii=False, indent=2)

    print(f"Отформатировано {len(sections)} разделов в {structure_path}") 
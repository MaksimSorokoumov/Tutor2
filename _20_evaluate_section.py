"""Модуль для комплексной оценки раздела курса по пятибалльной шкале."""
import json
from typing import Dict, Any
from _11_send_chat_completion import send_chat_completion, get_completion_text
from _4_load_settings import load_settings

def evaluate_section(
    progress_data: Dict[str, Any],
    section_id: str,
    settings_path: str = "settings.json"
) -> Dict[str, Any]:
    """Оценивает усвоение материала по упражнением раздела через LLM.

    Возвращает словарь с ключами 'score' (int) и 'comment' (str).
    """
    # Загружаем настройки
    settings = load_settings(settings_path)
    section = progress_data['sections'].get(section_id, {})
    exercises = section.get('exercises', [])
    # Формируем контент для LLM
    content = 'Оцени усвоение материала в разделе по пятибалльной шкале. ' \
              'Данные по упражнениям:\n'
    # Добавляем каждую попытку
    for ex in exercises:
        content += f"Вопрос: {ex['question']}\n"
        content += f"Этап: {ex['stage'] + 1}/3; Ответ пользователя: {ex['user_answer']}; Правильный: {ex['correct_answer']}; Результат: {'верно' if ex['is_correct'] else 'неверно'}\n\n"
    content += 'На основе этого дай оценку от 1 до 5 и краткий комментарий.'
    messages = [
        {"role": "system", "content": "Ты - опытный преподаватель, оценивающий усвоение курса, отвечай строго в формате JSON {\"score\": <число 1-5>, \"comment\": \"<текст>\"} без дополнительного текста."},
        {"role": "user", "content": content}
    ]
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
        messages=messages,
        max_tokens=settings.get("max_tokens", 200),
        temperature=0.3,
        api_key=api_key
    )
    text = get_completion_text(resp) or ''
    # Убираем обёртку ```json если есть
    def _clean_json(t):
        # Извлекаем JSON-объект из текста (убираем возможные code fencing)
        start = t.find('{')
        end = t.rfind('}')
        if start != -1 and end != -1:
            return t[start:end+1]
        return t.strip()
    text = _clean_json(text)
    data = None
    # Попытка парсинга с регенерацией при неудаче
    for attempt in range(2):  # первая попытка и одна регенерация
        try:
            data = json.loads(text)
            break
        except Exception:
            # Повторный запрос для получения корректного JSON
            resp = send_chat_completion(
                api_endpoint=api_endpoint,
                model=model,
                messages=messages,
                max_tokens=settings.get("max_tokens", 200),
                temperature=0.3,
                api_key=api_key
            )
            text = _clean_json(get_completion_text(resp) or '')
    if not data:
        return {'score': 0, 'comment': 'Не удалось получить оценку'}
    score = int(data.get('score', 0))
    comment = data.get('comment', '')
    return {'score': score, 'comment': comment} 
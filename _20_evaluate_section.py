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
        {"role": "system", "content": "Ты - опытный преподаватель, оценивающий усвоение курса."},
        {"role": "user", "content": content}
    ]
    resp = send_chat_completion(
        api_endpoint=settings['api_endpoint'],
        model=settings['model'],
        messages=messages,
        max_tokens=200,
        temperature=0.3
    )
    text = get_completion_text(resp) or ''
    # Выделяем JSON из ответа
    try:
        # Если ответ в ```json, убираем метки
        if text.startswith('```'):
            text = text.strip('`')
        data = json.loads(text)
        score = int(data.get('score', 0))
        comment = data.get('comment', '')
    except Exception:
        # В случае ошибки возвращаем нулевую оценку
        score, comment = 0, 'Не удалось получить оценку'
    return {'score': score, 'comment': comment} 
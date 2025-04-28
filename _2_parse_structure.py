"""Модуль для разбора структуры книги на разделы по маркерам."""
import re
from typing import List, Dict, Any

def parse_structure(raw_text: str) -> List[Dict[str, Any]]:
    """Разбивает текст на разделы по маркерам -=раздел=-.
    
    Формат разметки:
    -=раздел=-
    Название раздела
    Текст раздела...
    
    Args:
        raw_text: Полный текст книги
        
    Returns:
        Список словарей, где каждый словарь содержит:
        - id: номер раздела (с 1)
        - title: заголовок (первая строка после маркера)
        - content: текст раздела
    """
    # Регулярное выражение для поиска разделов, обозначенных маркерами -=раздел=-
    section_pattern = r'-=\s*раздел\s*=-'
    
    # Находим все маркеры разделов
    section_matches = list(re.finditer(section_pattern, raw_text))
    
    if not section_matches:
        # Если маркеры не найдены, возвращаем весь текст как один раздел
        return [{
            'id': 1,
            'title': 'Основной текст',
            'content': raw_text.strip()
        }]
    
    sections = []
    
    # Обработка каждого раздела
    for i, match in enumerate(section_matches):
        section_id = i + 1
        
        # Определяем начало и конец содержимого раздела
        start_pos = match.end()
        if i < len(section_matches) - 1:
            end_pos = section_matches[i + 1].start()
        else:
            end_pos = len(raw_text)
        
        # Извлекаем содержимое раздела
        section_content = raw_text[start_pos:end_pos].strip()
        
        # Разделяем заголовок и текст раздела
        section_lines = section_content.splitlines()
        if section_lines:
            title = section_lines[0].strip()
            content = '\n'.join(section_lines[1:]).strip()
        else:
            title = f"Раздел {section_id}"
            content = ""
        
        sections.append({
            'id': section_id,
            'title': title,
            'content': content
        })
    
    return sections 
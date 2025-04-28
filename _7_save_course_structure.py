"""Модуль для сохранения структуры курса."""
import json
from typing import List, Dict, Any

def save_course_structure(structure_path: str, structure: List[Dict[str, Any]]) -> None:
    """Сохраняет структуру курса в JSON.
    
    Args:
        structure_path: Путь к файлу структуры курса
        structure: Список словарей, представляющих разделы курса
        
    Returns:
        None
        
    Raises:
        IOError: При ошибке записи файла
    """
    with open(structure_path, 'w', encoding='utf-8') as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)
    
    print(f"Структура курса успешно сохранена в {structure_path}") 
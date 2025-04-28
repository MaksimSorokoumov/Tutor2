"""Модуль для загрузки структуры курса."""
import json
import os
from typing import List, Dict, Any

def load_course_structure(structure_path: str) -> List[Dict[str, Any]]:
    """Загружает список разделов курса.
    
    Args:
        structure_path: Путь к файлу структуры курса
        
    Returns:
        Список словарей, представляющих разделы курса
        
    Raises:
        FileNotFoundError: Если файл структуры не найден
        json.JSONDecodeError: Если файл имеет некорректный формат JSON
    """
    if not os.path.exists(structure_path):
        raise FileNotFoundError(f"Файл структуры курса не найден: {structure_path}")
    
    with open(structure_path, 'r', encoding='utf-8') as f:
        return json.load(f) 
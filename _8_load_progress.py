"""Модуль для загрузки прогресса пользователя."""
import json
import os
from typing import Dict, Any

def load_progress(progress_path: str) -> Dict[str, Any]:
    """Загружает прогресс пользователя.
    
    Args:
        progress_path: Путь к файлу прогресса
        
    Returns:
        Словарь с прогрессом пользователя
        
    Raises:
        FileNotFoundError: Если файл прогресса не найден
        json.JSONDecodeError: Если файл имеет некорректный формат JSON
    """
    if not os.path.exists(progress_path):
        raise FileNotFoundError(f"Файл прогресса не найден: {progress_path}")
    
    with open(progress_path, 'r', encoding='utf-8') as f:
        return json.load(f) 
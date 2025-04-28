"""Модуль для сохранения прогресса пользователя."""
import json
from typing import Dict, Any

def save_progress(progress_path: str, progress: Dict[str, Any]) -> None:
    """Сохраняет прогресс пользователя.
    
    Args:
        progress_path: Путь к файлу прогресса
        progress: Словарь с прогрессом пользователя
        
    Returns:
        None
        
    Raises:
        IOError: При ошибке записи файла
    """
    with open(progress_path, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)
    
    print(f"Прогресс пользователя успешно сохранен в {progress_path}") 
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
        progress = json.load(f)
    
    # Проверяем и обновляем структуру, если необходимо
    if "sections" in progress:
        for section_id, section_data in progress["sections"].items():
            # Добавляем поле "answered", если его нет
            if "answered" not in section_data:
                section_data["answered"] = []
            # Добавляем историю упражнений и оценку, если их нет
            if "exercises" not in section_data:
                section_data["exercises"] = []
            if "evaluation" not in section_data:
                section_data["evaluation"] = {"score": None, "comment": ""}
                
    return progress 
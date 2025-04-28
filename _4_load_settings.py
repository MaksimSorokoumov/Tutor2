"""Модуль для загрузки настроек из JSON-файла."""
import json
import os
from typing import Dict, Any

def load_settings(settings_path: str) -> Dict[str, Any]:
    """Загружает настройки из JSON-файла.
    
    Args:
        settings_path: Путь к файлу настроек
        
    Returns:
        Словарь с настройками
        
    Raises:
        FileNotFoundError: Если файл настроек не найден
        json.JSONDecodeError: Если файл настроек имеет некорректный формат JSON
    """
    if not os.path.exists(settings_path):
        # Если файл не существует, возвращаем настройки по умолчанию
        default_settings = {
            "api_endpoint": "http://localhost:1234/v1",
            "model": "local",
            "max_tokens": 8000,
            "temperature": 0.5,
            "detail_level": "средний",
            "difficulty": "средний"
        }
        
        # Сохраняем настройки по умолчанию
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, ensure_ascii=False, indent=2)
        
        print(f"Файл настроек не найден. Создан файл с настройками по умолчанию: {settings_path}")
        return default_settings
    
    # Загружаем настройки из файла
    with open(settings_path, 'r', encoding='utf-8') as f:
        return json.load(f) 
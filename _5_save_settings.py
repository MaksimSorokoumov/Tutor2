"""Модуль для сохранения настроек в JSON-файл."""
import json
from typing import Dict, Any

def save_settings(settings_path: str, settings: Dict[str, Any]) -> None:
    """Сохраняет настройки в JSON-файл.
    
    Args:
        settings_path: Путь к файлу настроек
        settings: Словарь с настройками для сохранения
        
    Returns:
        None
        
    Raises:
        IOError: При ошибке записи файла
    """
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
    
    print(f"Настройки успешно сохранены в {settings_path}") 
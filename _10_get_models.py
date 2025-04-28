"""Модуль для получения списка доступных моделей через API."""
import requests
from typing import List
import json

def get_models(api_endpoint: str) -> List[str]:
    """Получает список моделей через API.
    
    Args:
        api_endpoint: Базовый URL API (например, http://localhost:1234/v1)
        
    Returns:
        Список названий доступных моделей
        
    Raises:
        requests.RequestException: При ошибке соединения или запроса
        ValueError: При ошибке в формате ответа
    """
    # Формируем полный URL для запроса списка моделей
    models_url = f"{api_endpoint}/models"
    
    try:
        # Отправляем GET-запрос
        response = requests.get(models_url, timeout=5)
        response.raise_for_status()  # Вызовет исключение при ошибках HTTP
        
        # Парсим ответ
        data = response.json()
        
        # Проверяем структуру ответа и извлекаем названия моделей
        if 'data' in data and isinstance(data['data'], list):
            # Формат, совместимый с OpenAI API
            return [model['id'] for model in data['data']]
        elif isinstance(data, list):
            # Альтернативный формат (просто список моделей)
            return [model['id'] if isinstance(model, dict) and 'id' in model else model 
                   for model in data]
        else:
            # Неизвестный формат
            raise ValueError(f"Неизвестный формат ответа API: {data}")
    
    except requests.RequestException as e:
        print(f"Ошибка соединения с API: {e}")
        return ["local"]  # Возвращаем хотя бы локальную модель по умолчанию
    
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Ошибка разбора ответа API: {e}")
        return ["local"] 
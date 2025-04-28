"""Модуль для отправки запросов к API чат-модели."""
import requests
import json
from typing import List, Dict, Any, Optional

def send_chat_completion(
    api_endpoint: str,
    model: str,
    messages: List[Dict[str, str]],
    max_tokens: int,
    temperature: float
) -> Dict[str, Any]:
    """Отправляет сообщения модели через API.
    
    Args:
        api_endpoint: Базовый URL API (например, http://localhost:1234/v1)
        model: Название модели
        messages: Список сообщений в формате [{role: "system|user|assistant", content: "текст"}]
        max_tokens: Максимальное количество токенов в ответе
        temperature: Температура (креативность) от 0.0 до 1.0
        
    Returns:
        Словарь с ответом от API
        
    Raises:
        requests.RequestException: При ошибке соединения или запроса
        ValueError: При ошибке в формате ответа
    """
    # Формируем полный URL для запроса
    completion_url = f"{api_endpoint}/chat/completions"
    
    # Формируем тело запроса
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    # Заголовки запроса
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Отправляем POST-запрос
        response = requests.post(
            completion_url, 
            data=json.dumps(payload), 
            headers=headers,
            timeout=120  # Увеличенный таймаут (2 минуты)
        )
        response.raise_for_status()  # Вызовет исключение при ошибках HTTP
        
        # Возвращаем ответ
        return response.json()
    
    except requests.RequestException as e:
        print(f"Ошибка при отправке запроса к API: {e}")
        raise
    
    except json.JSONDecodeError as e:
        print(f"Ошибка разбора ответа API: {e}")
        raise ValueError(f"Некорректный формат ответа API: {response.text}")

def get_completion_text(response: Dict[str, Any]) -> Optional[str]:
    """Извлекает текст ответа из структуры ответа API.
    
    Args:
        response: Словарь с ответом от API
        
    Returns:
        Текст ответа или None, если структура ответа некорректна
    """
    try:
        # Проверяем ключи в соответствии с форматом OpenAI API
        if 'choices' in response and len(response['choices']) > 0:
            choice = response['choices'][0]
            
            # Формат может различаться в зависимости от API
            if 'message' in choice and 'content' in choice['message']:
                # Стандартный формат OpenAI
                return choice['message']['content']
            elif 'text' in choice:
                # Альтернативный формат
                return choice['text']
        
        print(f"Неизвестный формат ответа API: {response}")
        return None
    
    except Exception as e:
        print(f"Ошибка при извлечении текста из ответа: {e}")
        return None 
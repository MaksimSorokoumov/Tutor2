"""Модуль для логирования ошибок приложения."""
import logging
import traceback
import os
from datetime import datetime

def configure_logger():
    """Настраивает логгер приложения."""
    # Создаем логгер
    logger = logging.getLogger('tutor')
    logger.setLevel(logging.DEBUG)
    
    # Если логгер уже настроен, не добавляем обработчики повторно
    if logger.handlers:
        return logger
    
    # Формат сообщений лога
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Обработчик для файла
    file_handler = logging.FileHandler('tutor.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)  # Только ошибки в консоль
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_error(error: Exception) -> None:
    """Записывает ошибки в файл tutor.log.
    
    Args:
        error: Объект исключения
        
    Returns:
        None
    """
    logger = configure_logger()
    
    # Получаем трассировку стека
    stack_trace = traceback.format_exc()
    
    # Логируем ошибку
    logger.error(f"Произошла ошибка: {str(error)}")
    logger.error(f"Трассировка стека:\n{stack_trace}")
    
    print(f"Ошибка записана в лог-файл: tutor.log")

def log_info(message: str) -> None:
    """Записывает информационное сообщение в лог.
    
    Args:
        message: Текст сообщения
        
    Returns:
        None
    """
    logger = configure_logger()
    logger.info(message)

def log_warning(message: str) -> None:
    """Записывает предупреждение в лог.
    
    Args:
        message: Текст предупреждения
        
    Returns:
        None
    """
    logger = configure_logger()
    logger.warning(message)

def log_debug(message: str) -> None:
    """Записывает отладочное сообщение в лог.
    
    Args:
        message: Текст отладочного сообщения
        
    Returns:
        None
    """
    logger = configure_logger()
    logger.debug(message) 
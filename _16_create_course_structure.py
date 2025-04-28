"""Модуль для создания структуры курса на основе загруженной книги."""

import os
import tempfile
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from _3_initialize_course import initialize_course
from _6_load_course_structure import load_course_structure
from _15_log_error import log_error

def create_course_structure(parent, current_text):
    """Создает структуру курса на основе загруженной книги.
    
    Args:
        parent: Родительское окно для диалогов
        current_text: Текст книги
        
    Returns:
        tuple: (bool, str, list) - Успех операции, путь к директории курса, структура курса
    """
    if not current_text:
        QMessageBox.warning(parent, "Предупреждение", "Сначала загрузите книгу")
        return False, "", []
        
    # Запрашиваем директорию для сохранения курса
    directory = QFileDialog.getExistingDirectory(parent, "Выберите директорию для сохранения курса")
    
    if not directory:
        return False, "", []  # Пользователь отменил выбор
        
    try:
        # Создаем временный файл с текущим текстом
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(current_text)
            temp_path = temp_file.name
            
        # Инициализируем курс
        initialize_course(temp_path, directory)
        
        # Удаляем временный файл
        os.unlink(temp_path)
        
        # Показываем сообщение об успехе
        QMessageBox.information(parent, "Информация", f"Структура курса успешно создана в директории {directory}")
        
        # Загружаем созданную структуру
        structure_path = os.path.join(directory, "structure.json")
        structure = load_course_structure(structure_path)
        
        return True, directory, structure
            
    except Exception as e:
        log_error(e)
        QMessageBox.critical(parent, "Ошибка", f"Не удалось создать структуру курса: {str(e)}")
        return False, "", [] 
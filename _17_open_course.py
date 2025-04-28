"""Модуль для открытия существующего курса."""

import os
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from _6_load_course_structure import load_course_structure
from _15_log_error import log_error

def open_course(parent):
    """Открывает созданный курс.
    
    Args:
        parent: Родительское окно для диалогов
        
    Returns:
        tuple: (bool, str, list) - Успех операции, путь к директории курса, структура курса
    """
    # Запрашиваем директорию курса
    directory = QFileDialog.getExistingDirectory(parent, "Выберите директорию курса")
    
    if not directory:
        return False, "", []  # Пользователь отменил выбор
    
    try:
        # Проверяем наличие файла structure.json
        structure_path = os.path.join(directory, "structure.json")
        
        if not os.path.exists(structure_path):
            QMessageBox.warning(parent, "Предупреждение", f"Файл структуры курса не найден: {structure_path}")
            return False, "", []
        
        # Загружаем структуру курса
        structure = load_course_structure(structure_path)
        
        return True, directory, structure
        
    except Exception as e:
        log_error(e)
        QMessageBox.critical(parent, "Ошибка", f"Не удалось открыть курс: {str(e)}")
        return False, "", [] 
"""Модуль для открытия существующего курса."""

import os
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from _6_load_course_structure import load_course_structure
from _8_load_progress import load_progress
from _15_log_error import log_error
from _9_save_progress import save_progress

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
        
        # Загружаем прогресс пользователя
        progress_path = os.path.join(directory, "progress.json")
        try:
            progress = load_progress(progress_path)
            parent.progress = progress
        except Exception as e:
            log_error(f"Ошибка при загрузке прогресса: {str(e)}")
            # Создаем пустой прогресс если файл не найден
            parent.progress = {"sections": {}}
            for section in structure:
                section_id = section["id"]
                parent.progress["sections"][str(section_id)] = {
                    "completed": False,
                    "exercises_completed": 0,
                    "last_viewed": None,
                    "answered": [],
                    "exercises": [],           # история ответов
                    "evaluation": {"score": None, "comment": ""}  # оценка раздела
                }
            # Сохраняем новый прогресс
            save_progress(progress_path, parent.progress)
        
        # Запоминаем этот курс в настройках
        add_course_to_recent(directory, parent.settings)
        
        return True, directory, structure
        
    except Exception as e:
        log_error(e)
        QMessageBox.critical(parent, "Ошибка", f"Не удалось открыть курс: {str(e)}")
        return False, "", []

def add_course_to_recent(course_path, settings):
    """Добавляет курс в список последних курсов в настройках.
    
    Args:
        course_path: Путь к директории курса
        settings: Словарь настроек приложения
        
    Returns:
        None
    """
    # Проверяем наличие настроек для последних курсов
    if 'recent_courses' not in settings:
        settings['recent_courses'] = []
    
    # Удаляем этот курс из списка, если он там уже есть
    if course_path in settings['recent_courses']:
        settings['recent_courses'].remove(course_path)
    
    # Добавляем курс в начало списка
    settings['recent_courses'].insert(0, course_path)
    
    # Ограничиваем список 10 последними курсами
    if len(settings['recent_courses']) > 10:
        settings['recent_courses'] = settings['recent_courses'][:10]
    
    # Сохраняем настройки
    from _5_save_settings import save_settings
    save_settings("settings.json", settings) 
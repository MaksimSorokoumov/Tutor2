"""Модуль для основного окна приложения (MainWindow)."""
import os
from PyQt5.QtWidgets import QAction, QMenu
from typing import List, Dict, Any

def find_available_courses(courses_dir: str = "courses") -> List[Dict[str, Any]]:
    """Находит все доступные курсы в указанной директории.
    
    Args:
        courses_dir: Директория с курсами (по умолчанию 'courses')
        
    Returns:
        Список словарей с информацией о найденных курсах
    """
    courses = []
    
    # Проверяем существование директории
    if not os.path.exists(courses_dir):
        return courses
    
    # Перебираем все поддиректории
    for item in os.listdir(courses_dir):
        course_dir = os.path.join(courses_dir, item)
        
        # Если это директория и в ней есть structure.json
        if os.path.isdir(course_dir) and os.path.exists(os.path.join(course_dir, "structure.json")):
            # Получаем имя курса (имя папки)
            course_name = os.path.basename(item)
            
            courses.append({
                "name": course_name,
                "path": course_dir
            })
    
    return courses

def update_courses_menu(main_window) -> None:
    """Обновляет меню курсов в меню 'Файл'.
    
    Args:
        main_window: Экземпляр главного окна приложения
    """
    # Находим подменю курсов или создаем новое
    if hasattr(main_window, 'courses_menu'):
        main_window.courses_menu.clear()
    else:
        main_window.courses_menu = QMenu("Последние курсы", main_window)
        # Вставляем подменю курсов после пункта "Открыть курс..."
        file_menu = main_window.menuBar().findChild(QMenu, "file_menu")
        if file_menu:
            # Находим действие "Открыть курс..."
            for action in file_menu.actions():
                if action.text() == "Открыть курс...":
                    # Вставляем подменю после этого действия
                    file_menu.insertMenu(file_menu.actions()[file_menu.actions().index(action) + 1], 
                                        main_window.courses_menu)
                    # Добавляем разделитель после подменю
                    file_menu.insertSeparator(file_menu.actions()[file_menu.actions().index(main_window.courses_menu.menuAction()) + 1])
                    break
    
    # Проверяем наличие последних курсов в настройках
    recent_courses = []
    if hasattr(main_window, 'settings') and 'recent_courses' in main_window.settings:
        recent_courses = main_window.settings['recent_courses']
    
    # Если нет последних курсов, пытаемся найти доступные курсы
    if not recent_courses:
        courses = find_available_courses()
        
        # Если курсы не найдены
        if not courses:
            no_courses_action = QAction("Нет доступных курсов", main_window)
            no_courses_action.setEnabled(False)
            main_window.courses_menu.addAction(no_courses_action)
            return
            
        # Добавляем найденные курсы
        for course in courses:
            course_action = QAction(course["name"], main_window)
            course_action.setData(course["path"])
            course_action.triggered.connect(lambda checked, path=course["path"]: main_window.open_course_by_path(path))
            main_window.courses_menu.addAction(course_action)
    else:
        # Добавляем действия для каждого курса из недавно открытых
        for course_path in recent_courses:
            # Проверяем, что директория существует
            if not os.path.exists(course_path):
                continue
                
            # Проверяем, что это действительно курс
            if not os.path.exists(os.path.join(course_path, "structure.json")):
                continue
                
            # Получаем имя курса из имени директории
            course_name = os.path.basename(course_path)
                
            course_action = QAction(course_name, main_window)
            course_action.setData(course_path)
            course_action.triggered.connect(lambda checked, path=course_path: main_window.open_course_by_path(path))
            main_window.courses_menu.addAction(course_action)
        
        # Если после фильтрации не осталось курсов
        if main_window.courses_menu.isEmpty():
            no_courses_action = QAction("Нет доступных курсов", main_window)
            no_courses_action.setEnabled(False)
            main_window.courses_menu.addAction(no_courses_action)

def open_course_by_path(main_window, course_path: str) -> None:
    """Открывает курс по указанному пути.
    
    Args:
        main_window: Экземпляр главного окна приложения
        course_path: Путь к директории курса
    """
    try:
        from _6_load_course_structure import load_course_structure
        from _8_load_progress import load_progress
        
        # Проверяем, что директория существует
        if not os.path.exists(course_path):
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "Предупреждение", f"Директория курса не найдена: {course_path}")
            return
            
        # Загружаем структуру курса
        structure_path = os.path.join(course_path, "structure.json")
        structure = load_course_structure(structure_path)
        
        # Загружаем прогресс пользователя
        progress_path = os.path.join(course_path, "progress.json")
        try:
            progress = load_progress(progress_path)
            main_window.progress = progress
        except Exception as e:
            from _15_log_error import log_error
            log_error(f"Ошибка при загрузке прогресса: {str(e)}")
            # Создаем пустой прогресс если файл не найден
            main_window.progress = {"sections": {}}
            for section in structure:
                section_id = section["id"]
                main_window.progress["sections"][str(section_id)] = {
                    "completed": False,
                    "exercises_completed": 0,
                    "last_viewed": None,
                    "answered": []
                }
        
        # Устанавливаем текущую директорию курса
        main_window.current_course_dir = course_path
        main_window.current_course_structure = structure
        
        # Отображаем первый раздел, если он есть
        if structure and len(structure) > 0:
            main_window.display_section(structure[0])
        
    except Exception as e:
        from _15_log_error import log_error
        from PyQt5.QtWidgets import QMessageBox
        log_error(e)
        QMessageBox.critical(main_window, "Ошибка", f"Не удалось открыть курс: {str(e)}") 
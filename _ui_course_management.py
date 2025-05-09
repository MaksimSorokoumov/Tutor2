"""Модуль для управления курсами в приложении."""

import os
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from _15_log_error import log_error, log_info
from _16_create_course_structure import create_course_structure as create_struct
from _17_open_course import open_course as open_course_func
from _18_select_section import select_section, get_course_sections

def create_course_structure(parent):
    """Создает структуру курса на основе загруженной книги.
    
    Args:
        parent: Родительское окно для диалогов
        
    Returns:
        bool: Успешность операции
    """
    try:
        # Проверяем, загружен ли текст
        if not parent.current_text:
            QMessageBox.warning(parent, "Предупреждение", "Сначала нужно загрузить книгу!")
            return False
            
        # Запрашиваем директорию для сохранения структуры курса
        directory = QFileDialog.getExistingDirectory(parent, "Выберите директорию для сохранения курса")
        
        if not directory:
            return False  # Пользователь отменил выбор
            
        # Запрашиваем название курса
        from PyQt5.QtWidgets import QInputDialog
        course_name, ok = QInputDialog.getText(parent, "Название курса", "Введите название курса:")
        
        if not ok or not course_name:
            return False  # Пользователь отменил ввод или не ввел название
            
        # Создаем директорию курса
        course_dir = os.path.join(directory, course_name)
        if not os.path.exists(course_dir):
            os.makedirs(course_dir)
            
        # Создаем структуру курса
        structure = create_struct(parent.current_text)
        
        # Сохраняем структуру в JSON
        structure_path = os.path.join(course_dir, "structure.json")
        import json
        with open(structure_path, 'w', encoding='utf-8') as f:
            json.dump(structure, f, ensure_ascii=False, indent=2)
            
        # Сохраняем текст курса
        text_path = os.path.join(course_dir, "content.txt")
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(parent.current_text)
            
        # Создаем директорию для прогресса
        progress_dir = os.path.join(course_dir, "progress")
        if not os.path.exists(progress_dir):
            os.makedirs(progress_dir)
            
        # Устанавливаем текущую директорию курса
        parent.current_course_dir = course_dir
        parent.current_course_structure = structure
        
        # Отображаем первый раздел
        if structure and len(structure) > 0:
            display_section(parent, structure[0])
            
        QMessageBox.information(
            parent, 
            "Информация", 
            f"Курс '{course_name}' успешно создан в {course_dir}\n"
            f"Курс содержит {len(structure)} разделов.")
            
        # Запоминаем этот курс в настройках
        from _17_open_course import add_course_to_recent
        add_course_to_recent(course_dir, parent.settings)
        
        return True
            
    except Exception as e:
        log_error(e)
        QMessageBox.critical(parent, "Ошибка", f"Не удалось создать структуру курса: {str(e)}")
        return False

def open_course(parent):
    """Открывает созданный курс.
    
    Args:
        parent: Родительское окно для диалогов
        
    Returns:
        tuple: (bool, str, list) - Успех операции, путь к директории курса, структура курса
    """
    return open_course_func(parent)

def display_section(parent, section):
    """Отображает содержимое раздела в интерфейсе.
    
    Args:
        parent: Родительское окно
        section: Словарь с информацией о разделе
        
    Returns:
        None
    """
    try:
        # Сохраняем текущий раздел
        parent.current_section = section
        
        # Отображаем текст раздела
        parent.text_edit.setText(section["content"])
        parent.current_text = section["content"]
        
        # Устанавливаем заголовок текста
        parent.text_label.setText(f"Раздел {section['id']}: {section['title']}")
        
        # Очищаем объяснение и упражнение
        parent.explanation_edit.clear()
        parent.current_explanation = ""
        parent.exercise_edit.clear()
        parent.answer_edit.clear()
        parent.result_edit.clear()
        
        # Сбрасываем текущий этап на первый
        parent.current_stage = 0
        parent.update_stage_text()
        
        # Изменяем функцию кнопки "Следующий этап" на переход к следующему разделу после третьего этапа
        if parent.current_stage == 2:
            parent.next_stage_btn.setText("Следующий раздел")
            try:
                parent.next_stage_btn.clicked.disconnect()
            except:
                pass
            parent.next_stage_btn.clicked.connect(parent.open_next_section)
            
        log_info(f"Загружен раздел {section['id']}: {section['title']}")
        
    except Exception as e:
        log_error(e)
        QMessageBox.critical(parent, "Ошибка", f"Не удалось отобразить раздел: {str(e)}")

def create_new_course(parent):
    """Создает новый курс в одно действие (открытие книги + создание структуры).
    
    Args:
        parent: Родительское окно для диалогов
        
    Returns:
        bool: Успешность операции
    """
    try:
        # Открываем книгу
        from _ui_text_processing import open_book
        if not open_book(parent):
            return False
            
        # Создаем структуру курса
        return create_course_structure(parent)
            
    except Exception as e:
        log_error(e)
        QMessageBox.critical(parent, "Ошибка", f"Не удалось создать новый курс: {str(e)}")
        return False 
"""Модуль для UI-функций управления курсами: создание, открытие, отображение разделов."""

import os
from PyQt5.QtWidgets import QMessageBox, QFileDialog

# Импортируем необходимые функции из других модулей
from _16_create_course_structure import create_course_structure as create_structure_backend
from _17_open_course import open_course as open_course_backend
from _18_select_section import select_section
from _8_load_progress import load_progress
from _15_log_error import log_error
from _1_load_book import load_book
from _3_initialize_course import initialize_course

def display_section(window, section):
    """Отображает содержимое раздела в интерфейсе главного окна."""
    window.current_section = section
    window.text_edit.setText(section['content'])
    window.current_text = section['content']
    window.explanation_edit.clear()
    window.exercise_edit.clear()
    window.answer_edit.clear()
    window.result_edit.clear()
    
    # Обновляем заголовок окна
    window.setWindowTitle(f"Tutor - {section['title']}")
    
    QMessageBox.information(window, "Информация", f"Открыт раздел: {section['title']}")

def create_course_structure(window):
    """Создает структуру курса на основе загруженной книги через UI."""
    success, directory, structure = create_structure_backend(window, window.current_text)
    
    if success and structure:
        # Сохраняем структуру и загружаем прогресс
        window.current_course_dir = directory
        window.current_course_structure = structure
        window.progress = load_progress(os.path.join(directory, "progress.json"))
        window.current_section = None
        
        # Предлагаем открыть первый раздел
        reply = QMessageBox.question(
            window, 
            "Открыть раздел", 
            "Структура курса создана. Хотите открыть первый раздел?", 
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes and len(structure) > 0:
            display_section(window, structure[0])

def open_course(window):
    """Открывает созданный курс через UI."""
    success, directory, structure = open_course_backend(window)
    
    if success and structure:
        # Сохраняем структуру и загружаем прогресс
        window.current_course_dir = directory
        window.current_course_structure = structure
        window.progress = load_progress(os.path.join(directory, "progress.json"))
        window.current_section = None
        
        # Показываем диалог выбора раздела
        selected_section = select_section(window, structure)
        
        if selected_section:
            display_section(window, selected_section)

def create_new_course(window):
    """Создает новый курс в одно действие (открытие книги + создание структуры) через UI."""
    file_path, _ = QFileDialog.getOpenFileName(
        window, "Открыть книгу для создания курса", "", 
        "Текстовые файлы (*.txt);;Word документы (*.docx);;Все файлы (*.*)"
    )
    
    if not file_path:
        return  # Пользователь отменил выбор книги
        
    try:
        # Загружаем книгу
        text = load_book(file_path)
        window.text_edit.setText(text)
        window.current_text = text
        window.explanation_edit.clear()
        window.exercise_edit.clear()
        window.answer_edit.clear()
        window.result_edit.clear()
        
        # Запрашиваем директорию для сохранения курса
        directory = QFileDialog.getExistingDirectory(
            window, "Выберите директорию для сохранения курса"
        )
        
        if not directory:
            return  # Пользователь отменил выбор директории
        
        # Используем initialize_course для создания структуры курса
        initialize_course(file_path, directory)
        
        # Используем open_course для загрузки созданного курса
        # (переиспользуем логику open_course, т.к. она уже загружает структуру и прогресс)
        success, loaded_directory, structure = open_course_backend(window, directory) # Передаем директорию явно
        
        if success and structure:
            # Сохраняем данные в окне
            window.current_course_dir = loaded_directory
            window.current_course_structure = structure
            window.progress = load_progress(os.path.join(loaded_directory, "progress.json"))
            window.current_section = None
            
            QMessageBox.information(
                window, "Информация", 
                f"Курс успешно создан на основе книги:\n{file_path}\n\nСтруктура сохранена в:\n{loaded_directory}"
            )
            
            # Предлагаем открыть первый раздел
            if structure:
                reply = QMessageBox.question(
                    window, 
                    "Открыть раздел", 
                    "Структура курса создана. Хотите открыть первый раздел?", 
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes and len(structure) > 0:
                    display_section(window, structure[0])
                
    except Exception as e:
        log_error(e)
        QMessageBox.critical(window, "Ошибка", f"Не удалось создать курс: {str(e)}") 
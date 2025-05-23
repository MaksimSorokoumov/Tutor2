"""Модуль для выбора раздела курса."""

import os
import json
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox
from _15_log_error import log_error

def get_course_sections(course_dir):
    """Получает список разделов курса из его директории.
    
    Args:
        course_dir: Путь к директории курса
        
    Returns:
        list: Список разделов курса (каждый раздел - словарь)
    """
    try:
        structure_file = os.path.join(course_dir, "structure.json")
        
        if not os.path.exists(structure_file):
            return []
        
        with open(structure_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log_error(f"Ошибка при загрузке структуры курса: {str(e)}")
        return []

def select_section(parent, course_structure):
    """Показывает диалог выбора раздела курса.
    
    Args:
        parent: Родительское окно для диалогов
        course_structure: Структура курса (список разделов)
        
    Returns:
        dict: Выбранный раздел или None, если отменено
    """
    if not course_structure:
        QMessageBox.warning(parent, "Предупреждение", "Структура курса пуста")
        return None
    
    # Создаем диалог выбора раздела
    dialog = QDialog(parent)
    dialog.setWindowTitle("Выбор раздела курса")
    dialog.setMinimumWidth(500)
    dialog.setMinimumHeight(400)  # Увеличиваем высоту для списка с прокруткой
    
    layout = QVBoxLayout()
    
    # Добавляем заголовок
    layout.addWidget(QLabel("Выберите раздел:"))
    
    # Создаем список разделов с прокруткой
    section_list = QListWidget()
    section_list.setAlternatingRowColors(True)  # Чередующиеся цвета для улучшения читаемости
    
    # Заполняем список разделов
    for section in course_structure:
        # Получаем оценку раздела (может быть 0 или None)
        sid = str(section['id'])
        score = None
        if hasattr(parent, 'progress') and sid in parent.progress.get('sections', {}):
            score = parent.progress['sections'][sid].get('evaluation', {}).get('score')
        # Отображаем оценку или '-' если нет
        display_score = score if score is not None else '-'
        section_list.addItem(f"{section['id']}. {section['title']} (Оценка: {display_score})")
    
    # Сохраняем исходные данные в свойстве списка
    section_list.setProperty("sections", course_structure)
    
    layout.addWidget(section_list)
    
    # Кнопки
    buttons_layout = QHBoxLayout()
    open_btn = QPushButton("Открыть")
    cancel_btn = QPushButton("Отмена")
    
    buttons_layout.addWidget(open_btn)
    buttons_layout.addWidget(cancel_btn)
    
    layout.addLayout(buttons_layout)
    dialog.setLayout(layout)
    
    # Привязываем события
    open_btn.clicked.connect(dialog.accept)
    cancel_btn.clicked.connect(dialog.reject)
    section_list.doubleClicked.connect(dialog.accept)  # Двойной клик тоже открывает раздел
    
    # Показываем диалог
    if dialog.exec_() == QDialog.Accepted:
        # Получаем выбранный раздел
        current_index = section_list.currentRow()
        
        if current_index >= 0 and current_index < len(course_structure):
            return course_structure[current_index]
        else:
            QMessageBox.warning(parent, "Предупреждение", "Не выбран раздел курса")
            return None
    
    return None  # Отмена выбора 
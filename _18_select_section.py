"""Модуль для выбора раздела курса."""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox
from _15_log_error import log_error

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
        section_list.addItem(f"{section['id']}. {section['title']}")
    
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
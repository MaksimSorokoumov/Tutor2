"""Модуль для управления контейнером упражнений."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy, 
    QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Импортируем компоненты из других модулей
from _ui_exercise_generation_components import ZoomableScrollArea

def clear_exercise_container(window):
    """Очищает контейнер с упражнениями."""
    # Удаляем все виджеты из контейнера упражнений
    if hasattr(window, 'exercise_container'):
        # Удаляем все дочерние виджеты
        for i in reversed(range(window.exercise_container.layout().count())):
            widget = window.exercise_container.layout().itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

def create_exercise_container(window):
    """Создает контейнер для упражнений, если его еще нет."""
    if not hasattr(window, 'exercise_container'):
        # Создаем контейнер для упражнений с вертикальным макетом
        window.exercise_container = QWidget()
        exercise_container_layout = QVBoxLayout(window.exercise_container)
        exercise_container_layout.setSpacing(15)  # Увеличиваем расстояние между элементами
        # Устанавливаем поля макета
        exercise_container_layout.setContentsMargins(10, 10, 10, 10)
        window.exercise_container.setLayout(exercise_container_layout)
        
        # Устанавливаем политику размеров для контейнера
        window.exercise_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Добавляем контейнер в область прокрутки с поддержкой масштабирования
        window.exercise_scroll_area = ZoomableScrollArea()
        window.exercise_scroll_area.setWidget(window.exercise_container)
        
        # Получаем родительский виджет для exercise_edit
        parent_layout = None
        for child in window.findChildren(QWidget):
            if child.layout():
                for i in range(child.layout().count()):
                    item = child.layout().itemAt(i)
                    if item and item.widget() == window.exercise_edit:
                        parent_layout = child.layout()
                        break
                if parent_layout:
                    break
        
        if parent_layout:
            # Вставляем область прокрутки сразу после exercise_edit
            for i in range(parent_layout.count()):
                item = parent_layout.itemAt(i)
                if item and item.widget() == window.exercise_edit:
                    parent_layout.insertWidget(i + 1, window.exercise_scroll_area)
                    break
        else:
            # Не смогли найти родительский layout, выводим сообщение об ошибке
            window.exercise_edit.setText("Ошибка: не удалось найти родительский layout для exercise_edit")
            return
        
        # В зависимости от текущего этапа, настраиваем видимость элементов
        if window.current_stage < 2:  # Тесты
            # Скрываем поле для ввода ответа и комментария
            window.answer_edit.hide()
            
            # Находим и скрываем метку "Ваш ответ:"
            for label in window.findChildren(QLabel):
                if label.text() == "Ваш ответ:":
                    label.hide()
                    break
                    
            # Скрываем поле "Результат проверки"
            window.result_label.hide()
            window.result_edit.hide()
            
            # Показываем область прокрутки
            window.exercise_scroll_area.show()
        else:  # Открытые вопросы
            # Скрываем область прокрутки
            window.exercise_scroll_area.hide()
            
            # Показываем поля для ввода и результатов
            window.exercise_edit.show()
            window.exercise_edit.setReadOnly(True)
            window.answer_edit.show()
            window.result_label.show()
            window.result_edit.show()
            
            # Показываем метку "Ваш ответ:"
            for label in window.findChildren(QLabel):
                if label.text() == "Ваш ответ:":
                    label.show()
                    break 
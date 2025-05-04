"""Модуль с компонентами UI для генерации и проверки упражнений."""

from PyQt5.QtWidgets import QScrollArea, QLabel, QRadioButton, QCheckBox, QPushButton, QFrame, QSizePolicy, QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class ZoomableScrollArea(QScrollArea):
    """Область прокрутки с поддержкой масштабирования (Ctrl+колесо мыши)."""
    
    def __init__(self, parent=None):
        super(ZoomableScrollArea, self).__init__(parent)
        self.zoom_factor = 1.0
        self.setWidgetResizable(True)
        # Включаем горизонтальную прокрутку при необходимости
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # Устанавливаем политику размеров для области прокрутки
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Минимальная ширина, чтобы элементы не сжимались слишком сильно
        self.setMinimumWidth(200)

    def wheelEvent(self, event):
        """Обрабатывает событие прокрутки колеса мыши."""
        # Если нажата клавиша Ctrl, масштабируем содержимое
        if event.modifiers() & Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                # Увеличиваем масштаб
                self.zoom_factor += 0.1
                if self.zoom_factor > 3.0:
                    self.zoom_factor = 3.0
            else:
                # Уменьшаем масштаб
                self.zoom_factor -= 0.1
                if self.zoom_factor < 0.5:
                    self.zoom_factor = 0.5
            
            # Применяем масштаб к содержимому
            self.apply_zoom()
            event.accept()
        else:
            # Обычная прокрутка
            super(ZoomableScrollArea, self).wheelEvent(event)
    
    def apply_zoom(self):
        """Применяет масштаб к содержимому."""
        if not self.widget():
            return
        
        # Масштабируем все виджеты внутри контейнера
        self._apply_zoom_to_widget_and_children(self.widget())
        
    def _apply_zoom_to_widget_and_children(self, widget):
        """Рекурсивно применяет масштаб к виджету и всем его дочерним элементам."""
        # Устанавливаем размер шрифта для текущего виджета
        font = widget.font()
        font.setPointSize(int(10 * self.zoom_factor))
        widget.setFont(font)
        
        # Масштабируем размеры карточек, если это QFrame
        if isinstance(widget, QFrame):
            # Получаем текущие минимальные размеры
            min_width = widget.minimumWidth()
            min_height = widget.minimumHeight()
            
            # Если у виджета есть установленные минимальные размеры, масштабируем их
            if min_width > 0 and min_height > 0:
                base_min_width = min_width / self.zoom_factor  # расчет базового размера
                base_min_height = min_height / self.zoom_factor
                
                # Устанавливаем новые размеры с учетом масштаба
                widget.setMinimumWidth(int(base_min_width * self.zoom_factor))
                widget.setMinimumHeight(int(base_min_height * self.zoom_factor))
        
        # Применяем изменения к дочерним виджетам
        for child in widget.findChildren(QWidget):
            child_font = child.font()
            child_font.setPointSize(int(10 * self.zoom_factor))
            child.setFont(child_font)
            
            # Специфические стили для разных типов виджетов
            if isinstance(child, QLabel):
                # Проверяем, содержит ли метка HTML-форматирование
                if child.text().startswith("<") and ">" in child.text():
                    # Если это HTML, не меняем оригинальный текст, а добавляем стиль для размера шрифта
                    current_text = child.text()
                    if "style=" in current_text:
                        # Если уже есть стиль, добавляем в него font-size
                        child.setText(current_text.replace("style=\"", f"style=\"font-size: {int(10 * self.zoom_factor)}pt; "))
                    else:
                        # Если стиля нет, добавляем новый атрибут style
                        first_tag_end = current_text.find(">")
                        if first_tag_end > 0:
                            new_text = current_text[:first_tag_end] + f" style=\"font-size: {int(10 * self.zoom_factor)}pt;\"" + current_text[first_tag_end:]
                            child.setText(new_text)
                # Специальная обработка для меток с вопросами
                elif "Вопрос" in child.text():
                    # Извлекаем номер вопроса из текста
                    try:
                        parts = child.text().split(":")
                        if len(parts) > 1:
                            question_num = parts[0].strip()
                            question_text = ":".join(parts[1:]).strip()
                            # Создаем новый текст с HTML-форматированием и масштабированием
                            new_text = f"<span style='font-size: {int(11 * self.zoom_factor)}pt; font-weight: bold;'>{question_num}:</span> {question_text}"
                            child.setText(new_text)
                            child.setTextFormat(Qt.RichText)
                    except Exception:
                        # Если что-то пошло не так, оставляем текст как есть
                        pass
            elif isinstance(child, (QRadioButton, QCheckBox)):
                child.setStyleSheet(f"""
                    QRadioButton, QCheckBox {{
                        font-size: {int(10 * self.zoom_factor)}pt;
                        padding: 3px;
                        margin-right: 10px;
                    }}
                """)
            elif isinstance(child, QPushButton):
                child.setStyleSheet(f"""
                    QPushButton {{
                        font-size: {int(10 * self.zoom_factor)}pt;
                    }}
                """)
            
            # Масштабируем размеры карточек
            if isinstance(child, QFrame):
                # Получаем текущие минимальные размеры
                min_width = child.minimumWidth()
                min_height = child.minimumHeight()
                
                # Если у виджета есть установленные минимальные размеры, масштабируем их
                if min_width > 0 and min_height > 0:
                    base_min_width = min_width / self.zoom_factor  # расчет базового размера
                    base_min_height = min_height / self.zoom_factor
                    
                    # Устанавливаем новые размеры с учетом масштаба
                    child.setMinimumWidth(int(base_min_width * self.zoom_factor))
                    child.setMinimumHeight(int(base_min_height * self.zoom_factor))
                
        # Применяем общий стиль к виджету
        widget.setStyleSheet(f"""
            * {{
                font-size: {int(10 * self.zoom_factor)}pt;
            }}
            QLabel {{
                font-size: {int(10 * self.zoom_factor)}pt;
            }}
            QRadioButton, QCheckBox {{
                font-size: {int(10 * self.zoom_factor)}pt;
            }}
            QPushButton {{
                font-size: {int(10 * self.zoom_factor)}pt;
            }}
            QFrame {{
                font-size: {int(10 * self.zoom_factor)}pt;
            }}
        """) 
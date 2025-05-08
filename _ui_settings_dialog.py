"""Модуль для диалога настроек приложения."""

from PyQt5.QtWidgets import (QDialog, QFormLayout, QComboBox, QLineEdit, 
                             QPushButton, QHBoxLayout, QVBoxLayout)
from _4_load_settings import load_settings

class SettingsDialog(QDialog):
    """Диалог настроек приложения."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setMinimumWidth(400)
        
        # Загружаем текущие настройки
        self.settings = load_settings("settings.json")
        
        # Создаем виджеты
        self.detail_level_combo = QComboBox()
        self.detail_level_combo.addItems(["базовый", "средний", "подробный"])
        self.detail_level_combo.setCurrentText(self.settings.get("detail_level", "средний"))
        
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["начальный", "средний", "продвинутый"])
        self.difficulty_combo.setCurrentText(self.settings.get("difficulty", "средний"))
        
        self.model_edit = QLineEdit(self.settings.get("model", "локальная"))
        
        self.api_endpoint_edit = QLineEdit(self.settings.get("api_endpoint", "http://localhost:1234/v1"))
        
        self.max_tokens_edit = QLineEdit(str(self.settings.get("max_tokens", 8000)))
        
        # Кнопки
        self.cancel_btn = QPushButton("Отмена")
        self.save_btn = QPushButton("Сохранить")
        
        # Подключаем сигналы
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.accept)
        
        # Создаем макет
        layout = QFormLayout()
        layout.addRow("Уровень детализации объяснений:", self.detail_level_combo)
        layout.addRow("Сложность упражнений:", self.difficulty_combo)
        layout.addRow("Модель:", self.model_edit)
        layout.addRow("API Endpoint:", self.api_endpoint_edit)
        layout.addRow("Максимальное количество токенов:", self.max_tokens_edit)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def get_settings(self):
        """Возвращает настройки из диалога."""
        return {
            "detail_level": self.detail_level_combo.currentText(),
            "difficulty": self.difficulty_combo.currentText(),
            "model": self.model_edit.text(),
            "api_endpoint": self.api_endpoint_edit.text(),
            "max_tokens": int(self.max_tokens_edit.text()),
            "temperature": 0.5  # Фиксированное значение для простоты
        } 
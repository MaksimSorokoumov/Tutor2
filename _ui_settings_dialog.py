"""Модуль для диалога настроек приложения."""

from PyQt5.QtWidgets import (QDialog, QFormLayout, QComboBox, QLineEdit, 
                             QPushButton, QHBoxLayout, QVBoxLayout,
                             QGroupBox, QRadioButton, QLabel, QGridLayout,
                             QCheckBox, QListWidget, QMessageBox)
from PyQt5.QtCore import Qt
from _4_load_settings import load_settings
import json

class SettingsDialog(QDialog):
    """Диалог настроек приложения."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setMinimumWidth(500)
        
        # Загружаем текущие настройки
        self.settings = load_settings("settings.json")
        
        # Создаем виджеты для основных настроек
        self.detail_level_combo = QComboBox()
        self.detail_level_combo.addItems(["базовый", "средний", "подробный"])
        self.detail_level_combo.setCurrentText(self.settings.get("detail_level", "средний"))
        
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["начальный", "средний", "продвинутый"])
        self.difficulty_combo.setCurrentText(self.settings.get("difficulty", "средний"))
        
        # Создаем виджеты для настроек LLM
        self.llm_local_radio = QRadioButton("Локальная модель")
        self.llm_openrouter_radio = QRadioButton("OpenRouter API")
        
        llm_provider = self.settings.get("llm_provider", "local")
        if llm_provider == "local":
            self.llm_local_radio.setChecked(True)
        else:
            self.llm_openrouter_radio.setChecked(True)
        
        # Группа настроек для локальной модели
        self.local_group = QGroupBox("Настройки локальной модели")
        local_layout = QFormLayout()
        
        self.model_edit = QLineEdit(self.settings.get("model", "local"))
        self.api_endpoint_edit = QLineEdit(self.settings.get("api_endpoint", "http://localhost:1234/v1"))
        
        local_layout.addRow("Модель:", self.model_edit)
        local_layout.addRow("API Endpoint:", self.api_endpoint_edit)
        self.local_group.setLayout(local_layout)
        
        # Группа настроек для OpenRouter
        self.openrouter_group = QGroupBox("Настройки OpenRouter")
        openrouter_layout = QFormLayout()
        
        self.openrouter_api_key_edit = QLineEdit(self.settings.get("openrouter_api_key", ""))
        self.openrouter_api_key_edit.setEchoMode(QLineEdit.Password)
        
        self.openrouter_model_combo = QComboBox()
        for model in self.settings.get("openrouter_models", []):
            self.openrouter_model_combo.addItem(model)
        
        selected_model = self.settings.get("selected_openrouter_model", "")
        if selected_model and self.openrouter_model_combo.findText(selected_model) >= 0:
            self.openrouter_model_combo.setCurrentText(selected_model)
        
        openrouter_layout.addRow("API Key:", self.openrouter_api_key_edit)
        openrouter_layout.addRow("Выбрать модель:", self.openrouter_model_combo)
        self.openrouter_group.setLayout(openrouter_layout)
        
        # Общие настройки генерации
        self.max_tokens_edit = QLineEdit(str(self.settings.get("max_tokens", 8000)))
        self.temperature_edit = QLineEdit(str(self.settings.get("temperature", 0.5)))
        
        # Подключаем сигналы изменения провайдера
        self.llm_local_radio.toggled.connect(self.toggle_provider_settings)
        self.llm_openrouter_radio.toggled.connect(self.toggle_provider_settings)
        
        # Кнопки
        self.cancel_btn = QPushButton("Отмена")
        self.save_btn = QPushButton("Сохранить")
        
        # Подключаем сигналы
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.accept)
        
        # Создаем основной макет
        main_layout = QVBoxLayout()
        
        # Раздел основных настроек
        basic_group = QGroupBox("Основные настройки")
        basic_layout = QFormLayout()
        basic_layout.addRow("Уровень детализации объяснений:", self.detail_level_combo)
        basic_layout.addRow("Сложность упражнений:", self.difficulty_combo)
        basic_group.setLayout(basic_layout)
        main_layout.addWidget(basic_group)
        
        # Раздел выбора провайдера
        provider_group = QGroupBox("Провайдер языковой модели")
        provider_layout = QVBoxLayout()
        provider_layout.addWidget(self.llm_local_radio)
        provider_layout.addWidget(self.llm_openrouter_radio)
        provider_group.setLayout(provider_layout)
        main_layout.addWidget(provider_group)
        
        # Добавляем группы настроек
        main_layout.addWidget(self.local_group)
        main_layout.addWidget(self.openrouter_group)
        
        # Общие настройки генерации
        generation_group = QGroupBox("Параметры генерации")
        generation_layout = QFormLayout()
        generation_layout.addRow("Максимальное количество токенов:", self.max_tokens_edit)
        generation_layout.addRow("Температура:", self.temperature_edit)
        generation_group.setLayout(generation_layout)
        main_layout.addWidget(generation_group)
        
        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Инициализируем состояние интерфейса
        self.toggle_provider_settings()
    
    def toggle_provider_settings(self):
        """Переключает видимость настроек в зависимости от выбранного провайдера."""
        is_local = self.llm_local_radio.isChecked()
        self.local_group.setVisible(is_local)
        self.openrouter_group.setVisible(not is_local)
    
    def get_settings(self):
        """Возвращает настройки из диалога."""
        llm_provider = "local" if self.llm_local_radio.isChecked() else "openrouter"
        
        # Создаем словарь с новыми настройками
        new_settings = {
            "detail_level": self.detail_level_combo.currentText(),
            "difficulty": self.difficulty_combo.currentText(),
            "llm_provider": llm_provider,
            "model": self.model_edit.text(),
            "api_endpoint": self.api_endpoint_edit.text(),
            "openrouter_api_key": self.openrouter_api_key_edit.text(),
            "selected_openrouter_model": self.openrouter_model_combo.currentText(),
            "openrouter_models": [self.openrouter_model_combo.itemText(i) 
                                for i in range(self.openrouter_model_combo.count())],
            "max_tokens": int(self.max_tokens_edit.text()),
            "temperature": float(self.temperature_edit.text())
        }
        
        # Если в исходных настройках были recent_courses, сохраняем их
        if "recent_courses" in self.settings:
            new_settings["recent_courses"] = self.settings["recent_courses"]
            
        return new_settings 
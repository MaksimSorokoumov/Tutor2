"""Модуль для UI-функций генерации и проверки упражнений."""

import os
from PyQt5.QtWidgets import (
    QMessageBox, QApplication, QLabel, QRadioButton, QCheckBox, 
    QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QButtonGroup, QFrame,
    QScrollArea, QSizePolicy, QTextEdit
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QEvent

from _ui_exercise_generation_retry import generate_exercises as generate_exercises_llm
from _14_check_answer import check_answer as check_answer_llm
from _9_save_progress import save_progress
from _15_log_error import log_error
# Импортируем компоненты из новых модулей
from _ui_exercise_generation_components import ZoomableScrollArea, OptionWidget
from _ui_exercise_checking import check_single_exercise, check_answer
# Импортируем функции из новых модулей
from _ui_stage_management import update_stage_text, next_stage
from _ui_exercise_container import clear_exercise_container, create_exercise_container

# Стили для UI
QUESTION_STYLE = """
    QLabel {
        font-weight: bold;
        font-size: 11pt;
        color: #2c3e50;
        padding: 5px;
    }
"""

OPTION_STYLE = """
    QRadioButton, QCheckBox {
        font-size: 10pt;
        padding: 3px;
    }
    QRadioButton:hover, QCheckBox:hover {
        background-color: #f0f0f0;
    }
"""

EXERCISE_FRAME_STYLE = """
    QFrame {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 10px;
        margin: 5px;
    }
"""

CHECK_BUTTON_STYLE = """
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 5px 10px;
        font-size: 10pt;
        border-radius: 3px;
        min-width: 100px;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
    QPushButton:disabled {
        background-color: #9e9e9e;
    }
"""

def generate_exercise(window):
    """Генерирует упражнения в главном окне."""
    if not window.current_text:
        QMessageBox.warning(window, "Предупреждение", "Нет текста для генерации упражнения")
        return
    
    try:
        # Создаем контейнер для упражнений, если его еще нет
        create_exercise_container(window)
        
        # Очищаем контейнер
        clear_exercise_container(window)
        
        # Показываем сообщение о генерации
        loading_label = QLabel("Генерация упражнений...")
        loading_label.setAlignment(Qt.AlignCenter)
        loading_label.setFont(QFont("Arial", 12, QFont.Bold))
        window.exercise_container.layout().addWidget(loading_label)
        QApplication.processEvents()  # Обновляем интерфейс
        
        # Получаем заголовок раздела, если есть
        section_title = window.current_section['title'] if window.current_section else ""
        
        # Обновляем текст этапа обучения
        update_stage_text(window)
        
        # Генерируем упражнения конкретного этапа
        new_exs = generate_exercises_llm(
            window.current_text,
            window.settings.get("difficulty", "средний"),
            section_title,
            window.current_stage,
            window.previous_questions
        )
        
        if not new_exs:
            raise ValueError("Не удалось сгенерировать упражнения")
            
        # Фильтруем уже выполненные упражнения, если курс открыт
        if window.current_course_dir and window.current_section:
            sid = str(window.current_section['id'])
            answered = window.progress['sections'][sid]['answered']
            new_exs = [ex for ex in new_exs if ex['question'] not in answered]
            
            if not new_exs:
                # Если все упражнения данного этапа выполнены, переходим к следующему
                if window.current_stage < 2:
                    window.current_stage += 1
                    update_stage_text(window)
                    QMessageBox.information(window, "Информация", 
                                          f"Все упражнения этапа {window.current_stage} выполнены. Переходим к следующему этапу.")
                    # Рекурсивно вызываем генерацию упражнений для следующего этапа
                    generate_exercise(window)
                    return
                else:
                    QMessageBox.information(window, "Информация", "Вы выполнили все упражнения для этого раздела!")
                clear_exercise_container(window)
                return
        
        # Сохраняем сгенерированные упражнения
        window.current_exercises = new_exs
        
        # Добавляем вопросы в список предыдущих
        for ex in new_exs:
            window.previous_questions.append(ex['question'])
        
        # Ограничиваем список предыдущих вопросов (не более 20)
        if len(window.previous_questions) > 20:
            window.previous_questions = window.previous_questions[-20:]
        
        # Удаляем метку загрузки
        loading_label.deleteLater()
        
        # Добавляем заголовок для упражнений
        exercise_type = "Тест с выбором одного варианта" if window.current_stage == 0 else "Тест с выбором нескольких вариантов"
        header_label = QLabel(f"<h3 style='color: #2c3e50;'>{exercise_type}</h3>")
        header_label.setAlignment(Qt.AlignCenter)
        # Устанавливаем класс для заголовка, чтобы легче управлять его масштабированием
        header_label.setProperty("class", "exercise-header")
        window.exercise_container.layout().addWidget(header_label)
        
        # Добавляем подсказку о масштабировании
        if window.current_stage < 2 and not any(isinstance(w, QLabel) and "Используйте Ctrl+колесо мыши" in w.text() for w in window.exercise_container.findChildren(QLabel)):
            zoom_hint = QLabel("Используйте Ctrl+колесо мыши для масштабирования содержимого")
            zoom_hint.setAlignment(Qt.AlignCenter)
            zoom_hint.setStyleSheet("color: #6c757d; font-size: 9pt; font-style: italic;")
            # Устанавливаем класс для подсказки масштабирования
            zoom_hint.setProperty("class", "zoom-hint")
            window.exercise_container.layout().addWidget(zoom_hint)
        
        # Создаем виджеты для каждого упражнения
        if window.current_stage == 2:  # Открытый вопрос
            # Для открытых вопросов оставляем текстовое поле, но правильно настраиваем видимость всех элементов
            
            # Сначала скрываем область прокрутки с тестами
            if hasattr(window, 'exercise_scroll_area'):
                window.exercise_scroll_area.hide()
            
            # Показываем стандартные элементы для открытых вопросов
            window.exercise_edit.show()
            window.exercise_edit.setReadOnly(True)  # Устанавливаем поле только для чтения
            
            # Находим и показываем метку "Ваш ответ:"
            answer_label_found = False
            for label in window.findChildren(QLabel):
                if label.text() == "Ваш ответ:":
                    label.show()
                    answer_label_found = True
                    break
            
            # Показываем поля для ввода ответа и комментария
            window.answer_edit.show()
            window.result_label.show()
            window.result_edit.show()
            
            # Проверяем, что у нас есть вопросы и выводим отладочную информацию
            print(f"Количество сгенерированных вопросов: {len(new_exs)}")
            print(f"Текущая стадия: {window.current_stage}")
            if new_exs and len(new_exs) > 0:
                print(f"Отображаю открытый вопрос: {new_exs[0]['question']}")
                
                # Форматируем упражнение для отображения
                exercise_text = f"{new_exs[0]['question']}\n\n"
                window.exercise_edit.setText(exercise_text)
                window.exercise_edit.setStyleSheet("QTextEdit { margin-top: 15px; padding-top: 15px; }")
                window.answer_edit.clear()
                window.result_edit.clear()
                
                # Настраиваем заголовок упражнения
                window.exercise_label.setText("Упражнение")
                window.exercise_label.setFont(QFont("Arial", 12, QFont.Bold))
                window.exercise_label.setStyleSheet("QLabel { padding-bottom: 5px; }")
            else:
                print("Ошибка: не удалось получить открытые вопросы!")
                window.exercise_edit.setText("Ошибка: не удалось получить вопрос.")
            
            # Обновляем интерфейс, чтобы убедиться, что изменения применены
            QApplication.processEvents()
        else:
            # Для тестов с вариантами ответов
            
            # Скрываем стандартные элементы для открытых вопросов
            window.exercise_edit.hide()
            
            # Находим и скрываем метку "Ваш ответ:"
            for label in window.findChildren(QLabel):
                if label.text() == "Ваш ответ:":
                    label.hide()
                    break
            
            # Скрываем поля для ввода и результаты (без комментариев)
            window.answer_edit.hide()
            window.result_label.hide()
            window.result_edit.hide()
            
            # Показываем область прокрутки с тестами
            if hasattr(window, 'exercise_scroll_area'):
                window.exercise_scroll_area.show()
            
            # Счетчик для нумерации вопросов
            question_number = 1
            
            # Создаем виджеты для каждого вопроса
            for i, exercise in enumerate(new_exs):
                # Создаем фрейм для упражнения
                exercise_frame = QFrame()
                exercise_frame.setFrameShape(QFrame.StyledPanel)
                exercise_frame.setFrameShadow(QFrame.Raised)
                exercise_frame.setStyleSheet(EXERCISE_FRAME_STYLE)
                # Устанавливаем минимальную ширину фрейма, чтобы он мог корректно масштабироваться
                exercise_frame.setMinimumWidth(400)
                exercise_frame.setMinimumHeight(100)
                # Также устанавливаем политику размеров для фрейма вопроса
                exercise_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
                exercise_layout = QVBoxLayout(exercise_frame)
                exercise_layout.setSpacing(10)
                
                # Добавляем текст вопроса с номером
                question_text = f"<b>Вопрос {question_number}:</b> {exercise['question']}"
                question_label = QLabel(question_text)
                question_label.setWordWrap(True)  # Включаем перенос текста
                question_label.setStyleSheet(QUESTION_STYLE)
                question_label.setTextFormat(Qt.RichText)  # Явно указываем, что используем Rich Text
                exercise_layout.addWidget(question_label)
                question_number += 1
                
                # Добавляем варианты ответов
                options_layout = QVBoxLayout()
                options_layout.setSpacing(5)
                options_layout.setContentsMargins(10, 5, 5, 5)
                
                # Создаем группу для радиокнопок, если это одиночный выбор
                button_group = None
                if window.current_stage == 0:
                    button_group = QButtonGroup(exercise_frame)
                
                # Создаем кнопки для вариантов ответов
                options_widgets = []  # Список для хранения виджетов с вариантами ответов
                
                for j, option in enumerate(exercise['options']):
                    # Используем кастомный виджет с переносом текста
                    is_radio = (window.current_stage == 0)
                    opt_widget = OptionWidget(is_radio, option)
                    button = opt_widget.button
                    if is_radio:
                        button_group.addButton(button, j)
                    # Размер виджета управляется компоновкой
                    options_layout.addWidget(opt_widget)
                    options_widgets.append(button)
                
                exercise_layout.addLayout(options_layout)
                
                # Добавляем поле для комментария пользователя при множественном выборе
                if window.current_stage == 1:
                    comment_label = QLabel("Комментарий (необязательно):")
                    comment_label.setWordWrap(True)
                    exercise_layout.addWidget(comment_label)
                    comment_edit = QTextEdit()
                    comment_edit.setFixedHeight(60)
                    exercise_layout.addWidget(comment_edit)
                else:
                    comment_edit = None
                
                # Кнопки и результаты в горизонтальном layout
                button_result_layout = QHBoxLayout()
                
                # Добавляем кнопку проверки
                check_btn = QPushButton("Проверить")
                check_btn.setProperty("exercise_index", i)
                check_btn.clicked.connect(lambda checked, button=check_btn: check_single_exercise(window, button.property("exercise_index")))
                check_btn.setStyleSheet(CHECK_BUTTON_STYLE)
                # Устанавливаем минимальную и предпочтительную ширину для кнопки
                check_btn.setMinimumWidth(100)
                check_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
                button_result_layout.addWidget(check_btn)
                
                # Добавляем поле для результата
                result_label = QLabel("")
                result_label.setWordWrap(True)
                button_result_layout.addWidget(result_label, 1)  # 1 - растягивается по горизонтали
                
                exercise_layout.addLayout(button_result_layout)
                
                # Сохраняем виджеты в данных упражнения для дальнейшего доступа
                exercise['ui'] = {
                    'frame': exercise_frame,
                    'button_group': button_group,
                    'options_widgets': options_widgets,  # Используем подготовленный список
                    'result_label': result_label,
                    'check_button': check_btn,
                    'comment_edit': comment_edit
                }
                
                # Добавляем фрейм упражнения в контейнер
                window.exercise_container.layout().addWidget(exercise_frame)
                
                # Добавляем разделитель между упражнениями, если это не последнее упражнение
                if i < len(new_exs) - 1:
                    separator = QFrame()
                    separator.setFrameShape(QFrame.HLine)
                    separator.setFrameShadow(QFrame.Sunken)
                    window.exercise_container.layout().addWidget(separator)
                
                # Сохраняем контекст учебного материала для LLM проверки
                exercise['context'] = window.current_text
        
        # Обновляем интерфейс
        QApplication.processEvents()
        
    except Exception as e:
        log_error(e)
        # Очищаем контейнер и показываем ошибку
        clear_exercise_container(window)
        error_label = QLabel(f"Ошибка при генерации упражнения: {str(e)}")
        error_label.setWordWrap(True)
        error_label.setStyleSheet("color: red; font-weight: bold;")
        window.exercise_container.layout().addWidget(error_label) 
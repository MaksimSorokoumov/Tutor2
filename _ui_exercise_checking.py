"""Модуль для UI-функций проверки ответов."""

import os
from PyQt5.QtWidgets import QMessageBox, QCheckBox, QLabel, QApplication, QDialog, QVBoxLayout, QTextEdit, QPushButton, QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from _14_check_answer import check_answer as check_answer_llm
from _9_save_progress import save_progress
from _15_log_error import log_error

def check_single_exercise(window, exercise_index):
    """Проверяет ответ на конкретное упражнение (тест).
    
    Args:
        window: Главное окно приложения
        exercise_index: Индекс проверяемого упражнения
    """
    if not window.current_exercises or exercise_index >= len(window.current_exercises):
        return
    
    exercise = window.current_exercises[exercise_index]
    
    try:
        if window.current_stage == 0:  # Одиночный выбор
            # Получаем выбранный вариант ответа
            button_group = exercise['ui']['button_group']
            selected_button = button_group.checkedButton()
            
            if not selected_button:
                QMessageBox.warning(window, "Предупреждение", "Выберите вариант ответа")
                return
            
            # Получаем индекс выбранного варианта
            selected_index = button_group.id(selected_button)
            user_answer = str(selected_index + 1)  # Приводим к формату "1", "2" и т.д.
            
        elif window.current_stage == 1:  # Множественный выбор
            # Получаем все выбранные варианты
            selected_options = []
            for i, widget in enumerate(exercise['ui']['options_widgets']):
                if isinstance(widget, QCheckBox) and widget.isChecked():
                    selected_options.append(i + 1)  # Индексы начинаются с 1
            
            if not selected_options:
                QMessageBox.warning(window, "Предупреждение", "Выберите хотя бы один вариант ответа")
                return
            
            # Преобразуем список выбранных вариантов в строку
            user_answer = ",".join(map(str, selected_options))
            
        else:  # Открытый вопрос (обрабатывается отдельной функцией)
            return
        
        # Получаем комментарий пользователя, если он есть
        comment_edit = exercise['ui'].get('comment_edit')
        user_comment = comment_edit.toPlainText().strip() if comment_edit else ""
        # Проверяем ответ
        result = check_answer_llm(exercise, user_answer, user_comment)
        
        # Записываем попытку в историю exercises и обновляем прогресс
        if window.current_course_dir:
            sid = str(window.current_section['id'])
            sp = window.progress['sections'][sid]
            # Для тестов сохраняем все варианты и преобразуем ответ в текст
            options = exercise.get("options", [])
            if window.current_stage == 0:
                try:
                    idx = int(user_answer.strip()) - 1
                    user_answer_text = options[idx] if 0 <= idx < len(options) else user_answer
                except:
                    user_answer_text = user_answer
            else:
                # множественный выбор
                user_answer_text = []
                for part in user_answer.split(","):
                    part = part.strip()
                    if part.isdigit():
                        i = int(part) - 1
                        if 0 <= i < len(options):
                            user_answer_text.append(options[i])
            entry = {
                "question": exercise['question'],
                "stage": window.current_stage,
                "options": options,
                "user_answer": user_answer_text,
                "correct_answer": result.get('correct_answer'),
                "is_correct": bool(result.get('is_correct', False))
            }
            sp['exercises'].append(entry)
            # Обновляем количество правильных ответов
            sp['exercises_completed'] = sum(1 for e in sp['exercises'] if e['is_correct'])
            # Добавляем в список answered для обратной совместимости
            if entry['is_correct'] and entry['question'] not in sp.get('answered', []):
                sp.setdefault('answered', []).append(entry['question'])
            save_progress(os.path.join(window.current_course_dir, "progress.json"), window.progress)
        
        # Форматируем результат
        if result.get("is_correct", False):
            result_html = '<span style="color: green; font-weight: bold;">✓ Правильно!</span>'
        else:
            correct_answer = result.get('correct_answer', '')
            # Форматируем правильный ответ в зависимости от типа вопроса
            if window.current_stage == 0:  # Одиночный выбор
                # Находим индекс правильного ответа в списке опций
                for i, option in enumerate(exercise['options']):
                    if option.lower() == correct_answer.lower():
                        correct_answer = f"{i+1}. {option}"
                        break
            elif window.current_stage == 1:  # Множественный выбор
                # Если ответ - список, форматируем его
                if isinstance(correct_answer, list):
                    correct_indexes = []
                    for answer in correct_answer:
                        for i, option in enumerate(exercise['options']):
                            if option.lower() == answer.lower():
                                correct_indexes.append(str(i+1))
                                break
                    correct_answer = ", ".join(correct_indexes)
                
            result_html = f'<span style="color: red; font-weight: bold;">✗ Неправильно.</span><br>Правильный ответ: {correct_answer}'

            # Добавляем кнопку "Подробнее" для тестов с множественным выбором, если есть подробное объяснение
            if window.current_stage == 1 and 'feedback' in result and len(result['feedback']) > 30:
                # Создаем подробное объяснение для отображения
                detailed_feedback = result.get('feedback', '')
                
                # Проверяем, есть ли в контейнере упражнения виджет для подробного объяснения
                if not 'explanation_widget' in exercise['ui']:
                    # Если виджета нет, создаем и добавляем его в контейнер упражнения
                    explanation_label = QLabel()
                    explanation_label.setWordWrap(True)
                    explanation_label.setTextFormat(Qt.RichText)
                    explanation_label.setStyleSheet("QLabel { margin-top: 10px; background-color: #f0f0f0; border-radius: 5px; padding: 10px; }")
                    explanation_label.setVisible(False)  # Изначально скрыт
                    
                    # Создаем кнопку для отображения/скрытия объяснения
                    detail_btn = QPushButton("Подробнее")
                    detail_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #2196F3;
                            color: white;
                            border: none;
                            padding: 5px 10px;
                            font-size: 10pt;
                            border-radius: 3px;
                            max-width: 120px;
                        }
                        QPushButton:hover {
                            background-color: #1976D2;
                        }
                    """)
                    
                    # Добавляем кнопку и виджет объяснения в контейнер упражнения
                    layout = exercise['ui']['frame'].layout()
                    layout.addWidget(detail_btn)
                    layout.addWidget(explanation_label)
                    
                    # Сохраняем ссылки на виджеты в UI упражнения
                    exercise['ui']['explanation_widget'] = explanation_label
                    exercise['ui']['detail_button'] = detail_btn
                    
                    # Подключаем обработчик нажатия кнопки
                    detail_btn.clicked.connect(lambda checked, label=explanation_label, btn=detail_btn: toggle_explanation(label, btn))
                
                # Устанавливаем текст объяснения, заменяя переносы строк на HTML тег <br>
                # Избегаем прямого использования обратного слеша в f-строке
                explanation_text = detailed_feedback.replace("\n", "<br>")
                formatted_explanation = f"<div style='margin-top: 10px;'><b>Объяснение:</b><br>{explanation_text}</div>"
                exercise['ui']['explanation_widget'].setText(formatted_explanation)
        
        # Отображаем результат
        result_label = exercise['ui']['result_label']
        result_label.setText(result_html)
        result_label.setTextFormat(Qt.RichText)
        
        # Делаем кнопки неактивными после проверки и меняем стиль кнопки проверки
        exercise['ui']['check_button'].setEnabled(False)
        exercise['ui']['check_button'].setText("Проверено")
        exercise['ui']['check_button'].setStyleSheet("""
            QPushButton {
                background-color: #9e9e9e;
                color: white;
                border: none;
                padding: 5px 10px;
                font-size: 10pt;
                border-radius: 3px;
            }
        """)
        
        # Делаем варианты ответов неактивными и подсвечиваем правильные
        if window.current_stage == 0:  # Одиночный выбор
            for i, button_element in enumerate(exercise['ui']['options_widgets']): # button_element это QRadioButton/QCheckBox
                button_element.setEnabled(False)
                option_widget = button_element.parentWidget() # Получаем родительский OptionWidget
                if option_widget and hasattr(option_widget, 'label'):
                    label_to_style = option_widget.label
                    # Сравниваем текст метки с правильным ответом
                    if label_to_style.text().lower() == exercise['correct_answer'].lower():
                        label_to_style.setStyleSheet("QLabel { font-size: 10pt; padding: 3px; color: green; }") # Без font-weight: bold
        elif window.current_stage == 1:  # Множественный выбор
            for i, button_element in enumerate(exercise['ui']['options_widgets']): # button_element это QRadioButton/QCheckBox
                button_element.setEnabled(False)
                option_widget = button_element.parentWidget() # Получаем родительский OptionWidget
                if option_widget and hasattr(option_widget, 'label'):
                    label_to_style = option_widget.label
                    current_option_text = label_to_style.text().lower()
                    correct_answers_list = []
                    if isinstance(exercise['correct_answer'], list):
                        correct_answers_list = [ans.lower() for ans in exercise['correct_answer']]
                    else: # Строка с ответами через запятую
                        correct_answers_list = [ans.strip().lower() for ans in exercise['correct_answer'].split(',')]
                    
                    if current_option_text in correct_answers_list:
                        label_to_style.setStyleSheet("QLabel { font-size: 10pt; padding: 3px; color: green; }") # Без font-weight: bold
        
    except Exception as e:
        log_error(e)
        QMessageBox.critical(window, "Ошибка", f"Ошибка при проверке ответа: {str(e)}")

def toggle_explanation(label, button):
    """Переключает отображение подробного объяснения.
    
    Args:
        label: QLabel с объяснением
        button: QPushButton кнопка переключения
    """
    is_visible = label.isVisible()
    label.setVisible(not is_visible)
    
    if not is_visible:
        button.setText("Скрыть объяснение")
    else:
        button.setText("Подробнее")

def check_answer(window):
    """Проверяет ответ пользователя в главном окне (для открытых вопросов).
    
    Args:
        window: Главное окно приложения
    """
    if not window.current_exercises:
        QMessageBox.warning(window, "Предупреждение", "Нет активного упражнения")
        return
    
    # Этот метод используется только для открытых вопросов (этап 2)
    if window.current_stage != 2:
        return
    
    # Проверяем видимость и существование необходимых виджетов
    if not hasattr(window, 'answer_edit') or not window.answer_edit.isVisible():
        QMessageBox.warning(window, "Предупреждение", "Поле для ввода ответа недоступно")
        return
    
    user_answer = window.answer_edit.toPlainText().strip()
    
    if not user_answer:
        QMessageBox.warning(window, "Предупреждение", "Введите ваш ответ")
        return
    
    try:
        if not hasattr(window, 'result_edit') or not window.result_edit.isVisible():
            QMessageBox.warning(window, "Предупреждение", "Поле для вывода результата недоступно")
            return
            
        window.result_edit.setText("Проверка ответа...")
        QApplication.processEvents()  # Обновляем интерфейс
        
        exercise = window.current_exercises[0]  # Берем первое упражнение
        user_comment = window.comment_edit.toPlainText().strip() if hasattr(window, 'comment_edit') else ""
        
        # Проверяем ответ с учетом комментария пользователя
        result = check_answer_llm(exercise, user_answer, user_comment)
        
        # Записываем попытку в историю exercises и обновляем прогресс
        if window.current_course_dir:
            sid = str(window.current_section['id'])
            sp = window.progress['sections'][sid]
            # Для тестов сохраняем все варианты и преобразуем ответ в текст
            options = exercise.get("options", [])
            if window.current_stage == 0:
                try:
                    idx = int(user_answer.strip()) - 1
                    user_answer_text = options[idx] if 0 <= idx < len(options) else user_answer
                except:
                    user_answer_text = user_answer
            else:
                # множественный выбор
                user_answer_text = []
                for part in user_answer.split(","):
                    part = part.strip()
                    if part.isdigit():
                        i = int(part) - 1
                        if 0 <= i < len(options):
                            user_answer_text.append(options[i])
            entry = {
                "question": exercise['question'],
                "stage": window.current_stage,
                "options": options,
                "user_answer": user_answer_text,
                "correct_answer": result.get('correct_answer'),
                "is_correct": bool(result.get('is_correct', False))
            }
            sp['exercises'].append(entry)
            # Обновляем количество правильных ответов
            sp['exercises_completed'] = sum(1 for e in sp['exercises'] if e['is_correct'])
            # Добавляем в список answered для обратной совместимости
            if entry['is_correct'] and entry['question'] not in sp.get('answered', []):
                sp.setdefault('answered', []).append(entry['question'])
            save_progress(os.path.join(window.current_course_dir, "progress.json"), window.progress)
        
        # Форматируем результат для открытых вопросов
        result_text = ""
        if result.get("is_correct", False):
            result_text += "<div style='color: green; font-weight: bold;'>✓ Молодец! Ваш ответ соответствует требованиям.</div><br>"
        else:
            result_text += "<div style='color: red; font-weight: bold;'>Ваш ответ нуждается в доработке.</div><br>"
        
        result_text += f"<div><b>Отзыв преподавателя:</b><br>{result.get('feedback', '')}</div><br>"
        
        if "strengths" in result:
            result_text += "<div><b>Сильные стороны вашего ответа:</b><ul>"
            for strength in result["strengths"]:
                result_text += f"<li>{strength}</li>"
            result_text += "</ul></div>"
        
        if "areas_for_improvement" in result:
            result_text += "<div><b>Области для улучшения:</b><ul>"
            for area in result["areas_for_improvement"]:
                result_text += f"<li>{area}</li>"
            result_text += "</ul></div>"
        
        window.result_edit.setHtml(result_text)
        
        # После проверки ответа на третьем этапе меняем кнопку на "Следующий раздел" 
        # и делаем ее зеленой
        if window.current_stage == 2:
            window.next_stage_btn.setText("Следующий раздел")
            window.next_stage_btn.setStyleSheet("""
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
            """)
            
            # Отключаем обработчик events для текущей кнопки и подключаем новый
            try:
                window.next_stage_btn.clicked.disconnect()
            except:
                pass
            
            # Подключаем новый обработчик для открытия следующего раздела
            window.next_stage_btn.clicked.connect(window.open_next_section)
        
    except Exception as e:
        log_error(e)
        if hasattr(window, 'result_edit') and window.result_edit.isVisible():
            window.result_edit.setText(f"Ошибка при проверке ответа: {str(e)}")
        else:
            QMessageBox.critical(window, "Ошибка", f"Ошибка при проверке ответа: {str(e)}") 
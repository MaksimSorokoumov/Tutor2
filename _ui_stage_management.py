"""Модуль управления этапами обучения."""

from PyQt5.QtWidgets import QMessageBox, QLabel

def update_stage_text(window):
    """Обновляет текст с информацией о текущем этапе обучения."""
    stage_names = [
        "тесты с одним правильным ответом",
        "тесты с несколькими правильными ответами",
        "открытые вопросы"
    ]
    stage_name = stage_names[window.current_stage]
    window.stage_label.setText(f"Этап обучения: {stage_name} ({window.current_stage + 1}/3)")

def next_stage(window):
    """Переход к следующему этапу обучения."""
    if window.current_stage < 2:
        window.current_stage += 1
        update_stage_text(window)
        
        # Очищаем контейнер перед генерацией нового упражнения
        if hasattr(window, 'exercise_container'):
            from _ui_exercise_container import clear_exercise_container
            clear_exercise_container(window)
            
        # Если переходим к открытым вопросам, обеспечиваем нужное состояние виджетов
        if window.current_stage == 2:
            # Скрываем область прокрутки, если она создана
            if hasattr(window, 'exercise_scroll_area'):
                window.exercise_scroll_area.hide()
            
            # Показываем необходимые виджеты для открытых вопросов
            window.exercise_edit.show()
            window.exercise_edit.setReadOnly(True)
            window.answer_edit.show()
            
            # Показываем метку "Ваш ответ:"
            for label in window.findChildren(QLabel):
                if label.text() == "Ваш ответ:":
                    label.show()
                    break
                    
            # Показываем поля результата
            window.result_label.show()
            window.result_edit.show()
            
            # Сбрасываем содержимое полей
            window.exercise_edit.clear()
            window.answer_edit.clear()
            window.result_edit.clear()
            
        # Запускаем генерацию упражнения для нового этапа
        from _ui_exercise_generation import generate_exercise
        generate_exercise(window)
    else:
        # Меняем текст кнопки на "Следующий раздел" и делаем её зеленой
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

def open_next_section(window):
    """Открывает следующий раздел учебника."""
    # Перенаправляем вызов к методу объекта window
    window.open_next_section() 
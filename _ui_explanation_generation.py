"""Модуль для UI-функций генерации и обновления объяснений."""

from PyQt5.QtWidgets import QMessageBox, QApplication
from _12_generate_explanation import generate_explanation as generate_explanation_llm
from _15_log_error import log_error

def generate_explanation(window):
    """Генерирует объяснение для текста в главном окне."""
    if not window.current_text:
        QMessageBox.warning(window, "Предупреждение", "Нет текста для объяснения")
        return
    
    try:
        window.explanation_edit.setText("Генерация объяснения...")
        QApplication.processEvents()  # Обновляем интерфейс
        
        explanation = generate_explanation_llm(
            window.current_text,
            window.settings.get("detail_level", "средний")
        )
        
        window.explanation_edit.setText(explanation)
        window.current_explanation = explanation
        
        # Генерируем упражнение после объяснения
        window.generate_exercise() # Предполагаем, что метод generate_exercise останется в MainWindow или будет импортирован
        
    except Exception as e:
        log_error(e)
        window.explanation_edit.setText(f"Ошибка при генерации объяснения: {str(e)}")

def regenerate_explanation(window):
    """Генерирует объяснение заново в главном окне."""
    generate_explanation(window)

def send_feedback(window):
    """Отправляет отзыв для уточнения объяснения в главном окне."""
    feedback = window.feedback_edit.text()
    
    if not feedback:
        QMessageBox.warning(window, "Предупреждение", "Введите ваш вопрос или отзыв")
        return
    
    if not window.current_text:
        QMessageBox.warning(window, "Предупреждение", "Нет текста для объяснения")
        return
    
    try:
        window.explanation_edit.setText("Генерация уточненного объяснения...")
        QApplication.processEvents()  # Обновляем интерфейс
        
        explanation = generate_explanation_llm(
            window.current_text,
            window.settings.get("detail_level", "средний"),
            feedback
        )
        
        window.explanation_edit.setText(explanation)
        window.current_explanation = explanation
        window.feedback_edit.clear()
        
    except Exception as e:
        log_error(e)
        window.explanation_edit.setText(f"Ошибка при генерации уточненного объяснения: {str(e)}") 
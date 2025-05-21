"""Модуль для UI-функций генерации и обновления объяснений."""

from PyQt5.QtWidgets import QMessageBox, QApplication
from _12_generate_explanation import generate_explanation as generate_explanation_llm
from _15_log_error import log_error
import os
from _6_load_course_structure import load_course_structure
from _7_save_course_structure import save_course_structure
import re

def clean_html(expl: str) -> str:
    """Удаляет обрамляющие блоки кода ```html``` из объяснения."""
    expl = re.sub(r"^```html\s*\n?", "", expl)
    expl = re.sub(r"\n?```$", "", expl)
    return expl.strip()

def generate_explanation(window):
    """Показывает сохранённое объяснение из structure.json."""
    if not window.current_course_dir or not window.current_section:
        QMessageBox.warning(window, "Предупреждение", "Откройте курс для доступа к объяснению")
        return
    detail = getattr(window, "current_detail_level", window.settings.get("detail_level", "средний"))
    structure_path = os.path.join(window.current_course_dir, "structure.json")
    try:
        sections = load_course_structure(structure_path)
        explanation = None
        for sec in sections:
            if sec.get("id") == window.current_section.get("id"):
                explanation = sec.get("explanations", {}).get(detail)
                break
        if explanation:
            html = clean_html(explanation)
            window.explanation_edit.setHtml(html)
            window.current_explanation = html
        else:
            QMessageBox.warning(window, "Предупреждение", "Объяснение ещё не сгенерировано. Используйте меню 'Инструменты -> Прегенерировать объяснения'.")
    except Exception as e:
        log_error(e)
        window.explanation_edit.setText(f"Ошибка при загрузке объяснения: {str(e)}")

def regenerate_explanation(window):
    """Перегенерирует объяснение через LLM и сохраняет в structure.json."""
    if not window.current_course_dir or not window.current_section:
        QMessageBox.warning(window, "Предупреждение", "Откройте курс для регенерации объяснения")
        return
    detail = getattr(window, "current_detail_level", window.settings.get("detail_level", "средний"))
    try:
        window.explanation_edit.setText("Генерация объяснения...")
        QApplication.processEvents()
        new_expl = generate_explanation_llm(
            window.current_text,
            detail
        )
        html = clean_html(new_expl)
        window.explanation_edit.setHtml(html)
        window.current_explanation = html
        structure_path = os.path.join(window.current_course_dir, "structure.json")
        sections = load_course_structure(structure_path)
        for sec in sections:
            if sec.get("id") == window.current_section.get("id"):
                sec.setdefault("explanations", {})[detail] = html
                break
        save_course_structure(structure_path, sections)
    except Exception as e:
        log_error(e)
        window.explanation_edit.setText(f"Ошибка при регенерации объяснения: {str(e)}")

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
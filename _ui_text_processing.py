"""Модуль для обработки текста: загрузка демо-текста и открытие книг."""

import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from _1_load_book import load_book
from _19_load_demo_text import load_welcome_text as load_base_welcome_text
from _15_log_error import log_error

def load_demo_text(window):
    """Загружает приветственный текст и справку в главное окно."""
    welcome_text = load_base_welcome_text()
    window.text_edit.setText(welcome_text)
    window.current_text = welcome_text

def open_book(window):
    """Открывает диалог выбора книги и загружает ее текст в главное окно."""
    file_path, _ = QFileDialog.getOpenFileName(
        window, "Открыть книгу", "", "Текстовые файлы (*.txt);;Word документы (*.docx);;Все файлы (*.*)"
    )
    
    if file_path:
        try:
            text = load_book(file_path)
            window.text_edit.setText(text)
            window.current_text = text
            window.explanation_edit.clear()
            window.exercise_edit.clear()
            window.answer_edit.clear()
            window.result_edit.clear()
            
            QMessageBox.information(window, "Информация", f"Книга успешно загружена: {file_path}")
            return True
        except Exception as e:
            log_error(e)
            QMessageBox.critical(window, "Ошибка", f"Не удалось загрузить книгу: {str(e)}")
            return False
    return False

def open_book_with_return(window):
    """Открывает диалог выбора книги и загружает ее текст в главное окно."""
    file_path, _ = QFileDialog.getOpenFileName(
        window, "Открыть книгу", "", "Текстовые файлы (*.txt);;Word документы (*.docx);;Все файлы (*.*)"
    )
    
    if file_path:
        try:
            text = load_book(file_path)
            window.text_edit.setText(text)
            window.current_text = text
            window.explanation_edit.clear()
            window.exercise_edit.clear()
            window.answer_edit.clear()
            window.result_edit.clear()
            
            QMessageBox.information(window, "Информация", f"Книга успешно загружена: {file_path}")
            return True
        except Exception as e:
            log_error(e)
            QMessageBox.critical(window, "Ошибка", f"Не удалось загрузить книгу: {str(e)}")
            return False
    return False 
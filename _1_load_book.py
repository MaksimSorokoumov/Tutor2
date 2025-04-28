"""Модуль для загрузки книги из файлов .docx или .txt."""
from typing import Union
import os
from docx import Document

def load_book(filepath: str) -> str:
    """Загружает текст книги из файла .docx или .txt.
    
    Args:
        filepath: Путь к файлу книги (.docx или .txt)
        
    Returns:
        Полный текст книги одной строкой
        
    Raises:
        FileNotFoundError: Если файл не найден
        ValueError: Если формат файла не поддерживается
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл не найден: {filepath}")
    
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    if ext == '.txt':
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    elif ext == '.docx':
        doc = Document(filepath)
        return '\n'.join([para.text for para in doc.paragraphs])
    else:
        raise ValueError(f"Неподдерживаемый формат файла: {ext}. Поддерживаются только .txt и .docx") 
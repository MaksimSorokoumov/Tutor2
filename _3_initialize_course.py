"""Модуль для инициализации курса на основе книги."""

import os
import json
from typing import Optional
from _1_load_book import load_book
from _2_parse_structure import parse_structure

def initialize_course(book_path: str, output_dir: str) -> None:
    """Создаёт структуру курса и файл прогресса пользователя.
    
    Args:
        book_path: Путь к файлу книги (.docx или .txt)
        output_dir: Путь к директории для сохранения файлов курса
        
    Returns:
        None
        
    Raises:
        FileNotFoundError: Если файл книги не найден
        ValueError: Если формат файла не поддерживается
        IOError: При ошибке создания директории или записи файлов
    """
    # Загружаем книгу
    book_text = load_book(book_path)
    
    # Разбираем структуру книги
    sections = parse_structure(book_text)
    
    # Создаем директорию, если её нет
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Сохраняем структуру в structure.json
    structure_path = os.path.join(output_dir, "structure.json")
    with open(structure_path, 'w', encoding='utf-8') as f:
        json.dump(sections, f, ensure_ascii=False, indent=2)
    
    # Инициализируем пустой прогресс для всех разделов
    progress = {
        "book_path": book_path,
        "sections": {}
    }
    
    for section in sections:
        section_id = section["id"]
        progress["sections"][str(section_id)] = {
            "completed": False,
            "exercises_completed": 0,
            "last_viewed": None,
            "answered": [],
            "exercises": [],           # история ответов пользователя
            "evaluation": {"score": None, "comment": ""}  # оценка раздела
        }
    
    # Сохраняем прогресс в progress.json
    progress_path = os.path.join(output_dir, "progress.json")
    with open(progress_path, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)
    
    print(f"Курс успешно инициализирован в директории {output_dir}")
    print(f"Создано {len(sections)} разделов") 
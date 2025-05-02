"""Главный модуль приложения Tutor."""
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QPushButton, QLabel, QTextEdit, QComboBox, QMessageBox
from PyQt5.QtWidgets import QFileDialog, QTabWidget, QLineEdit, QDialog, QFormLayout
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

# Импортируем модули приложения
from _4_load_settings import load_settings
from _12_generate_explanation import generate_explanation
from _13_generate_exercises import generate_exercises
from _14_check_answer import check_answer
from _15_log_error import log_error, log_info
from _16_create_course_structure import create_course_structure
from _17_open_course import open_course
from _18_select_section import select_section
from _19_load_demo_text import load_welcome_text
from _8_load_progress import load_progress
from _9_save_progress import save_progress

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

class MainWindow(QMainWindow):
    """Главное окно приложения Tutor."""
    
    def __init__(self):
        super().__init__()
        
        # Настройки окна
        self.setWindowTitle("Tutor - Интерактивное обучение")
        self.setGeometry(100, 100, 1200, 800)
        
        # Загружаем настройки
        self.settings = load_settings("settings.json")
        
        # Текущий текст и данные
        self.current_text = ""
        self.current_exercises = []
        self.current_explanation = ""
        self.current_course_dir = ""
        self.current_course_structure = []
        self.current_section = None
        self.progress = {}
        self.current_stage = 0  # Этап обучения (0, 1 или 2)
        self.previous_questions = []  # Список предыдущих вопросов для избежания повторений
        
        # Создаем центральный виджет и макет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный макет - горизонтальный для трех панелей
        main_layout = QHBoxLayout()
        
        # Панель 1: Исходный текст
        text_panel = QWidget()
        text_layout = QVBoxLayout()
        
        self.text_label = QLabel("Исходный текст")
        self.text_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        
        text_buttons_layout = QHBoxLayout()
        self.copy_text_btn = QPushButton("Копировать")
        self.explain_btn = QPushButton("Объяснить")
        
        text_buttons_layout.addWidget(self.copy_text_btn)
        text_buttons_layout.addWidget(self.explain_btn)
        
        text_layout.addWidget(self.text_label)
        text_layout.addWidget(self.text_edit)
        text_layout.addLayout(text_buttons_layout)
        
        text_panel.setLayout(text_layout)
        
        # Панель 2: Объяснение
        explanation_panel = QWidget()
        explanation_layout = QVBoxLayout()
        
        self.explanation_label = QLabel("Объяснение")
        self.explanation_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.explanation_edit = QTextEdit()
        self.explanation_edit.setReadOnly(True)
        
        explanation_buttons_layout = QHBoxLayout()
        self.copy_explanation_btn = QPushButton("Копировать")
        self.regenerate_btn = QPushButton("Сгенерировать заново")
        
        explanation_feedback_layout = QHBoxLayout()
        self.feedback_edit = QLineEdit()
        self.feedback_edit.setPlaceholderText("Укажите, что непонятно...")
        self.send_feedback_btn = QPushButton("Отправить")
        
        explanation_feedback_layout.addWidget(self.feedback_edit)
        explanation_feedback_layout.addWidget(self.send_feedback_btn)
        
        explanation_buttons_layout.addWidget(self.copy_explanation_btn)
        explanation_buttons_layout.addWidget(self.regenerate_btn)
        
        explanation_layout.addWidget(self.explanation_label)
        explanation_layout.addWidget(self.explanation_edit)
        explanation_layout.addLayout(explanation_buttons_layout)
        explanation_layout.addLayout(explanation_feedback_layout)
        
        explanation_panel.setLayout(explanation_layout)
        
        # Панель 3: Упражнения
        exercise_panel = QWidget()
        exercise_layout = QVBoxLayout()
        
        self.exercise_label = QLabel("Упражнение")
        self.exercise_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.exercise_edit = QTextEdit()
        self.exercise_edit.setReadOnly(True)
        
        self.answer_edit = QTextEdit()
        self.answer_edit.setPlaceholderText("Введите ваш ответ здесь...")
        
        # Добавляем поле для комментария
        self.comment_label = QLabel("Ваш комментарий к ответу (необязательно):")
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Здесь вы можете объяснить свой выбор или указать на неоднозначность вопроса...")
        self.comment_edit.setMaximumHeight(80)  # Ограничиваем высоту поля
        
        exercise_buttons_layout = QHBoxLayout()
        self.check_btn = QPushButton("Проверить ответ")
        self.next_exercise_btn = QPushButton("Новое упражнение")
        self.next_stage_btn = QPushButton("Следующий этап")
        
        exercise_buttons_layout.addWidget(self.check_btn)
        exercise_buttons_layout.addWidget(self.next_exercise_btn)
        exercise_buttons_layout.addWidget(self.next_stage_btn)
        
        self.result_label = QLabel("Результат проверки")
        self.result_edit = QTextEdit()
        self.result_edit.setReadOnly(True)
        
        # Добавляем индикатор прогресса с этапом обучения
        self.stage_label = QLabel("Этап обучения: тесты с одним правильным ответом (1/3)")
        self.stage_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.stage_label.setAlignment(Qt.AlignCenter)
        
        exercise_layout.addWidget(self.stage_label)
        exercise_layout.addWidget(self.exercise_label)
        exercise_layout.addWidget(self.exercise_edit)
        exercise_layout.addWidget(QLabel("Ваш ответ:"))
        exercise_layout.addWidget(self.answer_edit)
        exercise_layout.addWidget(self.comment_label)
        exercise_layout.addWidget(self.comment_edit)
        exercise_layout.addLayout(exercise_buttons_layout)
        exercise_layout.addWidget(self.result_label)
        exercise_layout.addWidget(self.result_edit)
        
        exercise_panel.setLayout(exercise_layout)
        
        # Добавляем панели в главный макет
        main_layout.addWidget(text_panel, 1)
        main_layout.addWidget(explanation_panel, 1)
        main_layout.addWidget(exercise_panel, 1)
        
        central_widget.setLayout(main_layout)
        
        # Создаем меню
        self.create_menu()
        
        # Привязываем обработчики событий
        self.connect_signals()
        
        # Загружаем приветственный текст и справку
        self.load_demo_text()
    
    def create_menu(self):
        """Создает меню приложения."""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")
        
        create_new_course_action = file_menu.addAction("Создать новый курс...")
        create_new_course_action.triggered.connect(self.create_new_course)
        
        open_course_action = file_menu.addAction("Открыть курс...")
        open_course_action.triggered.connect(self.open_course)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Выход")
        exit_action.triggered.connect(self.close)
        
        # Меню "Инструменты"
        tools_menu = menubar.addMenu("Инструменты")
        
        settings_action = tools_menu.addAction("Настройки...")
        settings_action.triggered.connect(self.show_settings)
        
        # Меню "Справка"
        help_menu = menubar.addMenu("Справка")
        
        about_action = help_menu.addAction("О программе")
        about_action.triggered.connect(self.show_about)
    
    def connect_signals(self):
        """Привязывает обработчики событий к виджетам."""
        self.copy_text_btn.clicked.connect(self.copy_text)
        self.explain_btn.clicked.connect(self.generate_explanation)
        
        self.copy_explanation_btn.clicked.connect(self.copy_explanation)
        self.regenerate_btn.clicked.connect(self.regenerate_explanation)
        self.send_feedback_btn.clicked.connect(self.send_feedback)
        
        self.check_btn.clicked.connect(self.check_answer)
        self.next_exercise_btn.clicked.connect(self.generate_exercise)
        self.next_stage_btn.clicked.connect(self.next_stage)
    
    def load_demo_text(self):
        """Загружает приветственный текст и справку."""
        welcome_text = load_welcome_text()
        self.text_edit.setText(welcome_text)
        self.current_text = welcome_text
    
    def open_book(self):
        """Открывает диалог выбора книги."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть книгу", "", "Текстовые файлы (*.txt);;Word документы (*.docx);;Все файлы (*.*)"
        )
        
        if file_path:
            try:
                from _1_load_book import load_book
                text = load_book(file_path)
                self.text_edit.setText(text)
                self.current_text = text
                self.explanation_edit.clear()
                self.exercise_edit.clear()
                self.answer_edit.clear()
                self.result_edit.clear()
                
                QMessageBox.information(self, "Информация", f"Книга успешно загружена: {file_path}")
            except Exception as e:
                log_error(e)
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить книгу: {str(e)}")
    
    def generate_explanation(self):
        """Генерирует объяснение для текста."""
        if not self.current_text:
            QMessageBox.warning(self, "Предупреждение", "Нет текста для объяснения")
            return
        
        try:
            self.explanation_edit.setText("Генерация объяснения...")
            QApplication.processEvents()  # Обновляем интерфейс
            
            explanation = generate_explanation(
                self.current_text,
                self.settings.get("detail_level", "средний")
            )
            
            self.explanation_edit.setText(explanation)
            self.current_explanation = explanation
            
            # Генерируем упражнение после объяснения
            self.generate_exercise()
            
        except Exception as e:
            log_error(e)
            self.explanation_edit.setText(f"Ошибка при генерации объяснения: {str(e)}")
    
    def regenerate_explanation(self):
        """Генерирует объяснение заново."""
        self.generate_explanation()
    
    def send_feedback(self):
        """Отправляет отзыв для уточнения объяснения."""
        feedback = self.feedback_edit.text()
        
        if not feedback:
            QMessageBox.warning(self, "Предупреждение", "Введите ваш вопрос или отзыв")
            return
        
        if not self.current_text:
            QMessageBox.warning(self, "Предупреждение", "Нет текста для объяснения")
            return
        
        try:
            self.explanation_edit.setText("Генерация уточненного объяснения...")
            QApplication.processEvents()  # Обновляем интерфейс
            
            explanation = generate_explanation(
                self.current_text,
                self.settings.get("detail_level", "средний"),
                feedback
            )
            
            self.explanation_edit.setText(explanation)
            self.current_explanation = explanation
            self.feedback_edit.clear()
            
        except Exception as e:
            log_error(e)
            self.explanation_edit.setText(f"Ошибка при генерации уточненного объяснения: {str(e)}")
    
    def generate_exercise(self):
        """Генерирует упражнение."""
        if not self.current_text:
            QMessageBox.warning(self, "Предупреждение", "Нет текста для генерации упражнения")
            return
        
        try:
            self.exercise_edit.setText("Генерация упражнения...")
            QApplication.processEvents()  # Обновляем интерфейс
            
            # Получаем заголовок раздела, если есть
            section_title = self.current_section['title'] if self.current_section else ""
            
            # Обновляем текст этапа обучения
            self.update_stage_text()
            
            # Генерируем упражнения конкретного этапа
            new_exs = generate_exercises(
                self.current_text,
                self.settings.get("difficulty", "средний"),
                section_title,
                self.current_stage,
                self.previous_questions
            )
            
            if not new_exs:
                raise ValueError("Не удалось сгенерировать упражнения")
                
            # Фильтруем уже выполненные упражнения, если курс открыт
            if self.current_course_dir and self.current_section:
                sid = str(self.current_section['id'])
                answered = self.progress['sections'][sid]['answered']
                new_exs = [ex for ex in new_exs if ex['question'] not in answered]
                
                if not new_exs:
                    # Если все упражнения данного этапа выполнены, переходим к следующему
                    if self.current_stage < 2:
                        self.current_stage += 1
                        self.update_stage_text()
                        QMessageBox.information(self, "Информация", 
                                               f"Все упражнения этапа {self.current_stage} выполнены. Переходим к следующему этапу.")
                        # Рекурсивно вызываем генерацию упражнений для следующего этапа
                        self.generate_exercise()
                        return
                    else:
                        QMessageBox.information(self, "Информация", "Вы выполнили все упражнения для этого раздела!")
                        self.exercise_edit.clear()
                        return
            
            # Сохраняем сгенерированные упражнения и добавляем вопросы в список предыдущих
            self.current_exercises = new_exs
            exercise = new_exs[0]
            self.previous_questions.append(exercise['question'])
            
            # Ограничиваем список предыдущих вопросов (не более 20)
            if len(self.previous_questions) > 20:
                self.previous_questions = self.previous_questions[-20:]
            
            # Форматируем упражнение для отображения
            exercise_text = f"{exercise['question']}\n\n"
            
            if 'options' in exercise and exercise['options']:
                exercise_text += "Варианты ответов:\n"
                for i, option in enumerate(exercise['options'], 1):
                    exercise_text += f"{i}. {option}\n"
            
            self.exercise_edit.setText(exercise_text)
            self.answer_edit.clear()
            self.comment_edit.clear()
            self.result_edit.clear()
            
            # Показываем/скрываем поле для комментария в зависимости от этапа
            self.comment_label.setVisible(self.current_stage > 0)
            self.comment_edit.setVisible(self.current_stage > 0)
            
        except Exception as e:
            log_error(e)
            self.exercise_edit.setText(f"Ошибка при генерации упражнения: {str(e)}")
    
    def update_stage_text(self):
        """Обновляет текст с информацией о текущем этапе обучения."""
        stage_names = [
            "тесты с одним правильным ответом",
            "тесты с несколькими правильными ответами",
            "открытые вопросы"
        ]
        stage_name = stage_names[self.current_stage]
        self.stage_label.setText(f"Этап обучения: {stage_name} ({self.current_stage + 1}/3)")
    
    def next_stage(self):
        """Переход к следующему этапу обучения."""
        if self.current_stage < 2:
            self.current_stage += 1
            self.update_stage_text()
            self.generate_exercise()
        else:
            QMessageBox.information(self, "Информация", "Это последний этап обучения.")
    
    def check_answer(self):
        """Проверяет ответ пользователя."""
        if not self.current_exercises:
            QMessageBox.warning(self, "Предупреждение", "Нет активного упражнения")
            return
        
        user_answer = self.answer_edit.toPlainText().strip()
        
        if not user_answer:
            QMessageBox.warning(self, "Предупреждение", "Введите ваш ответ")
            return
        
        try:
            self.result_edit.setText("Проверка ответа...")
            QApplication.processEvents()  # Обновляем интерфейс
            
            exercise = self.current_exercises[0]  # Берем первое упражнение
            user_comment = self.comment_edit.toPlainText().strip()
            
            # Проверяем ответ с учетом комментария пользователя
            result = check_answer(exercise, user_answer, user_comment)
            
            # Обновляем историю в progress при правильном ответе
            if self.current_course_dir and result.get("is_correct", False):
                sid = str(self.current_section['id'])
                qtext = exercise['question']
                sp = self.progress['sections'][sid]
                if qtext not in sp['answered']:
                    sp['answered'].append(qtext)
                    sp['exercises_completed'] += 1
                    save_progress(os.path.join(self.current_course_dir, "progress.json"), self.progress)
            
            # Форматируем результат в зависимости от этапа
            if self.current_stage == 2:  # Открытые вопросы с подробным отзывом
                result_text = ""
                if result.get("is_correct", False):
                    result_text += "✓ Молодец! Ваш ответ соответствует требованиям.\n\n"
                else:
                    result_text += "Ваш ответ нуждается в доработке.\n\n"
                
                result_text += f"Отзыв преподавателя:\n{result.get('feedback', '')}\n\n"
                
                if "strengths" in result:
                    result_text += "Сильные стороны вашего ответа:\n"
                    for i, strength in enumerate(result["strengths"], 1):
                        result_text += f"{i}. {strength}\n"
                    result_text += "\n"
                
                if "areas_for_improvement" in result:
                    result_text += "Области для улучшения:\n"
                    for i, area in enumerate(result["areas_for_improvement"], 1):
                        result_text += f"{i}. {area}\n"
            else:
                # Стандартный формат для тестов (этапы 0 и 1)
                result_text = ""
                if result.get("is_correct", False):
                    result_text += "✓ Правильно!\n\n"
                else:
                    result_text += "✗ Неправильно.\n\n"
                
                result_text += f"Отзыв: {result.get('feedback', '')}\n\n"
                
                if not result.get("is_correct", False):
                    result_text += f"Правильный ответ: {result.get('correct_answer', '')}"
            
            self.result_edit.setText(result_text)
            
        except Exception as e:
            log_error(e)
            self.result_edit.setText(f"Ошибка при проверке ответа: {str(e)}")
    
    def copy_text(self):
        """Копирует текст в буфер обмена."""
        QApplication.clipboard().setText(self.text_edit.toPlainText())
        QMessageBox.information(self, "Информация", "Текст скопирован в буфер обмена")
    
    def copy_explanation(self):
        """Копирует объяснение в буфер обмена."""
        QApplication.clipboard().setText(self.explanation_edit.toPlainText())
        QMessageBox.information(self, "Информация", "Объяснение скопировано в буфер обмена")
    
    def show_settings(self):
        """Показывает диалог настроек."""
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.settings = dialog.get_settings()
            from _5_save_settings import save_settings
            save_settings("settings.json", self.settings)
            QMessageBox.information(self, "Информация", "Настройки сохранены")
    
    def show_about(self):
        """Показывает информацию о программе."""
        QMessageBox.about(
            self,
            "О программе",
            "Tutor - Интерактивное обучение\n\n"
            "Версия: 1.0\n\n"
            "Приложение для интерактивного обучения с использованием нейросети для генерации объяснений и упражнений."
        )
    
    def create_course_structure(self):
        """Создает структуру курса на основе загруженной книгу."""
        success, directory, structure = create_course_structure(self, self.current_text)
        
        if success and structure:
            # Сохраняем структуру и загружаем прогресс
            self.current_course_dir = directory
            self.current_course_structure = structure
            self.progress = load_progress(os.path.join(directory, "progress.json"))
            self.current_section = None
            
            # Предлагаем открыть первый раздел
            reply = QMessageBox.question(
                self, 
                "Открыть раздел", 
                "Структура курса создана. Хотите открыть первый раздел?", 
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes and len(structure) > 0:
                self.display_section(structure[0])
    
    def open_course(self):
        """Открывает созданный курс."""
        success, directory, structure = open_course(self)
        
        if success and structure:
            # Сохраняем структуру и загружаем прогресс
            self.current_course_dir = directory
            self.current_course_structure = structure
            self.progress = load_progress(os.path.join(directory, "progress.json"))
            self.current_section = None
            
            # Показываем диалог выбора раздела
            selected_section = select_section(self, structure)
            
            if selected_section:
                self.display_section(selected_section)
    
    def display_section(self, section):
        """Отображает содержимое раздела в интерфейсе."""
        self.current_section = section
        self.text_edit.setText(section['content'])
        self.current_text = section['content']
        self.explanation_edit.clear()
        self.exercise_edit.clear()
        self.answer_edit.clear()
        self.result_edit.clear()
        
        # Обновляем заголовок окна
        self.setWindowTitle(f"Tutor - {section['title']}")
        
        QMessageBox.information(self, "Информация", f"Открыт раздел: {section['title']}")

    def create_new_course(self):
        """Создает новый курс в одно действие (открытие книги + создание структуры)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть книгу для создания курса", "", 
            "Текстовые файлы (*.txt);;Word документы (*.docx);;Все файлы (*.*)"
        )
        
        if not file_path:
            return  # Пользователь отменил выбор книги
            
        try:
            # Загружаем книгу
            from _1_load_book import load_book
            text = load_book(file_path)
            self.text_edit.setText(text)
            self.current_text = text
            self.explanation_edit.clear()
            self.exercise_edit.clear()
            self.answer_edit.clear()
            self.result_edit.clear()
            
            # Запрашиваем директорию для сохранения курса
            directory = QFileDialog.getExistingDirectory(
                self, "Выберите директорию для сохранения курса"
            )
            
            if not directory:
                return  # Пользователь отменил выбор директории
                
            # Создаем структуру курса
            from _3_initialize_course import initialize_course
            from _6_load_course_structure import load_course_structure
            
            initialize_course(file_path, directory)
            
            # Загружаем созданную структуру
            structure_path = os.path.join(directory, "structure.json")
            structure = load_course_structure(structure_path)
            
            # Сохраняем структуру и загружаем прогресс
            self.current_course_dir = directory
            self.current_course_structure = structure
            self.progress = load_progress(os.path.join(directory, "progress.json"))
            self.current_section = None
            
            QMessageBox.information(
                self, "Информация", 
                f"Курс успешно создан на основе книги:\n{file_path}\n\nСтруктура сохранена в:\n{directory}"
            )
            
            # Предлагаем открыть первый раздел
            if structure:
                reply = QMessageBox.question(
                    self, 
                    "Открыть раздел", 
                    "Структура курса создана. Хотите открыть первый раздел?", 
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.display_section(structure[0])
                    
        except Exception as e:
            log_error(e)
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать курс: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
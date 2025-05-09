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
from _18_select_section import select_section, get_course_sections
from _19_load_demo_text import load_welcome_text
from _8_load_progress import load_progress
from _9_save_progress import save_progress

# Импортируем UI модули
from _ui_settings_dialog import SettingsDialog
from _ui_text_processing import load_demo_text, open_book
from _ui_explanation_generation import (generate_explanation, regenerate_explanation, 
                                          send_feedback)
from _ui_exercise_generation import (generate_exercise, check_answer, update_stage_text,
                                       next_stage)
from _ui_course_management import (create_course_structure, open_course, display_section,
                                     create_new_course)
from _ui_main_window import update_courses_menu, open_course_by_path

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
        self.progress = {"sections": {}}  # Инициализируем структуру progress с пустым разделом sections
        self.current_stage = 0  # Этап обучения (0, 1 или 2)
        self.previous_questions = []  # Список предыдущих вопросов для избежания повторений
        
        # Создаем центральный виджет и макет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный макет - горизонтальный для трех панелей
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)  # Добавляем отступ между панелями
        
        # Панель 1: Исходный текст
        text_panel = QWidget()
        text_layout = QVBoxLayout()
        
        self.text_label = QLabel("Исходный текст")
        self.text_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.text_label.setWordWrap(True)
        self.text_label.setMinimumHeight(40)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        
        text_buttons_layout = QHBoxLayout()
        self.copy_text_btn = QPushButton("Копировать")
        self.toc_btn = QPushButton("Оглавление")
        self.explain_btn = QPushButton("Объяснить")
        
        text_buttons_layout.addWidget(self.copy_text_btn)
        text_buttons_layout.addWidget(self.toc_btn)
        text_buttons_layout.addWidget(self.explain_btn)
        
        text_layout.addWidget(self.text_label)
        text_layout.addWidget(self.text_edit)
        text_layout.addLayout(text_buttons_layout)
        
        text_panel.setLayout(text_layout)
        text_panel.setMinimumWidth(300)
        
        # Панель 2: Объяснение
        explanation_panel = QWidget()
        explanation_layout = QVBoxLayout()
        
        self.explanation_label = QLabel("Объяснение")
        self.explanation_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.explanation_label.setWordWrap(True)
        self.explanation_label.setMinimumHeight(40)
        
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
        explanation_panel.setMinimumWidth(300)
        
        # Панель 3: Упражнения
        exercise_panel = QWidget()
        exercise_layout = QVBoxLayout()
        
        self.exercise_label = QLabel("Упражнение")
        self.exercise_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.exercise_label.setWordWrap(True)
        self.exercise_label.setMinimumHeight(40)
        
        self.exercise_edit = QTextEdit()
        self.exercise_edit.setReadOnly(True)
        
        self.answer_edit = QTextEdit()
        self.answer_edit.setPlaceholderText("Введите ваш ответ здесь...")
        
        exercise_buttons_layout = QHBoxLayout()
        self.check_btn = QPushButton("Проверить ответ")
        self.next_exercise_btn = QPushButton("Новое упражнение")
        self.next_stage_btn = QPushButton("Следующий этап")
        # Кнопка для обновления оценки раздела
        self.update_results_btn = QPushButton("Обновить результаты")
        
        exercise_buttons_layout.addWidget(self.check_btn)
        exercise_buttons_layout.addWidget(self.next_exercise_btn)
        exercise_buttons_layout.addWidget(self.next_stage_btn)
        exercise_buttons_layout.addWidget(self.update_results_btn)
        
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
        exercise_layout.addLayout(exercise_buttons_layout)
        exercise_layout.addWidget(self.result_label)
        exercise_layout.addWidget(self.result_edit)
        
        exercise_panel.setLayout(exercise_layout)
        exercise_panel.setMinimumWidth(300)
        
        # Добавляем панели в главный макет с минимальной шириной и соотношением растяжения
        main_layout.addWidget(text_panel, 3)
        main_layout.addWidget(explanation_panel, 3)
        main_layout.addWidget(exercise_panel, 4)
        
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
        file_menu.setObjectName("file_menu")  # Устанавливаем objectName для поиска меню
        
        create_new_course_action = file_menu.addAction("Создать новый курс...")
        create_new_course_action.triggered.connect(self.create_new_course)
        
        open_course_action = file_menu.addAction("Открыть курс...")
        open_course_action.triggered.connect(self.open_course)
        
        # Подменю доступных курсов будет добавлено в update_courses_menu
        
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
        
        # Обновляем меню курсов
        update_courses_menu(self)
    
    def connect_signals(self):
        """Привязывает обработчики событий к виджетам."""
        self.copy_text_btn.clicked.connect(self.copy_text)
        self.toc_btn.clicked.connect(self.open_toc)
        self.explain_btn.clicked.connect(self.generate_explanation)
        
        self.copy_explanation_btn.clicked.connect(self.copy_explanation)
        self.regenerate_btn.clicked.connect(self.regenerate_explanation)
        self.send_feedback_btn.clicked.connect(self.send_feedback)
        
        self.check_btn.clicked.connect(self.check_answer)
        self.next_exercise_btn.clicked.connect(self.generate_exercise)
        self.next_stage_btn.clicked.connect(self.next_stage)
        self.update_results_btn.clicked.connect(self.update_evaluation)
    
    def load_demo_text(self):
        """Загружает приветственный текст и справку."""
        load_demo_text(self)
    
    def open_book(self):
        """Открывает диалог выбора книги."""
        open_book(self)
    
    def generate_explanation(self):
        """Генерирует объяснение для текста."""
        generate_explanation(self)
    
    def regenerate_explanation(self):
        """Генерирует объяснение заново."""
        regenerate_explanation(self)
    
    def send_feedback(self):
        """Отправляет отзыв для уточнения объяснения."""
        send_feedback(self)
    
    def generate_exercise(self):
        """Генерирует упражнение."""
        generate_exercise(self)
    
    def update_stage_text(self):
        """Обновляет текст с информацией о текущем этапе обучения."""
        update_stage_text(self)
    
    def next_stage(self):
        """Переход к следующему этапу обучения."""
        next_stage(self)
    
    def check_answer(self):
        """Проверяет ответ пользователя."""
        check_answer(self)
    
    def open_next_section(self):
        """Открывает следующий раздел учебника."""
        # Проверяем, открыт ли курс и есть ли текущий раздел
        if not self.current_course_dir or not self.current_section:
            QMessageBox.warning(self, "Предупреждение", "Необходимо открыть курс для доступа к разделам.")
            return
        
        # Получаем все секции текущего курса
        sections = get_course_sections(self.current_course_dir)
        
        # Находим индекс текущей секции
        current_id = self.current_section['id']
        current_index = -1
        
        for i, section in enumerate(sections):
            if section['id'] == current_id:
                current_index = i
                break
        
        # Проверяем, есть ли следующая секция
        if current_index >= 0 and current_index < len(sections) - 1:
            # Получаем следующую секцию
            next_section = sections[current_index + 1]
            
            # Отображаем следующую секцию
            self.display_section(next_section)
            
            # Сбрасываем состояние кнопки "Следующий этап"
            self.next_stage_btn.setText("Следующий этап")
            try:
                self.next_stage_btn.clicked.disconnect()
            except:
                pass
            self.next_stage_btn.clicked.connect(self.next_stage)
            
            # Сбрасываем current_stage на первый этап для нового раздела
            self.current_stage = 0
            self.update_stage_text()
        else:
            QMessageBox.information(self, "Информация", "Это последний раздел учебника. Обучение завершено!")
    
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
        create_course_structure(self)
    
    def open_course(self):
        """Открывает созданный курс."""
        success, directory, structure = open_course(self)
        if success:
            self.current_course_dir = directory
            self.current_course_structure = structure
            
            # Отображаем первый раздел, если он есть
            if structure and len(structure) > 0:
                self.display_section(structure[0])
                
            # Обновляем меню курсов
            update_courses_menu(self)
    
    def display_section(self, section):
        """Отображает содержимое раздела в интерфейсе."""
        display_section(self, section)

    def create_new_course(self):
        """Создает новый курс в одно действие (открытие книги + создание структуры)."""
        success = create_new_course(self)
        if success:
            # Обновляем меню курсов после создания нового курса
            update_courses_menu(self)

    def open_toc(self):
        """Открывает оглавление курса для выбора раздела."""
        # Проверяем, открыт ли курс
        if not self.current_course_dir or not self.current_course_structure:
            QMessageBox.warning(self, "Предупреждение", "Необходимо открыть курс для доступа к оглавлению.")
            return
            
        # Показываем диалог выбора раздела
        section = select_section(self, self.current_course_structure)
        
        # Если пользователь выбрал раздел, отображаем его
        if section:
            self.display_section(section)
            
            # Сбрасываем current_stage на первый этап для нового раздела
            self.current_stage = 0
            self.update_stage_text()

    # Добавляем метод открытия курса по пути
    def open_course_by_path(self, course_path):
        """Открывает курс по указанному пути."""
        open_course_by_path(self, course_path)
        # Обновляем меню курсов после открытия
        update_courses_menu(self)

    def update_evaluation(self):
        """Пересчитывает и сохраняет оценку раздела через LLM"""
        if not self.current_course_dir or not self.current_section:
            QMessageBox.warning(self, "Предупреждение", "Откройте раздел курса для обновления результатов.")
            return
        from _20_evaluate_section import evaluate_section
        sid = str(self.current_section['id'])
        res = evaluate_section(self.progress, sid)
        # Сохраняем результат оценки в прогрессе
        self.progress['sections'][sid]['evaluation'] = res
        save_progress(os.path.join(self.current_course_dir, "progress.json"), self.progress)
        QMessageBox.information(self, "Результаты обновлены", f"Оценка: {res['score']}\nКомментарий: {res['comment']}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
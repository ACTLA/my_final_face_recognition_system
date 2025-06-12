# gui/main_application.py
import tkinter as tk
from tkinter import ttk
import os
from core.database_manager import DatabaseManager
from core.face_engine import FaceRecognitionEngine
from core.camera_manager import CameraManager
from gui.recognition_widget import RecognitionWidget
from gui.management_widget import ManagementWidget
from config.settings import *

class FaceRecognitionApp:
    """Основное приложение распознавания лиц"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=THEME_COLOR)
        
        # Инициализация компонентов
        self.db = DatabaseManager()
        self.face_engine = FaceRecognitionEngine()
        self.camera_manager = CameraManager()
        
        # Переменная для системы аудита (устанавливается при интеграции)
        self.audit = None
        
        # Создание папки для фотографий
        if not os.path.exists(PHOTOS_DIR):
            os.makedirs(PHOTOS_DIR)
        
        # Загрузка кодировок
        self.load_encodings()
        
        # Настройка интерфейса
        self.setup_ui()
    
    def setup_ui(self):
        """Создание пользовательского интерфейса"""
        # Заголовок
        self.create_header()
        
        # Создание вкладок
        self.create_notebook()
        
        # Создание виджетов вкладок
        self.create_tabs()
    
    def create_header(self):
        """Создание заголовка приложения"""
        header_frame = tk.Frame(self.root, bg=THEME_COLOR, height=80)
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        header_frame.pack_propagate(False)
        
        title_frame = tk.Frame(header_frame, bg=THEME_COLOR)
        title_frame.pack(side="left", fill="y")
        
        # Иконка
        icon_label = tk.Label(title_frame, text="👤", font=("Arial", 24), 
                             bg=THEME_COLOR, fg="white")
        icon_label.pack(side="left", padx=(0, 10))
        
        # Название
        title_label = tk.Label(title_frame, text="СИСТЕМА РАСПОЗНАВАНИЯ ЛИЦ", 
                              font=("Arial", 18, "bold"), bg=THEME_COLOR, fg="white")
        title_label.pack(side="left")
    
    def create_notebook(self):
        """Создание виджета вкладок"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.TNotebook.Tab', 
                       padding=[20, 10], 
                       font=('Arial', 12, 'bold'))
        
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def create_tabs(self):
        """Создание виджетов вкладок"""
        # Вкладка распознавания
        self.recognition_widget = RecognitionWidget(
            self.notebook, 
            self.camera_manager, 
            self.face_engine, 
            self.db
        )
        
        # Вкладка управления пользователями
        self.management_widget = ManagementWidget(
            self.notebook, 
            self.db, 
            self.face_engine,
            self.load_encodings  # Callback для обновления кодировок
        )
        
        # Устанавливаем ссылку на аудит для виджетов
        self.recognition_widget.set_audit_logger(lambda: self.audit)
        self.management_widget.set_audit_logger(lambda: self.audit)
    
    def load_encodings(self):
        """Загрузка кодировок лиц"""
        try:
            encodings, user_ids = self.db.get_all_encodings()
            self.face_engine.load_encodings(encodings, user_ids)
            
            # Логирование
            if self.audit:
                self.audit.log_system_event("encodings_loaded", "success")
            
        except Exception as e:
            print(f"Ошибка загрузки кодировок: {e}")
            if self.audit:
                self.audit.log_system_event("encodings_loaded", "failed")
    
    def on_closing(self):
        """Обработка закрытия приложения"""
        # Останавливаем камеру
        self.recognition_widget.stop_camera()
        
        # Закрываем приложение
        self.root.destroy()
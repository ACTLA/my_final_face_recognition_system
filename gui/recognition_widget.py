# gui/recognition_widget.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import datetime
import os
import cv2
from config.settings import *

class RecognitionWidget:
    """Виджет распознавания лиц"""
    
    def __init__(self, parent_notebook, camera_manager, face_engine, db):
        self.notebook = parent_notebook
        self.camera_manager = camera_manager
        self.face_engine = face_engine
        self.db = db
        
        # Переменные для контроля времени
        self.last_recognition_time = None
        self.last_unknown_time = None
        self.last_recognition_timer = None
        
        # Функция получения аудит логгера (устанавливается извне)
        self.get_audit_logger = None
        
        # Создание вкладки
        self.setup_widget()
    
    def set_audit_logger(self, get_audit_func):
        """Установка функции получения аудит логгера"""
        self.get_audit_logger = get_audit_func
    
    def setup_widget(self):
        """Создание интерфейса вкладки"""
        # Создание фрейма вкладки
        self.frame = tk.Frame(self.notebook, bg=THEME_COLOR)
        self.notebook.add(self.frame, text="  🎥 Распознавание лиц  ")
        
        # Основной контейнер
        main_container = tk.Frame(self.frame, bg=THEME_COLOR)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Левая панель - камера
        self.create_camera_panel(main_container)
        
        # Правая панель - информация
        self.create_info_panel(main_container)
    
    def create_camera_panel(self, parent):
        """Создание панели камеры"""
        left_panel = tk.Frame(parent, bg="white", relief="raised", bd=2, width=500)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Заголовок
        video_header = tk.Frame(left_panel, bg="#7C3AED", height=40)
        video_header.pack(fill="x")
        video_header.pack_propagate(False)
        
        video_title = tk.Label(video_header, text="КАМЕРА", 
                              font=("Arial", 12, "bold"), bg="#7C3AED", fg="white")
        video_title.pack(expand=True)
        
        # Видео контейнер
        video_container = tk.Frame(left_panel, bg="black", width=480, height=360)
        video_container.pack(padx=10, pady=10)
        video_container.pack_propagate(False)
        
        self.video_label = tk.Label(video_container, text="Камера не запущена", 
                                   bg="black", fg="white", font=("Arial", 12))
        self.video_label.pack(fill="both", expand=True)
        
        # Кнопки управления
        self.create_camera_controls(left_panel)
    
    def create_camera_controls(self, parent):
        """Создание кнопок управления камерой"""
        controls = tk.Frame(parent, bg="white", height=50)
        controls.pack(fill="x", padx=10, pady=(0, 10))
        controls.pack_propagate(False)
        
        self.start_button = tk.Button(controls, text="Запуск", 
                                     font=("Arial", 10, "bold"), bg="#10B981", fg="white",
                                     relief="flat", padx=15, pady=6, command=self.start_camera)
        self.start_button.pack(side="left", padx=(0, 5))
        
        self.stop_button = tk.Button(controls, text="Стоп", 
                                    font=("Arial", 10, "bold"), bg="#EF4444", fg="white",
                                    relief="flat", padx=15, pady=6, command=self.stop_camera,
                                    state="disabled")
        self.stop_button.pack(side="left", padx=(0, 5))
    
    def create_info_panel(self, parent):
        """Создание панели информации"""
        right_panel = tk.Frame(parent, bg="white", relief="raised", bd=2)
        right_panel.pack(side="right", fill="both", expand=True)
        
        info_content = tk.Frame(right_panel, bg="white")
        info_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Заголовок
        header = tk.Label(info_content, text="РАСПОЗНАННЫЙ ПОЛЬЗОВАТЕЛЬ", 
                         font=("Arial", 14, "bold"), bg="white", fg="#374151")
        header.pack(anchor="w", pady=(0, 15))
        
        # Статус
        self.status_label = tk.Label(info_content, text="⏳ Ожидание...", 
                                    font=("Arial", 16, "bold"), bg="white", fg="#6B7280")
        self.status_label.pack(anchor="w", pady=(0, 15))
        
        # Информация о пользователе
        self.create_user_info(info_content)
        
        # Фотография
        self.create_photo_display(info_content)
    
    def create_user_info(self, parent):
        """Создание блока информации о пользователе"""
        info_container = tk.Frame(parent, bg="#F9FAFB", relief="solid", bd=1)
        info_container.pack(fill="x", pady=(0, 15))
        
        # ID пользователя
        id_frame = tk.Frame(info_container, bg="#F9FAFB")
        id_frame.pack(fill="x", padx=10, pady=8)
        
        tk.Label(id_frame, text="ID:", font=("Arial", 11, "bold"), 
                bg="#F9FAFB", fg="#374151").pack(side="left")
        self.user_id_label = tk.Label(id_frame, text="—", font=("Arial", 11), 
                                     bg="#F9FAFB", fg="#6B7280")
        self.user_id_label.pack(side="right")
        
        # Имя пользователя
        name_frame = tk.Frame(info_container, bg="#F9FAFB")
        name_frame.pack(fill="x", padx=10, pady=8)
        
        tk.Label(name_frame, text="Имя:", font=("Arial", 11, "bold"), 
                bg="#F9FAFB", fg="#374151").pack(side="left")
        self.name_label = tk.Label(name_frame, text="—", font=("Arial", 11), 
                                  bg="#F9FAFB", fg="#6B7280")
        self.name_label.pack(side="right")
    
    def create_photo_display(self, parent):
        """Создание области отображения фотографии"""
        photo_frame = tk.Frame(parent, bg="white")
        photo_frame.pack(fill="x")
        
        tk.Label(photo_frame, text="Фотография:", font=("Arial", 11, "bold"), 
                bg="white", fg="#374151").pack(anchor="w", pady=(0, 8))
        
        photo_container = tk.Frame(photo_frame, bg="#F3F4F6", relief="solid", bd=1, 
                                  width=180, height=180)
        photo_container.pack(pady=(0, 10))
        photo_container.pack_propagate(False)
        
        self.photo_display = tk.Label(photo_container, text="Нет фото", 
                                     bg="#F3F4F6", font=("Arial", 10), fg="#6B7280")
        self.photo_display.pack(fill="both", expand=True)
    
    def start_camera(self):
        """Запуск камеры"""
        if self.camera_manager.start_camera():
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            # Логирование
            audit = self.get_audit_logger() if self.get_audit_logger else None
            if audit:
                audit.log_system_event("camera_start", "success")
            
            self.process_frame()
        else:
            # Логирование ошибки
            audit = self.get_audit_logger() if self.get_audit_logger else None
            if audit:
                audit.log_system_event("camera_start", "failed")
            
            messagebox.showerror("Ошибка", "Не удалось подключиться к камере!")
    
    def stop_camera(self):
        """Остановка камеры"""
        self.camera_manager.stop_camera()
        
        # Очистка таймеров
        if self.last_recognition_timer:
            self.frame.after_cancel(self.last_recognition_timer)
            self.last_recognition_timer = None
        
        self.last_recognition_time = None
        self.last_unknown_time = None
        
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        self.video_label.config(image="", text="Камера остановлена")
        self.reset_user_info()
        
        # Логирование
        audit = self.get_audit_logger() if self.get_audit_logger else None
        if audit:
            audit.log_system_event("camera_stop", "success")
    
    def process_frame(self):
        """Обработка кадров с камеры"""
        if not self.camera_manager.is_camera_running():
            return
        
        frame = self.camera_manager.get_frame()
        if frame is None:
            self.frame.after(30, self.process_frame)
            return
        
        # Распознавание лиц
        recognized_faces = self.face_engine.recognize_faces(frame, FRAME_SCALE)
        
        current_time = datetime.datetime.now()
        recognized_user = None
        
        # Проверка задержек
        can_recognize_known = self._can_recognize_known(current_time)
        can_recognize_unknown = self._can_recognize_unknown(current_time)
        
        # Обработка найденных лиц
        for face_info in recognized_faces:
            name, color = self._process_face(face_info, current_time, 
                                           can_recognize_known, can_recognize_unknown)
            
            # Рисуем рамку
            self.face_engine.draw_face_rectangle(frame, face_info, color, name)
            
            # Если распознали пользователя, сохраняем для отображения
            if face_info['is_known'] and can_recognize_known:
                user_data = self.db.get_user(face_info['user_id'])
                if user_data:
                    recognized_user = user_data
                    self.last_recognition_time = current_time
                    self._schedule_info_clear()
        
        # Обновление информации о пользователе
        if recognized_user:
            self.update_user_info(recognized_user)
        elif not recognized_faces and not self.last_recognition_timer:
            self.reset_user_info()
        
        # Отображение кадра
        self._display_frame(frame)
        
        # Планируем следующий кадр
        self.frame.after(30, self.process_frame)
    
    def _can_recognize_known(self, current_time):
        """Проверка возможности распознавания известного лица"""
        if not self.last_recognition_time:
            return True
        
        elapsed = (current_time - self.last_recognition_time).total_seconds()
        return elapsed >= RECOGNITION_DELAY
    
    def _can_recognize_unknown(self, current_time):
        """Проверка возможности распознавания неизвестного лица"""
        if not self.last_unknown_time:
            return True
        
        elapsed = (current_time - self.last_unknown_time).total_seconds()
        return elapsed >= UNKNOWN_FACE_DELAY
    
    def _process_face(self, face_info, current_time, can_recognize_known, can_recognize_unknown):
        """Обработка информации о лице"""
        audit = self.get_audit_logger() if self.get_audit_logger else None
        
        if face_info['is_known']:
            if can_recognize_known:
                # Логируем успешное распознавание
                if audit:
                    audit.log_recognition(face_info['user_id'], True, face_info['confidence'])
                
                user_data = self.db.get_user(face_info['user_id'])
                name = user_data[2] if user_data else "Неизвестно"
                color = (0, 255, 0)  # Зеленый
            else:
                # Ожидание для известного пользователя
                time_left = RECOGNITION_DELAY - (current_time - self.last_recognition_time).total_seconds()
                name = f"{time_left:.1f}s"
                color = (0, 255, 255)  # Желтый
        else:
            if can_recognize_unknown:
                # Логируем неудачное распознавание
                if audit:
                    audit.log_recognition(None, False, face_info['confidence'])
                
                self.last_unknown_time = current_time
                name = ""
                color = (0, 0, 255)  # Красный
            else:
                # Ожидание для неизвестного лица
                time_left = UNKNOWN_FACE_DELAY - (current_time - self.last_unknown_time).total_seconds()
                name = f"{time_left:.1f}s"
                color = (0, 255, 255)  # Желтый
        
        return name, color
    
    def _schedule_info_clear(self):
        """Планирование очистки информации"""
        if self.last_recognition_timer:
            self.frame.after_cancel(self.last_recognition_timer)
        
        self.last_recognition_timer = self.frame.after(
            INFO_DISPLAY_DURATION * 1000, 
            self.reset_user_info
        )
    
    def _display_frame(self, frame):
        """Отображение кадра в интерфейсе"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        photo = ImageTk.PhotoImage(pil_image)
        
        self.video_label.config(image=photo, text="")
        self.video_label.image = photo
    
    def update_user_info(self, user_data):
        """Обновление информации о пользователе"""
        user_id = user_data[1]
        name = user_data[2]
        photo_path = user_data[3]
        
        # Статус с временной меткой
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        self.status_label.config(text=f"✅ Распознан в {current_time}", fg="#10B981")
        self.user_id_label.config(text=user_id)
        self.name_label.config(text=name)
        
        # Загрузка фотографии
        if photo_path and os.path.exists(photo_path):
            try:
                pil_image = Image.open(photo_path)
                pil_image = pil_image.resize((170, 170), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(pil_image)
                
                self.photo_display.config(image=photo, text="")
                self.photo_display.image = photo
                
            except Exception as e:
                print(f"Ошибка загрузки фото: {e}")
                self.photo_display.config(image="", text="Ошибка\nзагрузки", 
                                        font=("Arial", 9), fg="#EF4444")
        else:
            self.photo_display.config(image="", text="Фото\nне найдено", 
                                    font=("Arial", 9), fg="#6B7280")
    
    def reset_user_info(self):
        """Сброс информации о пользователе"""
        self.status_label.config(text="⏳ Ожидание...", fg="#6B7280")
        self.user_id_label.config(text="—")
        self.name_label.config(text="—")
        self.photo_display.config(image="", text="Нет фото", 
                                 font=("Arial", 10), fg="#6B7280")
        
        if self.last_recognition_timer:
            self.last_recognition_timer = None
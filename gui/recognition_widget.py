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
        # Сохраняем ссылки на основные компоненты системы
        self.notebook = parent_notebook
        self.camera_manager = camera_manager
        self.face_engine = face_engine
        self.db = db
        
        # Переменные для контроля времени между распознаваниями
        self.last_recognition_time = None  # Время последнего успешного распознавания
        self.last_unknown_time = None      # Время последнего неуспешного распознавания
        self.last_recognition_timer = None # Таймер для очистки информации о пользователе
        
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
        # Создаем левую панель с фиксированной шириной для камеры
        left_panel = tk.Frame(parent, bg="white", relief="raised", bd=2, width=500)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)  # Запрещаем изменение размера
        
        # Заголовок панели камеры
        video_header = tk.Frame(left_panel, bg="#7C3AED", height=40)
        video_header.pack(fill="x")
        video_header.pack_propagate(False)
        
        video_title = tk.Label(video_header, text="КАМЕРА", 
                              font=("Arial", 12, "bold"), bg="#7C3AED", fg="white")
        video_title.pack(expand=True)
        
        # Контейнер для видео с фиксированными размерами
        video_container = tk.Frame(left_panel, bg="black", width=480, height=360)
        video_container.pack(padx=10, pady=10)
        video_container.pack_propagate(False)
        
        # Лейбл для отображения видео или сообщений
        self.video_label = tk.Label(video_container, text="Камера не запущена", 
                                   bg="black", fg="white", font=("Arial", 12))
        self.video_label.pack(fill="both", expand=True)
        
        # Кнопки управления камерой
        self.create_camera_controls(left_panel)
    
    def create_camera_controls(self, parent):
        """Создание кнопок управления камерой"""
        # Контейнер для кнопок управления
        controls = tk.Frame(parent, bg="white", height=50)
        controls.pack(fill="x", padx=10, pady=(0, 10))
        controls.pack_propagate(False)
        
        # Кнопка запуска камеры
        self.start_button = tk.Button(controls, text="Запуск", 
                                     font=("Arial", 10, "bold"), bg="#10B981", fg="white",
                                     relief="flat", padx=15, pady=6, command=self.start_camera)
        self.start_button.pack(side="left", padx=(0, 5))
        
        # Кнопка остановки камеры (изначально отключена)
        self.stop_button = tk.Button(controls, text="Стоп", 
                                    font=("Arial", 10, "bold"), bg="#EF4444", fg="white",
                                    relief="flat", padx=15, pady=6, command=self.stop_camera,
                                    state="disabled")
        self.stop_button.pack(side="left", padx=(0, 5))
    
    def create_info_panel(self, parent):
        """Создание панели информации о распознанном пользователе"""
        # Правая панель для отображения информации
        right_panel = tk.Frame(parent, bg="white", relief="raised", bd=2)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Контейнер для содержимого панели информации
        info_content = tk.Frame(right_panel, bg="white")
        info_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Заголовок панели
        header = tk.Label(info_content, text="РАСПОЗНАННЫЙ ПОЛЬЗОВАТЕЛЬ", 
                         font=("Arial", 14, "bold"), bg="white", fg="#374151")
        header.pack(anchor="w", pady=(0, 15))
        
        # Статус распознавания
        self.status_label = tk.Label(info_content, text="⏳ Ожидание...", 
                                    font=("Arial", 16, "bold"), bg="white", fg="#6B7280")
        self.status_label.pack(anchor="w", pady=(0, 15))
        
        # Информация о пользователе
        self.create_user_info(info_content)
        
        # Отображение фотографии пользователя
        self.create_photo_display(info_content)
    
    def create_user_info(self, parent):
        """Создание блока информации о пользователе"""
        # Контейнер для информации о пользователе
        info_container = tk.Frame(parent, bg="#F9FAFB", relief="solid", bd=1)
        info_container.pack(fill="x", pady=(0, 15))
        
        # Строка с ID пользователя
        id_frame = tk.Frame(info_container, bg="#F9FAFB")
        id_frame.pack(fill="x", padx=10, pady=8)
        
        tk.Label(id_frame, text="ID:", font=("Arial", 11, "bold"), 
                bg="#F9FAFB", fg="#374151").pack(side="left")
        self.user_id_label = tk.Label(id_frame, text="—", font=("Arial", 11), 
                                     bg="#F9FAFB", fg="#6B7280")
        self.user_id_label.pack(side="right")
        
        # Строка с именем пользователя
        name_frame = tk.Frame(info_container, bg="#F9FAFB")
        name_frame.pack(fill="x", padx=10, pady=8)
        
        tk.Label(name_frame, text="Имя:", font=("Arial", 11, "bold"), 
                bg="#F9FAFB", fg="#374151").pack(side="left")
        self.name_label = tk.Label(name_frame, text="—", font=("Arial", 11), 
                                  bg="#F9FAFB", fg="#6B7280")
        self.name_label.pack(side="right")
    
    def create_photo_display(self, parent):
        """Создание области отображения фотографии пользователя"""
        # Контейнер для фотографии
        photo_frame = tk.Frame(parent, bg="white")
        photo_frame.pack(fill="x")
        
        # Заголовок для фотографии
        tk.Label(photo_frame, text="Фотография:", font=("Arial", 11, "bold"), 
                bg="white", fg="#374151").pack(anchor="w", pady=(0, 8))
        
        # Контейнер для фотографии с фиксированными размерами
        photo_container = tk.Frame(photo_frame, bg="#F3F4F6", relief="solid", bd=1, 
                                  width=180, height=180)
        photo_container.pack(pady=(0, 10))
        photo_container.pack_propagate(False)
        
        # Лейбл для отображения фотографии
        self.photo_display = tk.Label(photo_container, text="Нет фото", 
                                     bg="#F3F4F6", font=("Arial", 10), fg="#6B7280")
        self.photo_display.pack(fill="both", expand=True)
    
    def start_camera(self):
        """Запуск камеры"""
        # Пытаемся запустить камеру
        if self.camera_manager.start_camera():
            # Если камера успешно запущена, меняем состояние кнопок
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            # Логируем успешный запуск камеры
            audit = self.get_audit_logger() if self.get_audit_logger else None
            if audit:
                audit.log_system_event("camera_start", "success")
            
            # Начинаем обработку кадров
            self.process_frame()
        else:
            # Если не удалось запустить камеру, логируем ошибку
            audit = self.get_audit_logger() if self.get_audit_logger else None
            if audit:
                audit.log_system_event("camera_start", "failed")
            
            # Показываем сообщение об ошибке
            messagebox.showerror("Ошибка", "Не удалось подключиться к камере!")
    
    def stop_camera(self):
        """Остановка камеры"""
        # Останавливаем камеру
        self.camera_manager.stop_camera()
        
        # Очищаем все таймеры
        if self.last_recognition_timer:
            self.frame.after_cancel(self.last_recognition_timer)
            self.last_recognition_timer = None
        
        # Сбрасываем временные метки
        self.last_recognition_time = None
        self.last_unknown_time = None
        
        # Возвращаем кнопки в исходное состояние
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        # Очищаем видео и информацию о пользователе
        self.video_label.config(image="", text="Камера остановлена")
        self.reset_user_info()
        
        # Логируем остановку камеры
        audit = self.get_audit_logger() if self.get_audit_logger else None
        if audit:
            audit.log_system_event("camera_stop", "success")
    
    def process_frame(self):
        """Обработка кадров с камеры"""
        # Проверяем, что камера все еще работает
        if not self.camera_manager.is_camera_running():
            return
        
        # Получаем кадр с камеры
        frame = self.camera_manager.get_frame()
        if frame is None:
            # Если кадр не получен, планируем следующую попытку через 30мс
            self.frame.after(30, self.process_frame)
            return
        
        # Выполняем распознавание лиц на кадре
        recognized_faces = self.face_engine.recognize_faces(frame, FRAME_SCALE)
        
        # Получаем текущее время для проверки задержек
        current_time = datetime.datetime.now()
        recognized_user = None
        
        # Проверяем возможность распознавания с учетом задержек
        can_recognize_known = self._can_recognize_known(current_time)
        can_recognize_unknown = self._can_recognize_unknown(current_time)
        
        # Обрабатываем каждое найденное лицо
        for face_info in recognized_faces:
            # Получаем имя для отображения и цвет рамки
            name, color = self._process_face(face_info, current_time, 
                                           can_recognize_known, can_recognize_unknown)
            
            # Рисуем рамку вокруг лица
            self.face_engine.draw_face_rectangle(frame, face_info, color, name)
            
            # Если распознали известного пользователя, сохраняем данные для отображения
            if face_info['is_known'] and can_recognize_known:
                user_data = self.db.get_user(face_info['user_id'])
                if user_data:
                    recognized_user = user_data
                    self.last_recognition_time = current_time
                    self._schedule_info_clear()
        
        # Обновляем информацию о пользователе
        if recognized_user:
            self.update_user_info(recognized_user)
        elif not recognized_faces and not self.last_recognition_timer:
            # Если лиц не найдено и нет активного таймера, сбрасываем информацию
            self.reset_user_info()
        
        # Отображаем кадр в интерфейсе
        self._display_frame(frame)
        
        # Планируем обработку следующего кадра через 30мс
        self.frame.after(30, self.process_frame)
    
    def _can_recognize_known(self, current_time):
        """Проверка возможности распознавания известного лица"""
        # Если это первое распознавание, разрешаем
        if not self.last_recognition_time:
            return True
        
        # Проверяем, прошло ли достаточно времени с последнего распознавания
        elapsed = (current_time - self.last_recognition_time).total_seconds()
        return elapsed >= RECOGNITION_DELAY
    
    def _can_recognize_unknown(self, current_time):
        """Проверка возможности распознавания неизвестного лица"""
        # Если это первое неизвестное лицо, разрешаем
        if not self.last_unknown_time:
            return True
        
        # Проверяем, прошло ли достаточно времени с последнего неизвестного лица
        elapsed = (current_time - self.last_unknown_time).total_seconds()
        return elapsed >= UNKNOWN_FACE_DELAY
    
    def _process_face(self, face_info, current_time, can_recognize_known, can_recognize_unknown):
        """Обработка информации о лице"""
        # Получаем логгер аудита
        audit = self.get_audit_logger() if self.get_audit_logger else None
        
        if face_info['is_known']:
            # Обработка известного пользователя
            if can_recognize_known:
                # Логируем успешное распознавание с distance (вместо confidence)
                if audit:
                    audit.log_recognition(face_info['user_id'], True, face_info['distance'])
                
                # Получаем имя пользователя для отображения
                user_data = self.db.get_user(face_info['user_id'])
                name = user_data[2] if user_data else "Неизвестно"
                color = (0, 255, 0)  # Зеленая рамка для известного пользователя
            else:
                # Ожидание для известного пользователя (показываем оставшееся время)
                time_left = RECOGNITION_DELAY - (current_time - self.last_recognition_time).total_seconds()
                name = f"{time_left:.1f}s"
                color = (0, 255, 255)  # Желтая рамка во время ожидания
        else:
            # Обработка неизвестного лица
            if can_recognize_unknown:
                # Логируем неудачное распознавание с distance (вместо confidence)
                if audit:
                    audit.log_recognition(None, False, face_info['distance'])
                
                # Обновляем время последнего неизвестного лица
                self.last_unknown_time = current_time
                name = ""  # Не показываем имя для неизвестного лица
                color = (0, 0, 255)  # Красная рамка для неизвестного лица
            else:
                # Ожидание для неизвестного лица (показываем оставшееся время)
                time_left = UNKNOWN_FACE_DELAY - (current_time - self.last_unknown_time).total_seconds()
                name = f"{time_left:.1f}s"
                color = (0, 255, 255)  # Желтая рамка во время ожидания
        
        return name, color
    
    def _schedule_info_clear(self):
        """Планирование очистки информации о пользователе"""
        # Отменяем предыдущий таймер, если он был
        if self.last_recognition_timer:
            self.frame.after_cancel(self.last_recognition_timer)
        
        # Планируем очистку информации через заданное время
        self.last_recognition_timer = self.frame.after(
            INFO_DISPLAY_DURATION * 1000, 
            self.reset_user_info
        )
    
    def _display_frame(self, frame):
        """Отображение кадра в интерфейсе"""
        # Конвертируем кадр из BGR в RGB для отображения
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        photo = ImageTk.PhotoImage(pil_image)
        
        # Обновляем изображение в лейбле
        self.video_label.config(image=photo, text="")
        self.video_label.image = photo  # Сохраняем ссылку на изображение
    
    def update_user_info(self, user_data):
        """Обновление информации о распознанном пользователе"""
        # Извлекаем данные пользователя
        user_id = user_data[1]
        name = user_data[2]
        photo_path = user_data[3]
        
        # Обновляем статус с текущим временем
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        self.status_label.config(text=f"✅ Распознан в {current_time}", fg="#10B981")
        self.user_id_label.config(text=user_id)
        self.name_label.config(text=name)
        
        # Загружаем и отображаем фотографию пользователя
        if photo_path and os.path.exists(photo_path):
            try:
                # Открываем и изменяем размер фотографии
                pil_image = Image.open(photo_path)
                pil_image = pil_image.resize((170, 170), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(pil_image)
                
                # Отображаем фотографию
                self.photo_display.config(image=photo, text="")
                self.photo_display.image = photo  # Сохраняем ссылку на изображение
                
            except Exception as e:
                print(f"Ошибка загрузки фото: {e}")
                self.photo_display.config(image="", text="Ошибка\nзагрузки", 
                                        font=("Arial", 9), fg="#EF4444")
        else:
            # Если фото не найдено
            self.photo_display.config(image="", text="Фото\nне найдено", 
                                    font=("Arial", 9), fg="#6B7280")
    
    def reset_user_info(self):
        """Сброс информации о пользователе"""
        # Возвращаем все поля в исходное состояние
        self.status_label.config(text="⏳ Ожидание...", fg="#6B7280")
        self.user_id_label.config(text="—")
        self.name_label.config(text="—")
        self.photo_display.config(image="", text="Нет фото", 
                                 font=("Arial", 10), fg="#6B7280")
        
        # Сбрасываем таймер
        if self.last_recognition_timer:
            self.last_recognition_timer = None
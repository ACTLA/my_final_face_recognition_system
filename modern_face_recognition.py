import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import face_recognition
import os
import shutil
import numpy as np
from PIL import Image, ImageTk
from database import DatabaseManager
import datetime

class ModernFaceRecognitionApp:
    def __init__(self, root):
        # Инициализация главного окна
        self.root = root
        self.root.title("Система распознавания лиц")
        self.root.geometry("1200x800")
        self.root.configure(bg="#6B46C1")  # Фиолетовый фон как на скриншоте
        
        # Инициализация базы данных
        self.db = DatabaseManager()
        
        # Переменные для работы с камерой
        self.cap = None
        self.is_running = False
        
        # Переменные для распознавания
        self.known_encodings = []
        self.known_user_ids = []
        
        # Переменные для добавления пользователя
        self.photo_path = ""
        
        # 🆕 Переменная для системы аудита (будет установлена при интеграции)
        self.audit = None
        
        # 🆕 Переменные для контроля задержек распознавания
        self.last_recognition_time = None
        self.last_unknown_time = None  # 🆕 Время последнего неизвестного лица
        self.last_recognition_timer = None
        self.recognition_delay = 3  # Задержка между успешными распознаваниями (секунды)
        self.unknown_face_delay = 5  # 🆕 Задержка для неизвестных лиц (секунды)
        self.info_display_duration = 2  # Время показа информации (секунды)
        
        # Создание папки для фотографий если её нет
        if not os.path.exists("photos"):
            os.makedirs("photos")
        
        # Загрузка кодировок лиц
        self.load_encodings()
        
        self.setup_modern_ui()
    
    def setup_modern_ui(self):
        # Создание современного интерфейса
        
        # Заголовок
        header_frame = tk.Frame(self.root, bg="#6B46C1", height=80)
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        header_frame.pack_propagate(False)
        
        # Иконка и название (как на скриншоте)
        title_frame = tk.Frame(header_frame, bg="#6B46C1")
        title_frame.pack(side="left", fill="y")
        
        # Иконка (можно заменить на реальную)
        icon_label = tk.Label(title_frame, text="👤", font=("Arial", 24), bg="#6B46C1", fg="white")
        icon_label.pack(side="left", padx=(0, 10))
        
        title_label = tk.Label(title_frame, text="СИСТЕМА РАСПОЗНАВАНИЯ ЛИЦ", 
                              font=("Arial", 18, "bold"), bg="#6B46C1", fg="white")
        title_label.pack(side="left")
        
        # Создание вкладок
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настройка стиля вкладок
        style.configure('Custom.TNotebook.Tab', 
                       padding=[20, 10], 
                       font=('Arial', 12, 'bold'))
        
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Вкладка распознавания
        self.recognition_frame = tk.Frame(self.notebook, bg="#6B46C1")
        self.notebook.add(self.recognition_frame, text="  🎥 Распознавание лиц  ")
        
        # Вкладка управления пользователями
        self.management_frame = tk.Frame(self.notebook, bg="#6B46C1")
        self.notebook.add(self.management_frame, text="  👥 Управление пользователями  ")
        
        # Настройка вкладки распознавания
        self.setup_recognition_tab()
        
        # Настройка вкладки управления
        self.setup_management_tab()
    
    def setup_recognition_tab(self):
        # Настройка вкладки распознавания лиц
        
        # Основной контейнер для распознавания
        main_container = tk.Frame(self.recognition_frame, bg="#6B46C1")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Левая панель - Видео (делаем меньше)
        left_panel = tk.Frame(main_container, bg="white", relief="raised", bd=2, width=500)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Заголовок видео панели
        video_header = tk.Frame(left_panel, bg="#7C3AED", height=40)
        video_header.pack(fill="x")
        video_header.pack_propagate(False)
        
        video_title = tk.Label(video_header, text="КАМЕРА", 
                              font=("Arial", 12, "bold"), bg="#7C3AED", fg="white")
        video_title.pack(expand=True)
        
        # Видео контейнер (фиксированный размер)
        video_container = tk.Frame(left_panel, bg="black", width=480, height=360)
        video_container.pack(padx=10, pady=10)
        video_container.pack_propagate(False)
        
        # Метка для отображения видео
        self.video_label = tk.Label(video_container, text="Камера не запущена", 
                                   bg="black", fg="white", font=("Arial", 12))
        self.video_label.pack(fill="both", expand=True)
        
        # Кнопки управления камерой (компактные)
        camera_controls = tk.Frame(left_panel, bg="white", height=50)
        camera_controls.pack(fill="x", padx=10, pady=(0, 10))
        camera_controls.pack_propagate(False)
        
        self.start_button = tk.Button(camera_controls, text="▶ Запуск", 
                                     font=("Arial", 10, "bold"), bg="#10B981", fg="white",
                                     relief="flat", padx=15, pady=6, command=self.start_camera)
        self.start_button.pack(side="left", padx=(0, 5))
        
        self.stop_button = tk.Button(camera_controls, text="⏹ Стоп", 
                                    font=("Arial", 10, "bold"), bg="#EF4444", fg="white",
                                    relief="flat", padx=15, pady=6, command=self.stop_camera,
                                    state="disabled")
        self.stop_button.pack(side="left", padx=(0, 5))
        
        # Правая панель - Информация о распознанном пользователе (шире)
        right_panel = tk.Frame(main_container, bg="white", relief="raised", bd=2)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # === СЕКЦИЯ РАСПОЗНАВАНИЯ ===
        recognition_info = tk.Frame(right_panel, bg="white")
        recognition_info.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Заголовок секции распознавания
        rec_header = tk.Label(recognition_info, text="РАСПОЗНАННЫЙ ПОЛЬЗОВАТЕЛЬ", 
                             font=("Arial", 14, "bold"), bg="white", fg="#374151")
        rec_header.pack(anchor="w", pady=(0, 15))
        
        # Статус распознавания
        self.status_label = tk.Label(recognition_info, text="Ожидание...", 
                                    font=("Arial", 16, "bold"), bg="white", fg="#6B7280")
        self.status_label.pack(anchor="w", pady=(0, 15))
        
        # Информация о пользователе в компактном виде
        info_container = tk.Frame(recognition_info, bg="#F9FAFB", relief="solid", bd=1)
        info_container.pack(fill="x", pady=(0, 15))
        
        # ID пользователя
        id_frame = tk.Frame(info_container, bg="#F9FAFB")
        id_frame.pack(fill="x", padx=10, pady=8)
        
        tk.Label(id_frame, text="ID:", font=("Arial", 11, "bold"), bg="#F9FAFB", fg="#374151").pack(side="left")
        self.user_id_label = tk.Label(id_frame, text="—", font=("Arial", 11), bg="#F9FAFB", fg="#6B7280")
        self.user_id_label.pack(side="right")
        
        # Имя пользователя
        name_frame = tk.Frame(info_container, bg="#F9FAFB")
        name_frame.pack(fill="x", padx=10, pady=8)
        
        tk.Label(name_frame, text="Имя:", font=("Arial", 11, "bold"), bg="#F9FAFB", fg="#374151").pack(side="left")
        self.name_label = tk.Label(name_frame, text="—", font=("Arial", 11), bg="#F9FAFB", fg="#6B7280")
        self.name_label.pack(side="right")
        
        # Фотография пользователя (компактнее)
        photo_frame = tk.Frame(recognition_info, bg="white")
        photo_frame.pack(fill="x")
        
        tk.Label(photo_frame, text="Фотография:", font=("Arial", 11, "bold"), 
                bg="white", fg="#374151").pack(anchor="w", pady=(0, 8))
        
        # Контейнер для фото с фиксированными размерами
        photo_container = tk.Frame(photo_frame, bg="#F3F4F6", relief="solid", bd=1, width=180, height=180)
        photo_container.pack(pady=(0, 10))
        photo_container.pack_propagate(False)
        
        self.photo_display = tk.Label(photo_container, text="Нет фото", bg="#F3F4F6", 
                                     font=("Arial", 10), fg="#6B7280")
        self.photo_display.pack(fill="both", expand=True)
    
    def setup_management_tab(self):
        # Настройка вкладки управления пользователями
        
        # Основной контейнер для управления
        main_container = tk.Frame(self.management_frame, bg="#6B46C1")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Настраиваем grid для равного разделения
        main_container.grid_columnconfigure(0, weight=1)  # Левая колонка
        main_container.grid_columnconfigure(1, weight=1)  # Правая колонка
        main_container.grid_rowconfigure(0, weight=1)
        
        # Левая панель - Добавление пользователя
        left_panel = tk.Frame(main_container, bg="white", relief="raised", bd=2)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Заголовок левой панели
        add_header_frame = tk.Frame(left_panel, bg="#7C3AED", height=40)
        add_header_frame.pack(fill="x")
        add_header_frame.pack_propagate(False)
        
        add_title = tk.Label(add_header_frame, text="ДОБАВИТЬ ПОЛЬЗОВАТЕЛЯ", 
                            font=("Arial", 12, "bold"), bg="#7C3AED", fg="white")
        add_title.pack(expand=True)
        
        # Контент добавления пользователя (компактный)
        add_content = tk.Frame(left_panel, bg="white")
        add_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Поле ID пользователя (компактное)
        id_input_frame = tk.Frame(add_content, bg="white")
        id_input_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(id_input_frame, text="ID пользователя:", font=("Arial", 10, "bold"), 
                bg="white", fg="#374151").pack(anchor="w")
        self.user_id_entry = tk.Entry(id_input_frame, font=("Arial", 10), relief="solid", bd=1)
        self.user_id_entry.pack(fill="x", pady=(3, 0), ipady=3)
        
        # Поле имени пользователя (компактное)
        name_input_frame = tk.Frame(add_content, bg="white")
        name_input_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(name_input_frame, text="Имя пользователя:", font=("Arial", 10, "bold"), 
                bg="white", fg="#374151").pack(anchor="w")
        self.name_entry = tk.Entry(name_input_frame, font=("Arial", 10), relief="solid", bd=1)
        self.name_entry.pack(fill="x", pady=(3, 0), ipady=3)
        
        # Выбор фотографии (компактное)
        photo_input_frame = tk.Frame(add_content, bg="white")
        photo_input_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(photo_input_frame, text="Фотография:", font=("Arial", 10, "bold"), 
                bg="white", fg="#374151").pack(anchor="w", pady=(0, 5))
        
        # Превью фотографии (меньший размер для компактности)
        preview_container = tk.Frame(photo_input_frame, bg="#F3F4F6", relief="solid", bd=1, width=120, height=120)
        preview_container.pack(pady=(0, 6))
        preview_container.pack_propagate(False)
        
        self.photo_preview = tk.Label(preview_container, text="Превью", bg="#F3F4F6", 
                                     font=("Arial", 8), fg="#6B7280")
        self.photo_preview.pack(fill="both", expand=True)
        
        # Кнопка выбора фото
        select_photo_btn = tk.Button(photo_input_frame, text="📁 Выбрать фото", 
                                    font=("Arial", 9, "bold"), bg="#6366F1", fg="white",
                                    relief="flat", padx=10, pady=5, command=self.select_photo)
        select_photo_btn.pack(fill="x")
        
        # Статус выбранного фото
        self.photo_status_label = tk.Label(photo_input_frame, text="Фото не выбрано", 
                                          font=("Arial", 8), bg="white", fg="#6B7280")
        self.photo_status_label.pack(pady=(5, 0))
        
        # Кнопки действий (только добавление)
        actions_frame = tk.Frame(add_content, bg="white")
        actions_frame.pack(fill="x", pady=(10, 0))
        
        # Основная кнопка добавления
        add_btn = tk.Button(actions_frame, text="➕ Добавить пользователя", 
                           font=("Arial", 10, "bold"), bg="#10B981", fg="white",
                           relief="flat", padx=15, pady=8, command=self.add_user)
        add_btn.pack(fill="x")
        
        # Правая панель - Список пользователей
        right_panel = tk.Frame(main_container, bg="white", relief="raised", bd=2)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Заголовок правой панели
        list_header_frame = tk.Frame(right_panel, bg="#7C3AED", height=40)
        list_header_frame.pack(fill="x")
        list_header_frame.pack_propagate(False)
        
        list_title = tk.Label(list_header_frame, text="СПИСОК ПОЛЬЗОВАТЕЛЕЙ", 
                             font=("Arial", 12, "bold"), bg="#7C3AED", fg="white")
        list_title.pack(expand=True)
        
        # Контент списка пользователей (компактный)
        list_content = tk.Frame(right_panel, bg="white")
        list_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Таблица пользователей (компактная)
        columns = ("ID", "Имя", "Фото")
        self.users_tree = ttk.Treeview(list_content, columns=columns, show="headings", height=12)
        
        # Настройка колонок (компактные)
        self.users_tree.heading("ID", text="ID")
        self.users_tree.heading("Имя", text="Имя")
        self.users_tree.heading("Фото", text="Фото")
        
        self.users_tree.column("ID", width=80)
        self.users_tree.column("Имя", width=120)
        self.users_tree.column("Фото", width=100)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(list_content, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение таблицы
        self.users_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления списком (компактные, в одну строку)
        list_controls = tk.Frame(right_panel, bg="white", height=40)
        list_controls.pack(fill="x", padx=10, pady=(0, 10))
        list_controls.pack_propagate(False)
        
        # Кнопка обновления фото (первая)
        update_photo_btn = tk.Button(list_controls, text="🔄 Обновить фото", 
                                    font=("Arial", 9, "bold"), bg="#F59E0B", fg="white",
                                    relief="flat", padx=8, pady=6, command=self.update_user_photo)
        update_photo_btn.pack(side="left", padx=(0, 3))
        
        # Кнопка удаления (вторая)
        delete_btn = tk.Button(list_controls, text="🗑 Удалить", 
                              font=("Arial", 9, "bold"), bg="#EF4444", fg="white",
                              relief="flat", padx=8, pady=6, command=self.delete_user)
        delete_btn.pack(side="left", padx=(0, 3))
        
        # Кнопка обновления списка (третья)
        refresh_list_btn = tk.Button(list_controls, text="🔄 Обновить список", 
                                    font=("Arial", 9, "bold"), bg="#6366F1", fg="white",
                                    relief="flat", padx=8, pady=6, command=self.refresh_user_list)
        refresh_list_btn.pack(side="left")
        
        # Загружаем список пользователей
        self.refresh_user_list()
    
    def load_encodings(self):
        # 🆕 Загрузка кодировок лиц из базы данных С ЛОГИРОВАНИЕМ
        try:
            self.known_encodings, self.known_user_ids = self.db.get_all_encodings()
            print(f"Загружено кодировок из БД: {len(self.known_encodings)}")
            
            # 📊 ЛОГИРУЕМ УСПЕШНУЮ ЗАГРУЗКУ КОДИРОВОК
            if self.audit:
                self.audit.log_system_event("encodings_loaded", "success")
            
            if not self.known_encodings:
                print("Кодировки не найдены. Добавьте пользователей.")
                
        except Exception as e:
            print(f"Ошибка загрузки кодировок: {e}")
            
            # 📊 ЛОГИРУЕМ ОШИБКУ ЗАГРУЗКИ КОДИРОВОК
            if self.audit:
                self.audit.log_system_event("encodings_loaded", "failed")
            
            self.known_encodings = []
            self.known_user_ids = []
    
    def start_camera(self):
        # 🆕 Запуск камеры С ЛОГИРОВАНИЕМ
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                # 📊 ЛОГИРУЕМ ОШИБКУ ЗАПУСКА КАМЕРЫ
                if self.audit:
                    self.audit.log_system_event("camera_start", "failed")
                messagebox.showerror("Ошибка", "Не удалось подключиться к камере!")
                return
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            self.is_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            # 📊 ЛОГИРУЕМ УСПЕШНЫЙ ЗАПУСК КАМЕРЫ
            if self.audit:
                self.audit.log_system_event("camera_start", "success")
            
            self.process_frame()
            
        except Exception as e:
            # 📊 ЛОГИРУЕМ ОШИБКУ ЗАПУСКА КАМЕРЫ
            if self.audit:
                self.audit.log_system_event("camera_start", "failed")
            messagebox.showerror("Ошибка", f"Ошибка запуска камеры: {str(e)}")
    
    def stop_camera(self):
        # 🆕 Остановка камеры с очисткой всех таймеров
        self.is_running = False
        if self.cap:
            self.cap.release()
        
        # 🆕 Очищаем все таймеры и времена при остановке камеры
        if self.last_recognition_timer:
            self.root.after_cancel(self.last_recognition_timer)
            self.last_recognition_timer = None
        
        self.last_recognition_time = None
        self.last_unknown_time = None  # 🆕 Очищаем время неизвестных лиц
        
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        self.video_label.config(image="", text="Камера остановлена")
        self.reset_user_info()
        
        # 📊 ЛОГИРУЕМ ОСТАНОВКУ КАМЕРЫ
        if self.audit:
            self.audit.log_system_event("camera_stop", "success")
    
    def process_frame(self):
        """🆕 Обработка каждого кадра с камеры С РАЗНЫМИ ЗАДЕРЖКАМИ"""
        if not self.is_running or not self.cap:
            return
        
        ret, frame = self.cap.read()
        if not ret:
            print("Не удалось получить кадр с камеры")
            self.root.after(30, self.process_frame)
            return
        
        # Уменьшаем размер кадра для ускорения распознавания
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Поиск лиц на кадре
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        recognized_user = None
        current_time = datetime.datetime.now()
        
        # 🆕 ПРОВЕРЯЕМ ЗАДЕРЖКИ ДЛЯ РАЗНЫХ ТИПОВ РАСПОЗНАВАНИЯ
        can_recognize_known = True
        can_recognize_unknown = True
        
        # Задержка для успешных распознаваний (3 секунды)
        if (self.last_recognition_time and 
            (current_time - self.last_recognition_time).total_seconds() < self.recognition_delay):
            can_recognize_known = False
        
        # 🆕 Задержка для неизвестных лиц (5 секунд)
        if (self.last_unknown_time and 
            (current_time - self.last_unknown_time).total_seconds() < self.unknown_face_delay):
            can_recognize_unknown = False
        
        # Обработка найденных лиц
        for face_encoding, face_location in zip(face_encodings, face_locations):
            name = "Обработка..."  # По умолчанию
            
            if self.known_encodings:
                matches = face_recognition.compare_faces(self.known_encodings, face_encoding)
                face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
                
                best_match_index = np.argmin(face_distances)
                confidence = 1 - face_distances[best_match_index]
                
                if matches[best_match_index]:
                    # 🆕 ИЗВЕСТНЫЙ ПОЛЬЗОВАТЕЛЬ - проверяем задержку 3 сек
                    if can_recognize_known:
                        user_id = self.known_user_ids[best_match_index]
                        user_data = self.db.get_user(user_id)
                        if user_data:
                            recognized_user = user_data
                            name = user_data[2]
                            
                            # 📊 ЛОГИРУЕМ УСПЕШНОЕ РАСПОЗНАВАНИЕ
                            if self.audit:
                                self.audit.log_recognition(user_id, True, confidence)
                            
                            # 🆕 ОБНОВЛЯЕМ ВРЕМЯ ПОСЛЕДНЕГО УСПЕШНОГО РАСПОЗНАВАНИЯ
                            self.last_recognition_time = current_time
                            
                            # 🆕 ЗАПУСКАЕМ ТАЙМЕР ОЧИСТКИ ЧЕРЕЗ 2 СЕКУНДЫ
                            if self.last_recognition_timer:
                                self.root.after_cancel(self.last_recognition_timer)
                            self.last_recognition_timer = self.root.after(
                                self.info_display_duration * 1000, 
                                self.reset_user_info
                            )
                        else:
                            name = "Ошибка БД"
                            if self.audit:
                                self.audit.log_recognition(None, False, confidence)
                    else:
                        # 🆕 Показываем ожидание для известного пользователя
                        time_left = self.recognition_delay - (current_time - self.last_recognition_time).total_seconds()
                        name = f"Ожидание {time_left:.1f}с"
                else:
                    # 🆕 НЕИЗВЕСТНЫЙ ПОЛЬЗОВАТЕЛЬ - проверяем задержку 5 сек
                    if can_recognize_unknown:
                        name = "Неизвестный"
                        
                        # 📊 ЛОГИРУЕМ НЕУДАЧНОЕ РАСПОЗНАВАНИЕ
                        if self.audit:
                            self.audit.log_recognition(None, False, confidence)
                        
                        # 🆕 ОБНОВЛЯЕМ ВРЕМЯ ПОСЛЕДНЕГО НЕИЗВЕСТНОГО ЛИЦА
                        self.last_unknown_time = current_time
                    else:
                        # 🆕 Показываем ожидание для неизвестного лица
                        time_left = self.unknown_face_delay - (current_time - self.last_unknown_time).total_seconds()
                        name = f"Блокировка {time_left:.1f}с"
            else:
                name = "Нет кодировок"
            
            # Рисуем рамку вокруг лица
            top, right, bottom, left = face_location
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # 🆕 Цвет рамки зависит от состояния
            if recognized_user:
                color = (0, 255, 0)  # Зеленый - распознан
            elif not can_recognize_known and "Ожидание" in name:
                color = (255, 165, 0)  # Оранжевый - ожидание известного
            elif not can_recognize_unknown and "Блокировка" in name:
                color = (255, 0, 255)  # Фиолетовый - блокировка неизвестного
            elif "Неизвестный" in name:
                color = (0, 0, 255)  # Красный - неизвестный
            else:
                color = (128, 128, 128)  # Серый - обработка
            
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        # 🆕 ОБНОВЛЯЕМ ИНФОРМАЦИЮ О ПОЛЬЗОВАТЕЛЕ ТОЛЬКО ПРИ НОВОМ РАСПОЗНАВАНИИ
        if recognized_user:
            self.update_user_info(recognized_user)
        elif not face_locations:
            # Сбрасываем информацию только если нет лиц И нет активного таймера
            if not self.last_recognition_timer:
                self.reset_user_info()
        
        # Конвертируем кадр для отображения в Tkinter
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        photo = ImageTk.PhotoImage(pil_image)
        
        self.video_label.config(image=photo, text="")
        self.video_label.image = photo
        
        self.root.after(30, self.process_frame)
    
    def update_user_info(self, user_data):
        """🆕 Обновление информации о распознанном пользователе С ВРЕМЕННОЙ МЕТКОЙ"""
        user_id = user_data[1]
        name = user_data[2]
        photo_path = user_data[3]
        
        # 🆕 Показываем статус с временной меткой
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        self.status_label.config(text=f"✅ Распознан в {current_time}", fg="#10B981")
        self.user_id_label.config(text=user_id)
        self.name_label.config(text=name)
        
        # Загружаем и отображаем фотографию с правильным размером
        if photo_path and os.path.exists(photo_path):
            try:
                # Открываем изображение
                pil_image = Image.open(photo_path)
                
                # Изменяем размер под контейнер (170x170 с отступами)
                pil_image = pil_image.resize((170, 170), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(pil_image)
                
                # Отображаем фото
                self.photo_display.config(image=photo, text="")
                self.photo_display.image = photo  # Сохраняем ссылку
                
            except Exception as e:
                print(f"Ошибка загрузки фото: {e}")
                self.photo_display.config(image="", text="Ошибка\nзагрузки", 
                                        font=("Arial", 9), fg="#EF4444")
        else:
            self.photo_display.config(image="", text="Фото\nне найдено", 
                                    font=("Arial", 9), fg="#6B7280")
    
    def reset_user_info(self):
        """🆕 Сброс информации о пользователе С ОЧИСТКОЙ ТАЙМЕРА"""
        self.status_label.config(text="⏳ Ожидание...", fg="#6B7280")
        self.user_id_label.config(text="—")
        self.name_label.config(text="—")
        self.photo_display.config(image="", text="Нет фото", font=("Arial", 10), fg="#6B7280")
        
        # 🆕 Очищаем таймер
        if self.last_recognition_timer:
            self.last_recognition_timer = None
    
    def select_photo(self):
        # Выбор фотографии пользователя
        file_path = filedialog.askopenfilename(
            title="Выберите фотографию",
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            self.photo_path = file_path
            filename = os.path.basename(file_path)
            self.photo_status_label.config(text=f"✓ {filename}", fg="#10B981")
            
            # Показываем превью фотографии с правильным масштабированием
            try:
                pil_image = Image.open(file_path)
                # Изменяем размер для превью (110x110 с отступами в контейнере 120x120)
                pil_image = pil_image.resize((110, 110), Image.Resampling.LANCZOS)
                photo_preview = ImageTk.PhotoImage(pil_image)
                
                # Отображаем превью
                self.photo_preview.config(image=photo_preview, text="")
                self.photo_preview.image = photo_preview  # Сохраняем ссылку
                
            except Exception as e:
                print(f"Ошибка загрузки превью: {e}")
                self.photo_preview.config(image="", text="Ошибка", 
                                        font=("Arial", 8), fg="#EF4444")
    
    def add_user(self):
        # 🆕 Добавление нового пользователя С ЛОГИРОВАНИЕМ
        user_id = self.user_id_entry.get().strip()
        name = self.name_entry.get().strip()
        
        if not user_id or not name:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        
        if not self.photo_path:
            messagebox.showerror("Ошибка", "Выберите фотографию!")
            return
        
        photo_filename = f"{user_id}.jpg"
        photo_destination = os.path.join("photos", photo_filename)
        
        try:
            shutil.copy2(self.photo_path, photo_destination)
            face_encoding = self.create_face_encoding(photo_destination)
            
            if self.db.add_user(user_id, name, photo_destination, face_encoding):
                # 📊 ЛОГИРУЕМ УСПЕШНОЕ ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ
                if self.audit:
                    self.audit.log_user_action("added", user_id, True)
                
                messagebox.showinfo("Успех", "✅ Пользователь добавлен!")
                
                # Очищаем поля
                self.user_id_entry.delete(0, tk.END)
                self.name_entry.delete(0, tk.END)
                self.photo_path = ""
                self.photo_status_label.config(text="Фото не выбрано", fg="#6B7280")
                
                # Очищаем превью
                self.photo_preview.config(image="", text="Превью", font=("Arial", 8), fg="#6B7280")
                
                # Обновляем данные
                self.refresh_user_list()
                self.load_encodings()
            else:
                # 📊 ЛОГИРУЕМ НЕУДАЧНОЕ ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ
                if self.audit:
                    self.audit.log_user_action("added", user_id, False)
                
                messagebox.showerror("Ошибка", "Пользователь с таким ID уже существует!")
                if os.path.exists(photo_destination):
                    os.remove(photo_destination)
                    
        except Exception as e:
            # 📊 ЛОГИРУЕМ ОШИБКУ ДОБАВЛЕНИЯ ПОЛЬЗОВАТЕЛЯ
            if self.audit:
                self.audit.log_user_action("added", user_id, False)
                self.audit.log_system_event("system_error", "failed")
            messagebox.showerror("Ошибка", f"Не удалось добавить пользователя: {str(e)}")
    
    def create_face_encoding(self, photo_path):
        # Создание кодировки лица из фотографии
        try:
            image = cv2.imread(photo_path)
            if image is None:
                raise Exception("Не удалось загрузить изображение")
            
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_encodings = face_recognition.face_encodings(rgb_image)
            
            if face_encodings:
                print(f"Кодировка создана для {os.path.basename(photo_path)}")
                return face_encodings[0]
            else:
                raise Exception("Лицо не найдено на фотографии. Убедитесь что на фото четко видно лицо.")
                
        except Exception as e:
            raise Exception(f"Ошибка создания кодировки: {str(e)}")
    
    def update_user_photo(self):
        # 🆕 Обновление фотографии существующего пользователя С ЛОГИРОВАНИЕМ
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для обновления фото!")
            return
        
        if not self.photo_path:
            messagebox.showerror("Ошибка", "Сначала выберите новую фотографию!")
            return
        
        # Получаем данные выбранного пользователя
        user_data = self.users_tree.item(selected_item)
        user_id = user_data['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Обновить фото для пользователя {user_id}?"):
            try:
                # Копируем новое фото
                photo_filename = f"{user_id}.jpg"
                photo_destination = os.path.join("photos", photo_filename)
                
                # Удаляем старое фото если существует
                if os.path.exists(photo_destination):
                    os.remove(photo_destination)
                
                # Копируем новое фото
                shutil.copy2(self.photo_path, photo_destination)
                
                # Создаем новую кодировку
                face_encoding = self.create_face_encoding(photo_destination)
                
                # Обновляем в БД
                if self.db.update_user_encoding(user_id, face_encoding):
                    # 📊 ЛОГИРУЕМ УСПЕШНОЕ ОБНОВЛЕНИЕ ФОТО
                    if self.audit:
                        self.audit.log_user_action("photo_updated", user_id, True)
                    
                    messagebox.showinfo("Успех", "✅ Фото пользователя обновлено!")
                    
                    # Очищаем выбранное фото
                    self.photo_path = ""
                    self.photo_status_label.config(text="Фото не выбрано", fg="#6B7280")
                    self.photo_preview.config(image="", text="Превью", font=("Arial", 8), fg="#6B7280")
                    
                    # Обновляем данные
                    self.refresh_user_list()
                    self.load_encodings()
                else:
                    # 📊 ЛОГИРУЕМ НЕУДАЧНОЕ ОБНОВЛЕНИЕ ФОТО
                    if self.audit:
                        self.audit.log_user_action("photo_updated", user_id, False)
                    messagebox.showerror("Ошибка", "Не удалось обновить фото в БД!")
                    
            except Exception as e:
                # 📊 ЛОГИРУЕМ ОШИБКУ ОБНОВЛЕНИЯ ФОТО
                if self.audit:
                    self.audit.log_user_action("photo_updated", user_id, False)
                    self.audit.log_system_event("system_error", "failed")
                messagebox.showerror("Ошибка", f"Не удалось обновить фото: {str(e)}")
    
    def delete_user(self):
        # 🆕 Удаление выбранного пользователя С ЛОГИРОВАНИЕМ
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления!")
            return
        
        user_data = self.users_tree.item(selected_item)
        user_id = user_data['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить пользователя {user_id}?"):
            if self.db.delete_user(user_id):
                # 📊 ЛОГИРУЕМ УСПЕШНОЕ УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ
                if self.audit:
                    self.audit.log_user_action("deleted", user_id, True)
                
                messagebox.showinfo("Успех", "✅ Пользователь удален!")
                self.refresh_user_list()
                self.load_encodings()
            else:
                # 📊 ЛОГИРУЕМ НЕУДАЧНОЕ УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ
                if self.audit:
                    self.audit.log_user_action("deleted", user_id, False)
                messagebox.showerror("Ошибка", "Не удалось удалить пользователя!")
    
    def refresh_user_list(self):
        # Обновление списка пользователей
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        users = self.db.get_all_users()
        for user in users:
            photo_name = os.path.basename(user[3]) if user[3] else "Нет"
            self.users_tree.insert("", "end", values=(user[1], user[2], photo_name))
    
    def on_closing(self):
        # 🆕 Обработка закрытия окна с очисткой всех таймеров
        self.stop_camera()
        
        # Очистка всех таймеров при закрытии
        if self.last_recognition_timer:
            self.root.after_cancel(self.last_recognition_timer)
        
        # 🆕 Очищаем все переменные времени
        self.last_recognition_time = None
        self.last_unknown_time = None
        
        self.root.destroy()

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = ModernFaceRecognitionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
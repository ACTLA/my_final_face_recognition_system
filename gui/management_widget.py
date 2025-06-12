# gui/management_widget.py
"""
Модуль виджета управления пользователями системы
Автор: Студент 4 курса ОмГУ им. Ф.М. Достоевского
ВКР: Автоматизированная система распознавания лиц

Описание:
Виджет управления пользователями обеспечивает полный жизненный цикл
управления зарегистрированными пользователями системы биометрической
идентификации. Включает функции добавления, редактирования, удаления
пользователей и управления их биометрическими данными.

Основные функции:
- Регистрация новых пользователей с фотографиями
- Обновление биометрических данных существующих пользователей
- Удаление пользователей с каскадной очисткой данных
- Просмотр списка всех зарегистрированных пользователей
- Предварительный просмотр загружаемых фотографий
- Интеграция с системой аудита для логирования всех операций

Архитектурные решения:
- Двухпанельный интерфейс (добавление + управление)
- Проверка входных данных на стороне клиента
- Безопасное управление файлами фотографий
- Транзакционные операции с автоматическим откатом при ошибках
"""

import tkinter as tk  # Основная библиотека для создания графического интерфейса
from tkinter import ttk, filedialog, messagebox  # Дополнительные компоненты графического интерфейса
from PIL import Image, ImageTk  # Библиотеки для обработки и отображения изображений
import os  # Операции с файловой системой
import shutil  # Высокоуровневые операции с файлами
from config.settings import PHOTOS_DIR, PHOTO_PREVIEW_SIZE, GUI_BUTTON_PADDING_X, GUI_BUTTON_PADDING_Y


class UserManagementWidget:
    """
    Виджет управления пользователями системы распознавания лиц
    
    Предоставляет полнофункциональный интерфейс для администрирования
    базы пользователей системы биометрической идентификации.
    
    Ключевые возможности:
    - Операции создания, чтения, обновления и удаления пользователей
    - Загрузка и проверка фотографий пользователей
    - Автоматическая генерация биометрических отпечатков
    - Предварительный просмотр загружаемых изображений
    - Интеграция с системой аудита безопасности
    - Каскадное удаление связанных файлов и данных
    
    Архитектурные особенности:
    - Транзакционные операции для обеспечения целостности данных
    - Проверка данных на стороне клиента для улучшения пользовательского опыта
    - Безопасные операции с файлами с корректной обработкой ошибок
    - Обновление списков, управляемое событиями, после операций
    """
    
    def __init__(self, parent_notebook, db, face_engine, load_encodings_callback):
        """
        Инициализация виджета управления пользователями
        
        Аргументы:
            parent_notebook (ttk.Notebook): Родительский контейнер вкладок
            db (DatabaseManager): Менеджер базы данных пользователей
            face_engine (FaceAnalysisEngine): Движок анализа лиц для создания кодировок
            load_encodings_callback (callable): Функция обратного вызова для обновления кодировок в системе
        """
        # Сохранение ссылок на внешние компоненты
        self.notebook = parent_notebook  # Контейнер вкладок
        self.db = db  # Менеджер базы данных
        self.face_engine = face_engine  # Движок анализа лиц
        self.load_encodings_callback = load_encodings_callback  # Функция обратного вызова обновления кодировок
        
        # Состояние виджета
        self.selected_photo_file_path = ""  # Путь к выбранной фотографии
        self.audit_logger_provider = None  # Поставщик системы аудита
        
        # Инициализация пользовательского интерфейса
        self.initialize_management_interface()
        
        # Загрузка начального списка пользователей
        self.reload_users_table()
    
    def set_audit_logger(self, audit_provider_function):
        """
        Установка поставщика системы аудита через внедрение зависимостей
        
        Аргументы:
            audit_provider_function (callable): Функция получения экземпляра логгера аудита
        """
        self.audit_logger_provider = audit_provider_function
    
    def initialize_management_interface(self):
        """
        Создание двухпанельного интерфейса управления пользователями
        
        Интерфейс состоит из:
        1. Левая панель: Форма добавления нового пользователя
        2. Правая панель: Список существующих пользователей с кнопками управления
        """
        # Создание основного фрейма вкладки
        self.frame = tk.Frame(self.notebook, bg="#6B46C1")
        self.notebook.add(self.frame, text="  Управление пользователями  ")
        
        # Основной контейнер с сеткой для двухпанельного размещения
        main_container = tk.Frame(self.frame, bg="#6B46C1")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Настройка сетки для равномерного распределения панелей
        main_container.grid_columnconfigure(0, weight=1)  # Левая панель
        main_container.grid_columnconfigure(1, weight=1)  # Правая панель
        main_container.grid_rowconfigure(0, weight=1)
        
        # Создание панелей интерфейса
        self.create_user_addition_panel(main_container)  # Левая панель - добавление
        self.create_user_list_panel(main_container)      # Правая панель - список
    
    def create_user_addition_panel(self, parent):
        """
        Создание панели добавления нового пользователя
        
        Включает:
        - Поля ввода пользовательских данных
        - Секцию загрузки фотографии с предварительным просмотром
        - Кнопку добавления пользователя
        
        Аргументы:
            parent (tk.Widget): Родительский контейнер
        """
        # Левая панель с рамкой
        left_panel = tk.Frame(parent, bg="white", relief="raised", bd=2)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Заголовок панели
        header_frame = tk.Frame(left_panel, bg="#7C3AED", height=40)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="ДОБАВИТЬ ПОЛЬЗОВАТЕЛЯ", 
                        font=("Arial", 12, "bold"), bg="#7C3AED", fg="white")
        title.pack(expand=True)
        
        # Контейнер содержимого панели
        content = tk.Frame(left_panel, bg="white")
        content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Создание секций формы
        self.create_user_input_fields(content)      # Поля ввода данных
        self.create_photo_upload_section(content)   # Секция загрузки фото
        self.create_user_addition_button(content)   # Кнопка добавления
    
    def create_user_input_fields(self, parent):
        """
        Создание полей ввода пользовательских данных
        
        Включает проверяемые поля:
        - ID пользователя (уникальный идентификатор)
        - Имя пользователя (отображаемое имя)
        
        Аргументы:
            parent (tk.Widget): Родительский контейнер
        """
        # Поле ID пользователя
        id_frame = tk.Frame(parent, bg="white")
        id_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(id_frame, text="ID пользователя:", font=("Arial", 10, "bold"), 
                bg="white", fg="#374151").pack(anchor="w")
        self.user_id_entry = tk.Entry(id_frame, font=("Arial", 10), relief="solid", bd=1)
        self.user_id_entry.pack(fill="x", pady=(3, 0), ipady=3)
        
        # Поле имени пользователя
        name_frame = tk.Frame(parent, bg="white")
        name_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(name_frame, text="Имя пользователя:", font=("Arial", 10, "bold"), 
                bg="white", fg="#374151").pack(anchor="w")
        self.name_entry = tk.Entry(name_frame, font=("Arial", 10), relief="solid", bd=1)
        self.name_entry.pack(fill="x", pady=(3, 0), ipady=3)
    
    def create_photo_upload_section(self, parent):
        """
        Создание секции загрузки и предварительного просмотра фотографии
        
        Включает:
        - Область предварительного просмотра фотографии
        - Кнопку выбора файла фотографии
        - Индикатор состояния загрузки
        
        Аргументы:
            parent (tk.Widget): Родительский контейнер
        """
        photo_frame = tk.Frame(parent, bg="white")
        photo_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(photo_frame, text="Фотография:", font=("Arial", 10, "bold"), 
                bg="white", fg="#374151").pack(anchor="w", pady=(0, 5))
        
        # Контейнер предварительного просмотра с фиксированным размером
        preview_container = tk.Frame(photo_frame, bg="#F3F4F6", relief="solid", bd=1, 
                                   width=PHOTO_PREVIEW_SIZE[0], height=PHOTO_PREVIEW_SIZE[1])
        preview_container.pack(pady=(0, 6))
        preview_container.pack_propagate(False)
        
        # Метка для отображения предварительного просмотра фотографии
        self.photo_preview = tk.Label(preview_container, text="Превью", 
                                     bg="#F3F4F6", font=("Arial", 8), fg="#6B7280")
        self.photo_preview.pack(fill="both", expand=True)
        
        # Кнопка выбора фотографии
        select_btn = tk.Button(photo_frame, text="Выбрать фото", 
                              font=("Arial", 9, "bold"), bg="#6366F1", fg="white",
                              relief="flat", padx=GUI_BUTTON_PADDING_X, pady=5, 
                              command=self.handle_photo_selection)
        select_btn.pack(fill="x")
        
        # Индикатор состояния загрузки фотографии
        self.photo_status_label = tk.Label(photo_frame, text="Фото не выбрано", 
                                          font=("Arial", 8), bg="white", fg="#6B7280")
        self.photo_status_label.pack(pady=(5, 0))
    
    def create_user_addition_button(self, parent):
        """
        Создание кнопки добавления пользователя
        
        Аргументы:
            parent (tk.Widget): Родительский контейнер
        """
        actions_frame = tk.Frame(parent, bg="white")
        actions_frame.pack(fill="x", pady=(10, 0))
        
        add_btn = tk.Button(actions_frame, text="Добавить пользователя", 
                           font=("Arial", 10, "bold"), bg="#10B981", fg="white",
                           relief="flat", padx=GUI_BUTTON_PADDING_X, pady=8, 
                           command=self.handle_user_addition)
        add_btn.pack(fill="x")
    
    def create_user_list_panel(self, parent):
        """
        Создание панели списка пользователей
        
        Включает:
        - Заголовок панели
        - Таблицу пользователей с прокруткой
        - Кнопки управления пользователями
        
        Аргументы:
            parent (tk.Widget): Родительский контейнер
        """
        # Правая панель с рамкой
        right_panel = tk.Frame(parent, bg="white", relief="raised", bd=2)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Заголовок панели
        header_frame = tk.Frame(right_panel, bg="#7C3AED", height=40)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="СПИСОК ПОЛЬЗОВАТЕЛЕЙ", 
                        font=("Arial", 12, "bold"), bg="#7C3AED", fg="white")
        title.pack(expand=True)
        
        # Создание компонентов панели
        self.initialize_users_table(right_panel)        # Таблица пользователей
        self.create_user_management_buttons(right_panel) # Кнопки управления
    
    def initialize_users_table(self, parent):
        """
        Создание таблицы пользователей с функцией прокрутки
        
        Таблица включает колонки:
        - ID: Идентификатор пользователя
        - Имя: Отображаемое имя пользователя  
        - Фото: Состояние наличия фотографии
        
        Аргументы:
            parent (tk.Widget): Родительский контейнер
        """
        list_content = tk.Frame(parent, bg="white")
        list_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Определение колонок таблицы
        columns = ("ID", "Имя", "Фото")
        self.users_tree = ttk.Treeview(list_content, columns=columns, 
                                      show="headings", height=12)
        
        # Настройка заголовков и ширины колонок
        self.users_tree.heading("ID", text="ID")
        self.users_tree.heading("Имя", text="Имя")
        self.users_tree.heading("Фото", text="Фото")
        
        self.users_tree.column("ID", width=80)
        self.users_tree.column("Имя", width=120)
        self.users_tree.column("Фото", width=100)
        
        # Вертикальная прокрутка для таблицы
        scrollbar = ttk.Scrollbar(list_content, orient="vertical", 
                                 command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение компонентов
        self.users_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_user_management_buttons(self, parent):
        """
        Создание панели кнопок управления пользователями
        
        Включает кнопки:
        - Обновить фото: Замена фотографии выбранного пользователя
        - Удалить: Удаление пользователя из системы
        - Обновить список: Перезагрузка таблицы пользователей
        
        Аргументы:
            parent (tk.Widget): Родительский контейнер
        """
        controls = tk.Frame(parent, bg="white", height=40)
        controls.pack(fill="x", padx=10, pady=(0, 10))
        controls.pack_propagate(False)
        
        # Кнопка обновления фотографии пользователя
        update_btn = tk.Button(controls, text="Обновить фото", 
                              font=("Arial", 9, "bold"), bg="#F59E0B", fg="white",
                              relief="flat", padx=8, pady=6, 
                              command=self.handle_user_photo_update)
        update_btn.pack(side="left", padx=(0, 3))
        
        # Кнопка удаления пользователя
        delete_btn = tk.Button(controls, text="Удалить", 
                              font=("Arial", 9, "bold"), bg="#EF4444", fg="white",
                              relief="flat", padx=8, pady=6, 
                              command=self.handle_user_deletion)
        delete_btn.pack(side="left", padx=(0, 3))
        
        # Кнопка обновления списка пользователей
        refresh_btn = tk.Button(controls, text="Обновить список", 
                               font=("Arial", 9, "bold"), bg="#6366F1", fg="white",
                               relief="flat", padx=8, pady=6, 
                               command=self.reload_users_table)
        refresh_btn.pack(side="left")
    
    def handle_photo_selection(self):
        """
        Обработка выбора фотографии пользователя
        
        Открывает диалог выбора файла, проверяет выбранное изображение
        и отображает предварительный просмотр. Поддерживает основные
        форматы изображений: JPEG, PNG, BMP.
        """
        # Открытие диалога выбора файла
        file_path = filedialog.askopenfilename(
            title="Выберите фотографию пользователя",
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            # Сохранение пути к выбранной фотографии
            self.selected_photo_file_path = file_path
            filename = os.path.basename(file_path)
            
            # Обновление индикатора состояния
            self.photo_status_label.config(text=f"✓ {filename}", fg="#10B981")
            
            # Создание и отображение предварительного просмотра
            try:
                # Загрузка и масштабирование изображения для предварительного просмотра
                pil_image = Image.open(file_path)
                pil_image = pil_image.resize(PHOTO_PREVIEW_SIZE, Image.Resampling.LANCZOS)
                photo_preview = ImageTk.PhotoImage(pil_image)
                
                # Отображение предварительного просмотра в интерфейсе
                self.photo_preview.config(image=photo_preview, text="")
                self.photo_preview.image = photo_preview  # Сохранение ссылки для предотвращения сборки мусора
                
            except Exception as e:
                # Обработка ошибок загрузки изображения
                print(f"Ошибка загрузки предварительного просмотра изображения: {e}")
                self.photo_preview.config(image="", text="Ошибка", 
                                        font=("Arial", 8), fg="#EF4444")
    
    def handle_user_addition(self):
        """
        Обработка добавления нового пользователя в систему
        
        Выполняет полный цикл регистрации пользователя:
        1. Проверка входных данных
        2. Копирование фотографии в системную папку
        3. Генерация биометрического отпечатка
        4. Сохранение в базу данных
        5. Обновление интерфейса и кодировок
        6. Логирование операции в систему аудита
        
        Использует транзакционный подход с автоматическим откатом при ошибках.
        """
        # Получение и проверка входных данных
        user_id = self.user_id_entry.get().strip()
        name = self.name_entry.get().strip()
        
        # Проверка данных на стороне клиента для обязательных полей
        if not user_id or not name:
            messagebox.showerror("Ошибка проверки данных", "Заполните все обязательные поля!")
            return
        
        if not self.selected_photo_file_path:
            messagebox.showerror("Ошибка проверки данных", "Выберите фотографию пользователя!")
            return
        
        # Определение целевого пути для фотографии
        photo_filename = f"{user_id}.jpg"
        photo_destination = os.path.join(PHOTOS_DIR, photo_filename)
        
        try:
            # Транзакционная операция добавления пользователя
            
            # 1. Копирование фотографии в системную папку
            shutil.copy2(self.selected_photo_file_path, photo_destination)
            
            # 2. Генерация биометрического отпечатка лица
            face_encoding = self.face_engine.generate_facial_encoding(photo_destination)
            
            # 3. Сохранение пользователя в базу данных
            if self.db.add_user(user_id, name, photo_destination, face_encoding):
                # Успешное добавление - логирование и обновление интерфейса
                audit = self.audit_logger_provider() if self.audit_logger_provider else None
                if audit:
                    audit.log_user_management_action("added", user_id, True)
                
                messagebox.showinfo("Успех", f"Пользователь '{name}' успешно добавлен в систему!")
                
                # Очистка формы и обновление данных
                self.reset_input_form()
                self.reload_users_table()
                self.load_encodings_callback()  # Обновление кодировок в движке
            else:
                # Ошибка добавления (дублирование ID) - откат файловых операций
                audit = self.audit_logger_provider() if self.audit_logger_provider else None
                if audit:
                    audit.log_user_management_action("added", user_id, False)
                
                messagebox.showerror("Ошибка", "Пользователь с таким ID уже существует в системе!")
                
                # Удаление скопированной фотографии при ошибке
                if os.path.exists(photo_destination):
                    os.remove(photo_destination)
                    
        except Exception as e:
            # Обработка ошибок с автоматическим откатом
            audit = self.audit_logger_provider() if self.audit_logger_provider else None
            if audit:
                audit.log_user_management_action("added", user_id, False)
            
            # Очистка созданных файлов при ошибке
            if os.path.exists(photo_destination):
                try:
                    os.remove(photo_destination)
                except OSError:
                    pass
            
            messagebox.showerror("Ошибка", f"Не удалось добавить пользователя: {str(e)}")
    
    def handle_user_photo_update(self):
        """
        Обработка обновления фотографии существующего пользователя
        
        Заменяет фотографию и биометрический отпечаток выбранного пользователя
        с сохранением целостности данных и корректной очисткой старых файлов.
        """
        # Проверка выбора пользователя в таблице
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", 
                                 "Выберите пользователя для обновления фотографии!")
            return
        
        # Проверка выбора новой фотографии
        if not self.selected_photo_file_path:
            messagebox.showerror("Ошибка", "Сначала выберите новую фотографию!")
            return
        
        # Получение данных выбранного пользователя
        user_data = self.users_tree.item(selected_item)
        user_id = user_data['values'][0]
        
        # Подтверждение операции пользователем
        if messagebox.askyesno("Подтверждение", 
                              f"Обновить фотографию для пользователя '{user_id}'?\n"
                              f"Старая фотография будет удалена безвозвратно."):
            try:
                # Определение путей для файлов
                photo_filename = f"{user_id}.jpg"
                photo_destination = os.path.join(PHOTOS_DIR, photo_filename)
                
                # Удаление старой фотографии
                if os.path.exists(photo_destination):
                    os.remove(photo_destination)
                
                # Копирование новой фотографии
                shutil.copy2(self.selected_photo_file_path, photo_destination)
                
                # Генерация нового биометрического отпечатка
                face_encoding = self.face_engine.generate_facial_encoding(photo_destination)
                
                # Обновление биометрических данных в базе
                if self.db.update_user_facial_encoding(user_id, face_encoding):
                    # Успешное обновление
                    audit = self.audit_logger_provider() if self.audit_logger_provider else None
                    if audit:
                        audit.log_user_management_action("photo_updated", user_id, True)
                    
                    messagebox.showinfo("Успех", "Фотография пользователя успешно обновлена!")
                    
                    # Обновление интерфейса и кодировок
                    self.reset_input_form()
                    self.reload_users_table()
                    self.load_encodings_callback()
                else:
                    # Ошибка обновления в базе данных
                    audit = self.audit_logger_provider() if self.audit_logger_provider else None
                    if audit:
                        audit.log_user_management_action("photo_updated", user_id, False)
                    
                    messagebox.showerror("Ошибка", "Не удалось обновить биометрические данные в базе!")
                    
            except Exception as e:
                # Обработка ошибок обновления
                audit = self.audit_logger_provider() if self.audit_logger_provider else None
                if audit:
                    audit.log_user_management_action("photo_updated", user_id, False)
                
                messagebox.showerror("Ошибка", f"Не удалось обновить фотографию: {str(e)}")
    
    def handle_user_deletion(self):
        """
        Обработка удаления пользователя из системы
        
        Выполняет каскадное удаление пользователя с очисткой всех связанных данных:
        - Запись в базе данных
        - Файл фотографии
        - Биометрические данные из движка распознавания
        """
        # Проверка выбора пользователя
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", 
                                 "Выберите пользователя для удаления!")
            return
        
        # Получение данных пользователя
        user_data = self.users_tree.item(selected_item)
        user_id = user_data['values'][0]
        user_name = user_data['values'][1]
        
        # Подтверждение удаления с предупреждением о необратимости
        if messagebox.askyesno("Подтверждение удаления", 
                              f"Удалить пользователя '{user_name}' (ID: {user_id})?\n\n"
                              f"Внимание: Все данные пользователя будут удалены безвозвратно!"):
            
            # Выполнение каскадного удаления
            if self.db.remove_user(user_id):
                # Успешное удаление
                audit = self.audit_logger_provider() if self.audit_logger_provider else None
                if audit:
                    audit.log_user_management_action("deleted", user_id, True)
                
                messagebox.showinfo("Успех", f"Пользователь '{user_name}' удален из системы!")
                
                # Обновление интерфейса и кодировок
                self.reload_users_table()
                self.load_encodings_callback()
            else:
                # Ошибка удаления
                audit = self.audit_logger_provider() if self.audit_logger_provider else None
                if audit:
                    audit.log_user_management_action("deleted", user_id, False)
                
                messagebox.showerror("Ошибка", "Не удалось удалить пользователя из системы!")
    
    def reload_users_table(self):
        """
        Перезагрузка таблицы пользователей из базы данных
        
        Обновляет отображение списка всех зарегистрированных пользователей
        с актуальной информацией из базы данных.
        """
        # Очистка существующих записей в таблице
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # Загрузка актуального списка пользователей
        users = self.db.get_all_users()
        for user in users:
            # Форматирование информации о фотографии для отображения
            photo_name = os.path.basename(user[3]) if user[3] else "Нет фото"
            
            # Добавление пользователя в таблицу
            self.users_tree.insert("", "end", values=(user[1], user[2], photo_name))
    
    def reset_input_form(self):
        """
        Сброс формы добавления пользователя в исходное состояние
        
        Очищает все поля ввода и сбрасывает состояние выбора фотографии
        для подготовки к добавлению следующего пользователя.
        """
        # Очистка текстовых полей
        self.user_id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        
        # Сброс состояния выбора фотографии
        self.selected_photo_file_path = ""
        self.photo_status_label.config(text="Фото не выбрано", fg="#6B7280")
        
        # Сброс предварительного просмотра фотографии
        self.photo_preview.config(image="", text="Превью", 
                                 font=("Arial", 8), fg="#6B7280")
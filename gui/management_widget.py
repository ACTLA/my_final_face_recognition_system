# gui/management_widget.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
from config.settings import PHOTOS_DIR

class ManagementWidget:
    """Виджет управления пользователями"""
    
    def __init__(self, parent_notebook, db, face_engine, load_encodings_callback):
        self.notebook = parent_notebook
        self.db = db
        self.face_engine = face_engine
        self.load_encodings_callback = load_encodings_callback
        
        # Переменные
        self.photo_path = ""
        self.get_audit_logger = None
        
        # Создание виджета
        self.setup_widget()
        
        # Загрузка списка пользователей
        self.refresh_user_list()
    
    def set_audit_logger(self, get_audit_func):
        """Установка функции получения аудит логгера"""
        self.get_audit_logger = get_audit_func
    
    def setup_widget(self):
        """Создание интерфейса вкладки"""
        # Создание фрейма вкладки
        self.frame = tk.Frame(self.notebook, bg="#6B46C1")
        self.notebook.add(self.frame, text="  👥 Управление пользователями  ")
        
        # Основной контейнер
        main_container = tk.Frame(self.frame, bg="#6B46C1")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Настройка сетки
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Левая панель - добавление
        self.create_add_panel(main_container)
        
        # Правая панель - список
        self.create_list_panel(main_container)
    
    def create_add_panel(self, parent):
        """Создание панели добавления пользователя"""
        left_panel = tk.Frame(parent, bg="white", relief="raised", bd=2)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Заголовок
        header_frame = tk.Frame(left_panel, bg="#7C3AED", height=40)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="ДОБАВИТЬ ПОЛЬЗОВАТЕЛЯ", 
                        font=("Arial", 12, "bold"), bg="#7C3AED", fg="white")
        title.pack(expand=True)
        
        # Контент
        content = tk.Frame(left_panel, bg="white")
        content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Поля ввода
        self.create_input_fields(content)
        
        # Выбор фото
        self.create_photo_selection(content)
        
        # Кнопка добавления
        self.create_add_button(content)
    
    def create_input_fields(self, parent):
        """Создание полей ввода"""
        # ID пользователя
        id_frame = tk.Frame(parent, bg="white")
        id_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(id_frame, text="ID пользователя:", font=("Arial", 10, "bold"), 
                bg="white", fg="#374151").pack(anchor="w")
        self.user_id_entry = tk.Entry(id_frame, font=("Arial", 10), relief="solid", bd=1)
        self.user_id_entry.pack(fill="x", pady=(3, 0), ipady=3)
        
        # Имя пользователя
        name_frame = tk.Frame(parent, bg="white")
        name_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(name_frame, text="Имя пользователя:", font=("Arial", 10, "bold"), 
                bg="white", fg="#374151").pack(anchor="w")
        self.name_entry = tk.Entry(name_frame, font=("Arial", 10), relief="solid", bd=1)
        self.name_entry.pack(fill="x", pady=(3, 0), ipady=3)
    
    def create_photo_selection(self, parent):
        """Создание области выбора фотографии"""
        photo_frame = tk.Frame(parent, bg="white")
        photo_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(photo_frame, text="Фотография:", font=("Arial", 10, "bold"), 
                bg="white", fg="#374151").pack(anchor="w", pady=(0, 5))
        
        # Превью
        preview_container = tk.Frame(photo_frame, bg="#F3F4F6", relief="solid", bd=1, 
                                   width=120, height=120)
        preview_container.pack(pady=(0, 6))
        preview_container.pack_propagate(False)
        
        self.photo_preview = tk.Label(preview_container, text="Превью", 
                                     bg="#F3F4F6", font=("Arial", 8), fg="#6B7280")
        self.photo_preview.pack(fill="both", expand=True)
        
        # Кнопка выбора
        select_btn = tk.Button(photo_frame, text="Выбрать фото", 
                              font=("Arial", 9, "bold"), bg="#6366F1", fg="white",
                              relief="flat", padx=10, pady=5, command=self.select_photo)
        select_btn.pack(fill="x")
        
        # Статус
        self.photo_status_label = tk.Label(photo_frame, text="Фото не выбрано", 
                                          font=("Arial", 8), bg="white", fg="#6B7280")
        self.photo_status_label.pack(pady=(5, 0))
    
    def create_add_button(self, parent):
        """Создание кнопки добавления"""
        actions_frame = tk.Frame(parent, bg="white")
        actions_frame.pack(fill="x", pady=(10, 0))
        
        add_btn = tk.Button(actions_frame, text="Добавить пользователя", 
                           font=("Arial", 10, "bold"), bg="#10B981", fg="white",
                           relief="flat", padx=15, pady=8, command=self.add_user)
        add_btn.pack(fill="x")
    
    def create_list_panel(self, parent):
        """Создание панели списка пользователей"""
        right_panel = tk.Frame(parent, bg="white", relief="raised", bd=2)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Заголовок
        header_frame = tk.Frame(right_panel, bg="#7C3AED", height=40)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="СПИСОК ПОЛЬЗОВАТЕЛЕЙ", 
                        font=("Arial", 12, "bold"), bg="#7C3AED", fg="white")
        title.pack(expand=True)
        
        # Таблица
        self.create_users_table(right_panel)
        
        # Кнопки управления
        self.create_control_buttons(right_panel)
    
    def create_users_table(self, parent):
        """Создание таблицы пользователей"""
        list_content = tk.Frame(parent, bg="white")
        list_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("ID", "Имя", "Фото")
        self.users_tree = ttk.Treeview(list_content, columns=columns, 
                                      show="headings", height=12)
        
        # Настройка колонок
        self.users_tree.heading("ID", text="ID")
        self.users_tree.heading("Имя", text="Имя")
        self.users_tree.heading("Фото", text="Фото")
        
        self.users_tree.column("ID", width=80)
        self.users_tree.column("Имя", width=120)
        self.users_tree.column("Фото", width=100)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(list_content, orient="vertical", 
                                 command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение
        self.users_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_control_buttons(self, parent):
        """Создание кнопок управления"""
        controls = tk.Frame(parent, bg="white", height=40)
        controls.pack(fill="x", padx=10, pady=(0, 10))
        controls.pack_propagate(False)
        
        # Кнопка обновления фото
        update_btn = tk.Button(controls, text="Обновить фото", 
                              font=("Arial", 9, "bold"), bg="#F59E0B", fg="white",
                              relief="flat", padx=8, pady=6, command=self.update_user_photo)
        update_btn.pack(side="left", padx=(0, 3))
        
        # Кнопка удаления
        delete_btn = tk.Button(controls, text="Удалить", 
                              font=("Arial", 9, "bold"), bg="#EF4444", fg="white",
                              relief="flat", padx=8, pady=6, command=self.delete_user)
        delete_btn.pack(side="left", padx=(0, 3))
        
        # Кнопка обновления списка
        refresh_btn = tk.Button(controls, text="Обновить список", 
                               font=("Arial", 9, "bold"), bg="#6366F1", fg="white",
                               relief="flat", padx=8, pady=6, command=self.refresh_user_list)
        refresh_btn.pack(side="left")
    
    def select_photo(self):
        """Выбор фотографии"""
        file_path = filedialog.askopenfilename(
            title="Выберите фотографию",
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            self.photo_path = file_path
            filename = os.path.basename(file_path)
            self.photo_status_label.config(text=f"✓ {filename}", fg="#10B981")
            
            # Показываем превью
            try:
                pil_image = Image.open(file_path)
                pil_image = pil_image.resize((110, 110), Image.Resampling.LANCZOS)
                photo_preview = ImageTk.PhotoImage(pil_image)
                
                self.photo_preview.config(image=photo_preview, text="")
                self.photo_preview.image = photo_preview
                
            except Exception as e:
                print(f"Ошибка загрузки превью: {e}")
                self.photo_preview.config(image="", text="Ошибка", 
                                        font=("Arial", 8), fg="#EF4444")
    
    def add_user(self):
        """Добавление пользователя"""
        user_id = self.user_id_entry.get().strip()
        name = self.name_entry.get().strip()
        
        if not user_id or not name:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        
        if not self.photo_path:
            messagebox.showerror("Ошибка", "Выберите фотографию!")
            return
        
        photo_filename = f"{user_id}.jpg"
        photo_destination = os.path.join(PHOTOS_DIR, photo_filename)
        
        try:
            # Копируем фото
            shutil.copy2(self.photo_path, photo_destination)
            
            # Создаем кодировку
            face_encoding = self.face_engine.create_face_encoding(photo_destination)
            
            # Добавляем в базу
            if self.db.add_user(user_id, name, photo_destination, face_encoding):
                # Логирование успеха
                audit = self.get_audit_logger() if self.get_audit_logger else None
                if audit:
                    audit.log_user_action("added", user_id, True)
                
                messagebox.showinfo("Успех", "Пользователь добавлен!")
                
                # Очистка полей
                self.clear_form()
                
                # Обновление данных
                self.refresh_user_list()
                self.load_encodings_callback()
            else:
                # Логирование неудачи
                audit = self.get_audit_logger() if self.get_audit_logger else None
                if audit:
                    audit.log_user_action("added", user_id, False)
                
                messagebox.showerror("Ошибка", "Пользователь с таким ID уже существует!")
                if os.path.exists(photo_destination):
                    os.remove(photo_destination)
                    
        except Exception as e:
            # Логирование ошибки
            audit = self.get_audit_logger() if self.get_audit_logger else None
            if audit:
                audit.log_user_action("added", user_id, False)
            
            messagebox.showerror("Ошибка", f"Не удалось добавить пользователя: {str(e)}")
    
    def update_user_photo(self):
        """Обновление фотографии пользователя"""
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", 
                                 "Выберите пользователя для обновления фото!")
            return
        
        if not self.photo_path:
            messagebox.showerror("Ошибка", "Сначала выберите новую фотографию!")
            return
        
        user_data = self.users_tree.item(selected_item)
        user_id = user_data['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Обновить фото для пользователя {user_id}?"):
            try:
                photo_filename = f"{user_id}.jpg"
                photo_destination = os.path.join(PHOTOS_DIR, photo_filename)
                
                # Удаляем старое фото
                if os.path.exists(photo_destination):
                    os.remove(photo_destination)
                
                # Копируем новое
                shutil.copy2(self.photo_path, photo_destination)
                
                # Создаем новую кодировку
                face_encoding = self.face_engine.create_face_encoding(photo_destination)
                
                # Обновляем в БД
                if self.db.update_user_encoding(user_id, face_encoding):
                    # Логирование успеха
                    audit = self.get_audit_logger() if self.get_audit_logger else None
                    if audit:
                        audit.log_user_action("photo_updated", user_id, True)
                    
                    messagebox.showinfo("Успех", "Фото пользователя обновлено!")
                    
                    # Очистка
                    self.clear_form()
                    
                    # Обновление
                    self.refresh_user_list()
                    self.load_encodings_callback()
                else:
                    # Логирование неудачи
                    audit = self.get_audit_logger() if self.get_audit_logger else None
                    if audit:
                        audit.log_user_action("photo_updated", user_id, False)
                    
                    messagebox.showerror("Ошибка", "Не удалось обновить фото в БД!")
                    
            except Exception as e:
                # Логирование ошибки
                audit = self.get_audit_logger() if self.get_audit_logger else None
                if audit:
                    audit.log_user_action("photo_updated", user_id, False)
                
                messagebox.showerror("Ошибка", f"Не удалось обновить фото: {str(e)}")
    
    def delete_user(self):
        """Удаление пользователя"""
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", 
                                 "Выберите пользователя для удаления!")
            return
        
        user_data = self.users_tree.item(selected_item)
        user_id = user_data['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить пользователя {user_id}?"):
            if self.db.delete_user(user_id):
                # Логирование успеха
                audit = self.get_audit_logger() if self.get_audit_logger else None
                if audit:
                    audit.log_user_action("deleted", user_id, True)
                
                messagebox.showinfo("Успех", "Пользователь удален!")
                self.refresh_user_list()
                self.load_encodings_callback()
            else:
                # Логирование неудачи
                audit = self.get_audit_logger() if self.get_audit_logger else None
                if audit:
                    audit.log_user_action("deleted", user_id, False)
                
                messagebox.showerror("Ошибка", "Не удалось удалить пользователя!")
    
    def refresh_user_list(self):
        """Обновление списка пользователей"""
        # Очистка таблицы
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # Загрузка пользователей
        users = self.db.get_all_users()
        for user in users:
            photo_name = os.path.basename(user[3]) if user[3] else "Нет"
            self.users_tree.insert("", "end", values=(user[1], user[2], photo_name))
    
    def clear_form(self):
        """Очистка формы"""
        self.user_id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.photo_path = ""
        self.photo_status_label.config(text="Фото не выбрано", fg="#6B7280")
        self.photo_preview.config(image="", text="Превью", 
                                 font=("Arial", 8), fg="#6B7280")
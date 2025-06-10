import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import face_recognition
import os
import shutil
import numpy as np
from PIL import Image, ImageTk
from database import DatabaseManager

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
        
        title_label = tk.Label(title_frame, text="FACE RECOGNITION SYSTEM", 
                              font=("Arial", 18, "bold"), bg="#6B46C1", fg="white")
        title_label.pack(side="left")
        
        # Основной контейнер
        main_container = tk.Frame(self.root, bg="#6B46C1")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Левая панель - Видео
        left_panel = tk.Frame(main_container, bg="white", relief="raised", bd=2)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Заголовок видео панели
        video_header = tk.Frame(left_panel, bg="#7C3AED", height=50)
        video_header.pack(fill="x")
        video_header.pack_propagate(False)
        
        video_title = tk.Label(video_header, text="LIVE CAMERA", 
                              font=("Arial", 14, "bold"), bg="#7C3AED", fg="white")
        video_title.pack(expand=True)
        
        # Видео контейнер
        video_container = tk.Frame(left_panel, bg="black")
        video_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Метка для отображения видео
        self.video_label = tk.Label(video_container, text="Камера не запущена", 
                                   bg="black", fg="white", font=("Arial", 14))
        self.video_label.pack(fill="both", expand=True)
        
        # Кнопки управления камерой
        camera_controls = tk.Frame(left_panel, bg="white", height=60)
        camera_controls.pack(fill="x", padx=10, pady=(0, 10))
        camera_controls.pack_propagate(False)
        
        self.start_button = tk.Button(camera_controls, text="▶ Запустить камеру", 
                                     font=("Arial", 11, "bold"), bg="#10B981", fg="white",
                                     relief="flat", padx=20, pady=8, command=self.start_camera)
        self.start_button.pack(side="left", padx=(0, 10))
        
        self.stop_button = tk.Button(camera_controls, text="⏹ Остановить камеру", 
                                    font=("Arial", 11, "bold"), bg="#EF4444", fg="white",
                                    relief="flat", padx=20, pady=8, command=self.stop_camera,
                                    state="disabled")
        self.stop_button.pack(side="left")
        
        # Правая панель - Информация и управление
        right_panel = tk.Frame(main_container, bg="white", relief="raised", bd=2, width=400)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)
        
        # === СЕКЦИЯ РАСПОЗНАВАНИЯ ===
        recognition_frame = tk.Frame(right_panel, bg="white")
        recognition_frame.pack(fill="x", padx=15, pady=15)
        
        # Заголовок секции распознавания
        rec_header = tk.Label(recognition_frame, text="РАСПОЗНАННЫЙ ПОЛЬЗОВАТЕЛЬ", 
                             font=("Arial", 12, "bold"), bg="white", fg="#374151")
        rec_header.pack(anchor="w", pady=(0, 10))
        
        # Статус распознавания
        self.status_label = tk.Label(recognition_frame, text="Ожидание...", 
                                    font=("Arial", 14, "bold"), bg="white", fg="#6B7280")
        self.status_label.pack(anchor="w", pady=(0, 10))
        
        # Информация о пользователе
        info_container = tk.Frame(recognition_frame, bg="#F9FAFB", relief="solid", bd=1)
        info_container.pack(fill="x", pady=(0, 10))
        
        # ID пользователя
        id_frame = tk.Frame(info_container, bg="#F9FAFB")
        id_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(id_frame, text="ID:", font=("Arial", 10, "bold"), bg="#F9FAFB", fg="#374151").pack(side="left")
        self.user_id_label = tk.Label(id_frame, text="—", font=("Arial", 10), bg="#F9FAFB", fg="#6B7280")
        self.user_id_label.pack(side="right")
        
        # Имя пользователя
        name_frame = tk.Frame(info_container, bg="#F9FAFB")
        name_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(name_frame, text="Имя:", font=("Arial", 10, "bold"), bg="#F9FAFB", fg="#374151").pack(side="left")
        self.name_label = tk.Label(name_frame, text="—", font=("Arial", 10), bg="#F9FAFB", fg="#6B7280")
        self.name_label.pack(side="right")
        
        # Фотография пользователя
        photo_frame = tk.Frame(recognition_frame, bg="white")
        photo_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(photo_frame, text="Фотография:", font=("Arial", 10, "bold"), 
                bg="white", fg="#374151").pack(anchor="w")
        
        self.photo_display = tk.Label(photo_frame, text="Нет фото", bg="#F3F4F6", 
                                     width=20, height=8, relief="solid", bd=1)
        self.photo_display.pack(pady=5)
        
        # === РАЗДЕЛИТЕЛЬ ===
        separator = tk.Frame(right_panel, bg="#E5E7EB", height=2)
        separator.pack(fill="x", padx=15, pady=10)
        
        # === СЕКЦИЯ ДОБАВЛЕНИЯ ПОЛЬЗОВАТЕЛЯ ===
        add_user_frame = tk.Frame(right_panel, bg="white")
        add_user_frame.pack(fill="x", padx=15, pady=15)
        
        # Заголовок секции добавления
        add_header = tk.Label(add_user_frame, text="ДОБАВИТЬ ПОЛЬЗОВАТЕЛЯ", 
                             font=("Arial", 12, "bold"), bg="white", fg="#374151")
        add_header.pack(anchor="w", pady=(0, 15))
        
        # Поле ID пользователя
        id_input_frame = tk.Frame(add_user_frame, bg="white")
        id_input_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(id_input_frame, text="ID пользователя:", font=("Arial", 10, "bold"), 
                bg="white", fg="#374151").pack(anchor="w")
        self.user_id_entry = tk.Entry(id_input_frame, font=("Arial", 11), relief="solid", bd=1)
        self.user_id_entry.pack(fill="x", pady=(5, 0))
        
        # Поле имени пользователя
        name_input_frame = tk.Frame(add_user_frame, bg="white")
        name_input_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(name_input_frame, text="Имя:", font=("Arial", 10, "bold"), 
                bg="white", fg="#374151").pack(anchor="w")
        self.name_entry = tk.Entry(name_input_frame, font=("Arial", 11), relief="solid", bd=1)
        self.name_entry.pack(fill="x", pady=(5, 0))
        
        # Выбор фотографии
        photo_input_frame = tk.Frame(add_user_frame, bg="white")
        photo_input_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(photo_input_frame, text="Фотография:", font=("Arial", 10, "bold"), 
                bg="white", fg="#374151").pack(anchor="w")
        
        photo_select_frame = tk.Frame(photo_input_frame, bg="white")
        photo_select_frame.pack(fill="x", pady=(5, 0))
        
        select_photo_btn = tk.Button(photo_select_frame, text="📁 Выбрать фото", 
                                    font=("Arial", 10), bg="#6366F1", fg="white",
                                    relief="flat", padx=15, pady=5, command=self.select_photo)
        select_photo_btn.pack(side="left")
        
        self.photo_status_label = tk.Label(photo_select_frame, text="Фото не выбрано", 
                                          font=("Arial", 9), bg="white", fg="#6B7280")
        self.photo_status_label.pack(side="left", padx=(10, 0))
        
        # Кнопки действий
        actions_frame = tk.Frame(add_user_frame, bg="white")
        actions_frame.pack(fill="x", pady=(15, 0))
        
        add_btn = tk.Button(actions_frame, text="➕ Добавить пользователя", 
                           font=("Arial", 11, "bold"), bg="#10B981", fg="white",
                           relief="flat", padx=20, pady=8, command=self.add_user)
        add_btn.pack(fill="x", pady=(0, 5))
        
        refresh_btn = tk.Button(actions_frame, text="🔄 Обновить кодировки", 
                               font=("Arial", 10), bg="#6366F1", fg="white",
                               relief="flat", padx=20, pady=6, command=self.load_encodings)
        refresh_btn.pack(fill="x")
        
        # === СПИСОК ПОЛЬЗОВАТЕЛЕЙ ===
        users_frame = tk.Frame(right_panel, bg="white")
        users_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        users_header = tk.Label(users_frame, text="СПИСОК ПОЛЬЗОВАТЕЛЕЙ", 
                               font=("Arial", 12, "bold"), bg="white", fg="#374151")
        users_header.pack(anchor="w", pady=(0, 10))
        
        # Таблица пользователей
        columns = ("ID", "Имя")
        self.users_tree = ttk.Treeview(users_frame, columns=columns, show="headings", height=6)
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(users_frame, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        self.users_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопка удаления
        delete_btn = tk.Button(users_frame, text="🗑 Удалить выбранного", 
                              font=("Arial", 10), bg="#EF4444", fg="white",
                              relief="flat", padx=15, pady=5, command=self.delete_user)
        delete_btn.pack(pady=(10, 0))
        
        # Загружаем список пользователей
        self.refresh_user_list()
    
    def load_encodings(self):
        # Загрузка кодировок лиц из базы данных
        try:
            self.known_encodings, self.known_user_ids = self.db.get_all_encodings()
            print(f"Загружено кодировок из БД: {len(self.known_encodings)}")
            
            if not self.known_encodings:
                print("Кодировки не найдены. Добавьте пользователей.")
                
        except Exception as e:
            print(f"Ошибка загрузки кодировок: {e}")
            self.known_encodings = []
            self.known_user_ids = []
    
    def start_camera(self):
        # Запуск камеры
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Ошибка", "Не удалось подключиться к камере!")
                return
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            self.is_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            self.process_frame()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка запуска камеры: {str(e)}")
    
    def stop_camera(self):
        # Остановка камеры
        self.is_running = False
        if self.cap:
            self.cap.release()
        
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        self.video_label.config(image="", text="Камера остановлена")
        self.reset_user_info()
    
    def process_frame(self):
        # Обработка каждого кадра с камеры
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
        
        # Обработка найденных лиц
        for face_encoding, face_location in zip(face_encodings, face_locations):
            if self.known_encodings:
                matches = face_recognition.compare_faces(self.known_encodings, face_encoding)
                face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
                
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    user_id = self.known_user_ids[best_match_index]
                    user_data = self.db.get_user(user_id)
                    if user_data:
                        recognized_user = user_data
                        name = user_data[2]
                    else:
                        name = "Ошибка БД"
                else:
                    name = "Неизвестный"
            else:
                name = "Нет кодировок"
            
            # Рисуем рамку вокруг лица
            top, right, bottom, left = face_location
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            color = (0, 255, 0) if recognized_user else (0, 0, 255)
            
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        # Обновляем информацию о пользователе
        if recognized_user:
            self.update_user_info(recognized_user)
        elif not face_locations:
            self.reset_user_info()
        
        # Конвертируем кадр для отображения в Tkinter
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        photo = ImageTk.PhotoImage(pil_image)
        
        self.video_label.config(image=photo, text="")
        self.video_label.image = photo
        
        self.root.after(30, self.process_frame)
    
    def update_user_info(self, user_data):
        # Обновление информации о распознанном пользователе
        user_id = user_data[1]
        name = user_data[2]
        photo_path = user_data[3]
        
        self.status_label.config(text="✅ Пользователь распознан", fg="#10B981")
        self.user_id_label.config(text=user_id)
        self.name_label.config(text=name)
        
        # Загружаем и отображаем фотографию
        if photo_path and os.path.exists(photo_path):
            try:
                pil_image = Image.open(photo_path)
                pil_image = pil_image.resize((120, 120), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(pil_image)
                
                self.photo_display.config(image=photo, text="")
                self.photo_display.image = photo
            except Exception as e:
                print(f"Ошибка загрузки фото: {e}")
                self.photo_display.config(image="", text="Ошибка загрузки")
        else:
            self.photo_display.config(image="", text="Фото не найдено")
    
    def reset_user_info(self):
        # Сброс информации о пользователе
        self.status_label.config(text="⏳ Ожидание...", fg="#6B7280")
        self.user_id_label.config(text="—")
        self.name_label.config(text="—")
        self.photo_display.config(image="", text="Нет фото")
    
    def select_photo(self):
        # Выбор фотографии пользователя
        file_path = filedialog.askopenfilename(
            title="Выберите фотографию",
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            self.photo_path = file_path
            self.photo_status_label.config(text=f"✓ {os.path.basename(file_path)}", fg="#10B981")
    
    def add_user(self):
        # Добавление нового пользователя
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
                messagebox.showinfo("Успех", "✅ Пользователь добавлен!")
                
                # Очищаем поля
                self.user_id_entry.delete(0, tk.END)
                self.name_entry.delete(0, tk.END)
                self.photo_path = ""
                self.photo_status_label.config(text="Фото не выбрано", fg="#6B7280")
                
                # Обновляем данные
                self.refresh_user_list()
                self.load_encodings()
            else:
                messagebox.showerror("Ошибка", "Пользователь с таким ID уже существует!")
                if os.path.exists(photo_destination):
                    os.remove(photo_destination)
                    
        except Exception as e:
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
    
    def delete_user(self):
        # Удаление выбранного пользователя
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления!")
            return
        
        user_data = self.users_tree.item(selected_item)
        user_id = user_data['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить пользователя {user_id}?"):
            if self.db.delete_user(user_id):
                messagebox.showinfo("Успех", "✅ Пользователь удален!")
                self.refresh_user_list()
                self.load_encodings()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить пользователя!")
    
    def refresh_user_list(self):
        # Обновление списка пользователей
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        users = self.db.get_all_users()
        for user in users:
            self.users_tree.insert("", "end", values=(user[1], user[2]))
    
    def on_closing(self):
        # Обработка закрытия окна
        self.stop_camera()
        self.root.destroy()

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = ModernFaceRecognitionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
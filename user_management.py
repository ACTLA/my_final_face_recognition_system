import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import face_recognition
import os
import shutil
import pickle
from database import DatabaseManager

class UserManagement:
    def __init__(self, root):
        # Инициализация окна управления пользователями
        self.root = root
        self.root.title("Управление пользователями")
        self.root.geometry("600x400")
        
        # Инициализация базы данных
        self.db = DatabaseManager()
        
        # Создание папки для фотографий если её нет
        if not os.path.exists("photos"):
            os.makedirs("photos")
        
        self.setup_ui()
        self.refresh_user_list()
    
    def setup_ui(self):
        # Создание интерфейса
        
        # Фрейм для добавления пользователя
        add_frame = ttk.LabelFrame(self.root, text="Добавить пользователя", padding="10")
        add_frame.pack(fill="x", padx=10, pady=5)
        
        # Поле для ID пользователя
        ttk.Label(add_frame, text="ID пользователя:").grid(row=0, column=0, sticky="w")
        self.user_id_entry = ttk.Entry(add_frame, width=20)
        self.user_id_entry.grid(row=0, column=1, padx=5)
        
        # Поле для имени пользователя
        ttk.Label(add_frame, text="Имя:").grid(row=1, column=0, sticky="w")
        self.name_entry = ttk.Entry(add_frame, width=20)
        self.name_entry.grid(row=1, column=1, padx=5)
        
        # Кнопка выбора фотографии
        self.photo_path = ""
        ttk.Button(add_frame, text="Выбрать фото", command=self.select_photo).grid(row=2, column=0, pady=5)
        self.photo_label = ttk.Label(add_frame, text="Фото не выбрано")
        self.photo_label.grid(row=2, column=1, padx=5)
        
        # Кнопка добавления пользователя
        ttk.Button(add_frame, text="Добавить", command=self.add_user).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Фрейм для списка пользователей
        list_frame = ttk.LabelFrame(self.root, text="Список пользователей", padding="10")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Таблица пользователей
        columns = ("ID", "Имя", "Фото")
        self.user_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # Настройка колонок
        for col in columns:
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=150)
        
        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение таблицы и скроллбара
        self.user_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопка удаления пользователя
        ttk.Button(list_frame, text="Удалить выбранного", command=self.delete_user).pack(pady=10)
        
        # Кнопка обновления кодировок лиц
        ttk.Button(self.root, text="Обновить кодировки лиц", command=self.update_encodings).pack(pady=10)
    
    def select_photo(self):
        # Выбор фотографии пользователя
        file_path = filedialog.askopenfilename(
            title="Выберите фотографию",
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            self.photo_path = file_path
            self.photo_label.config(text=f"Выбрано: {os.path.basename(file_path)}")
    
    def add_user(self):
        # Добавление нового пользователя
        user_id = self.user_id_entry.get().strip()
        name = self.name_entry.get().strip()
        
        # Проверка заполненности полей
        if not user_id or not name:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        
        if not self.photo_path:
            messagebox.showerror("Ошибка", "Выберите фотографию!")
            return
        
        # Копирование фото в папку проекта
        photo_filename = f"{user_id}.jpg"
        photo_destination = os.path.join("photos", photo_filename)
        
        try:
            # Копируем файл в папку photos
            shutil.copy2(self.photo_path, photo_destination)
            
            # Добавляем пользователя в базу данных
            if self.db.add_user(user_id, name, photo_destination):
                messagebox.showinfo("Успех", "Пользователь добавлен!")
                
                # Очищаем поля
                self.user_id_entry.delete(0, tk.END)
                self.name_entry.delete(0, tk.END)
                self.photo_path = ""
                self.photo_label.config(text="Фото не выбрано")
                
                # Обновляем список
                self.refresh_user_list()
            else:
                messagebox.showerror("Ошибка", "Пользователь с таким ID уже существует!")
                # Удаляем скопированное фото
                if os.path.exists(photo_destination):
                    os.remove(photo_destination)
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить пользователя: {str(e)}")
    
    def delete_user(self):
        # Удаление выбранного пользователя
        selected_item = self.user_tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления!")
            return
        
        # Получаем ID выбранного пользователя
        user_data = self.user_tree.item(selected_item)
        user_id = user_data['values'][0]
        
        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", f"Удалить пользователя {user_id}?"):
            if self.db.delete_user(user_id):
                messagebox.showinfo("Успех", "Пользователь удален!")
                self.refresh_user_list()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить пользователя!")
    
    def refresh_user_list(self):
        # Обновление списка пользователей
        # Очищаем таблицу
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        # Загружаем пользователей из БД
        users = self.db.get_all_users()
        for user in users:
            # user = (id, user_id, name, photo_path)
            photo_name = os.path.basename(user[3]) if user[3] else "Нет"
            self.user_tree.insert("", "end", values=(user[1], user[2], photo_name))
    
    def update_encodings(self):
        # Создание файла с кодировками лиц для распознавания
        try:
            users = self.db.get_all_users()
            if not users:
                messagebox.showwarning("Предупреждение", "Нет пользователей для кодирования!")
                return
            
            encode_list = []
            user_ids = []
            
            # Обрабатываем каждого пользователя
            for user in users:
                user_id = user[1]
                photo_path = user[3]
                
                if os.path.exists(photo_path):
                    # Загружаем изображение
                    image = cv2.imread(photo_path)
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    
                    # Получаем кодировку лица
                    face_encodings = face_recognition.face_encodings(rgb_image)
                    
                    if face_encodings:
                        encode_list.append(face_encodings[0])
                        user_ids.append(user_id)
                    else:
                        print(f"Лицо не найдено на фото пользователя {user_id}")
            
            # Сохраняем кодировки в файл
            if encode_list:
                with open("encodings.pickle", "wb") as f:
                    pickle.dump([encode_list, user_ids], f)
                
                messagebox.showinfo("Успех", f"Кодировки обновлены! Обработано: {len(encode_list)} пользователей")
            else:
                messagebox.showerror("Ошибка", "Не удалось создать кодировки!")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании кодировок: {str(e)}")

# Запуск окна управления пользователями
if __name__ == "__main__":
    root = tk.Tk()
    app = UserManagement(root)
    root.mainloop()
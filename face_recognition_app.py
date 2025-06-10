import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import face_recognition
import pickle
import os
import numpy as np
from PIL import Image, ImageTk
from database import DatabaseManager

class FaceRecognitionApp:
    def __init__(self, root):
        # Инициализация главного окна
        self.root = root
        self.root.title("Система распознавания лиц")
        self.root.geometry("800x600")
        
        # Инициализация базы данных
        self.db = DatabaseManager()
        
        # Переменные для работы с камерой
        self.cap = None
        self.is_running = False
        
        # Переменные для распознавания
        self.known_encodings = []
        self.known_user_ids = []
        self.current_user_info = None
        
        # Загрузка кодировок лиц
        self.load_encodings()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Создание интерфейса
        
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Фрейм для видео
        video_frame = ttk.LabelFrame(main_frame, text="Видео с камеры", padding="10")
        video_frame.pack(side="left", fill="both", expand=True)
        
        # Метка для отображения видео
        self.video_label = ttk.Label(video_frame, text="Камера не запущена", background="black", foreground="white")
        self.video_label.pack(fill="both", expand=True)
        
        # Кнопки управления камерой
        control_frame = ttk.Frame(video_frame)
        control_frame.pack(fill="x", pady=10)
        
        self.start_button = ttk.Button(control_frame, text="Запустить камеру", command=self.start_camera)
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Остановить камеру", command=self.stop_camera, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        # Фрейм для информации о пользователе
        info_frame = ttk.LabelFrame(main_frame, text="Информация о пользователе", padding="10")
        info_frame.pack(side="right", fill="y", padx=(10, 0))
        
        # Статус распознавания
        self.status_label = ttk.Label(info_frame, text="Ожидание...", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=10)
        
        # Информация о пользователе
        ttk.Label(info_frame, text="ID пользователя:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.user_id_label = ttk.Label(info_frame, text="—", font=("Arial", 10))
        self.user_id_label.pack(anchor="w", pady=(0, 10))
        
        ttk.Label(info_frame, text="Имя:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.name_label = ttk.Label(info_frame, text="—", font=("Arial", 10))
        self.name_label.pack(anchor="w", pady=(0, 10))
        
        # Фотография пользователя
        ttk.Label(info_frame, text="Фотография:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.photo_label = ttk.Label(info_frame, text="Нет фото", background="lightgray", width=20, height=10)
        self.photo_label.pack(pady=10)
        
        # Кнопка обновления кодировок
        ttk.Button(info_frame, text="Обновить кодировки", command=self.load_encodings).pack(pady=10)
    
    def load_encodings(self):
        # Загрузка кодировок лиц из файла
        try:
            if os.path.exists("encodings.pickle"):
                with open("encodings.pickle", "rb") as f:
                    self.known_encodings, self.known_user_ids = pickle.load(f)
                print(f"Загружено кодировок: {len(self.known_encodings)}")
            else:
                print("Файл кодировок не найден. Создайте кодировки в управлении пользователями.")
                self.known_encodings = []
                self.known_user_ids = []
        except Exception as e:
            print(f"Ошибка загрузки кодировок: {e}")
            self.known_encodings = []
            self.known_user_ids = []
    
    def start_camera(self):
        # Запуск камеры
        try:
            self.cap = cv2.VideoCapture(0)  # Используем первую доступную камеру
            if not self.cap.isOpened():
                messagebox.showerror("Ошибка", "Не удалось подключиться к камере!")
                return
            
            # Настройка камеры
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            self.is_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            # Запуск цикла обработки кадров
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
        
        # Очистка видео метки
        self.video_label.config(image="", text="Камера остановлена")
        
        # Сброс информации о пользователе
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
        
        # Отражаем кадр по горизонтали (как в зеркале)
        frame = cv2.flip(frame, 1)
        
        # Уменьшаем размер кадра для ускорения распознавания
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Поиск лиц на кадре
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        # Обработка найденных лиц
        for face_encoding, face_location in zip(face_encodings, face_locations):
            # Сравнение с известными лицами
            matches = face_recognition.compare_faces(self.known_encodings, face_encoding)
            face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
            
            name = "Неизвестный"
            user_id = None
            
            # Если найдено совпадение
            if True in matches:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    user_id = self.known_user_ids[best_match_index]
                    
                    # Получаем информацию о пользователе из БД
                    user_data = self.db.get_user(user_id)
                    if user_data:
                        name = user_data[2]  # Имя пользователя
                        self.update_user_info(user_data)
                    else:
                        self.reset_user_info()
            else:
                self.reset_user_info()
            
            # Рисуем рамку вокруг лица
            top, right, bottom, left = face_location
            # Масштабируем координаты обратно к оригинальному размеру
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Цвет рамки: зеленый для известных, красный для неизвестных
            color = (0, 255, 0) if user_id else (0, 0, 255)
            
            # Рисуем рамку
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Рисуем имя под рамкой
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        # Если лица не найдены, сбрасываем информацию
        if not face_locations:
            self.reset_user_info()
        
        # Конвертируем кадр для отображения в Tkinter
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        photo = ImageTk.PhotoImage(pil_image)
        
        # Обновляем видео метку
        self.video_label.config(image=photo, text="")
        self.video_label.image = photo  # Сохраняем ссылку
        
        # Планируем следующий кадр
        self.root.after(30, self.process_frame)
    
    def update_user_info(self, user_data):
        # Обновление информации о распознанном пользователе
        # user_data = (id, user_id, name, photo_path)
        user_id = user_data[1]
        name = user_data[2]
        photo_path = user_data[3]
        
        # Обновляем статус
        self.status_label.config(text="Пользователь распознан", foreground="green")
        
        # Обновляем информацию
        self.user_id_label.config(text=user_id)
        self.name_label.config(text=name)
        
        # Загружаем и отображаем фотографию пользователя
        if photo_path and os.path.exists(photo_path):
            try:
                # Загружаем изображение
                pil_image = Image.open(photo_path)
                # Изменяем размер под наш интерфейс
                pil_image = pil_image.resize((150, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(pil_image)
                
                # Отображаем фото
                self.photo_label.config(image=photo, text="")
                self.photo_label.image = photo  # Сохраняем ссылку
            except Exception as e:
                print(f"Ошибка загрузки фото: {e}")
                self.photo_label.config(image="", text="Ошибка загрузки фото")
        else:
            self.photo_label.config(image="", text="Фото не найдено")
    
    def reset_user_info(self):
        # Сброс информации о пользователе
        self.status_label.config(text="Ожидание...", foreground="black")
        self.user_id_label.config(text="—")
        self.name_label.config(text="—")
        self.photo_label.config(image="", text="Нет фото")
    
    def on_closing(self):
        # Обработка закрытия окна
        self.stop_camera()
        self.root.destroy()

# Запуск приложения распознавания лиц
if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
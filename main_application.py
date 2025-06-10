import tkinter as tk
from tkinter import ttk
from user_management import UserManagement
from face_recognition_app import FaceRecognitionApp

class MainApplication:
    def __init__(self):
        # Создание главного окна
        self.root = tk.Tk()
        self.root.title("Система распознавания лиц - Главное меню")
        self.root.geometry("400x300")
        
        # Центрируем окно на экране
        self.center_window()
        
        self.setup_ui()
    
    def center_window(self):
        # Центрирование окна на экране
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        # Создание интерфейса главного меню
        
        # Заголовок
        title_label = tk.Label(
            self.root, 
            text="Система распознавания лиц", 
            font=("Arial", 16, "bold"),
            pady=20
        )
        title_label.pack()
        
        # Описание
        desc_label = tk.Label(
            self.root,
            text="Выберите действие:",
            font=("Arial", 12),
            pady=10
        )
        desc_label.pack()
        
        # Фрейм для кнопок
        button_frame = tk.Frame(self.root)
        button_frame.pack(expand=True)
        
        # Кнопка управления пользователями
        user_mgmt_button = tk.Button(
            button_frame,
            text="Управление пользователями",
            font=("Arial", 12),
            width=25,
            height=2,
            command=self.open_user_management
        )
        user_mgmt_button.pack(pady=10)
        
        # Кнопка распознавания лиц
        face_recognition_button = tk.Button(
            button_frame,
            text="Распознавание лиц",
            font=("Arial", 12),
            width=25,
            height=2,
            command=self.open_face_recognition
        )
        face_recognition_button.pack(pady=10)
        
        # Кнопка выхода
        exit_button = tk.Button(
            button_frame,
            text="Выход",
            font=("Arial", 12),
            width=25,
            height=2,
            command=self.root.quit
        )
        exit_button.pack(pady=10)
        
        # Информация внизу
        info_label = tk.Label(
            self.root,
            text="ВКР - Автоматизированная система распознавания лиц",
            font=("Arial", 10),
            fg="gray"
        )
        info_label.pack(side="bottom", pady=10)
    
    def open_user_management(self):
        # Открытие окна управления пользователями
        user_window = tk.Toplevel(self.root)
        UserManagement(user_window)
    
    def open_face_recognition(self):
        # Открытие окна распознавания лиц
        recognition_window = tk.Toplevel(self.root)
        FaceRecognitionApp(recognition_window)
    
    def run(self):
        # Запуск главного цикла приложения
        self.root.mainloop()

# Точка входа в программу
if __name__ == "__main__":
    app = MainApplication()
    app.run()
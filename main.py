import tkinter as tk
from modern_face_recognition import ModernFaceRecognitionApp

class MainApplication:
    def __init__(self):
        # Создание главного окна
        self.root = tk.Tk()
        self.root.withdraw()  # Скрываем главное меню
        
        # Сразу запускаем современное приложение
        self.modern_app = ModernFaceRecognitionApp(self.root)
    
    def run(self):
        # Запуск главного цикла приложения
        self.root.mainloop()

# Точка входа в программу
if __name__ == "__main__":
    # Можно запускать напрямую современное приложение
    root = tk.Tk()
    app = ModernFaceRecognitionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
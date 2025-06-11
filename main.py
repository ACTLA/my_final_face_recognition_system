# main_with_audit.py
# Модифицированная версия main.py с интегрированной системой аудита

import tkinter as tk
from modern_face_recognition import ModernFaceRecognitionApp
from audit_system import AuditIntegration

class MainApplication:
    def __init__(self):
        # Создание главного окна
        self.root = tk.Tk()
        self.root.withdraw()  # Скрываем главное меню
        
        # Сразу запускаем современное приложение
        self.modern_app = ModernFaceRecognitionApp(self.root)
        
        # 📊 ИНТЕГРИРУЕМ СИСТЕМУ АУДИТА 📊
        self.modern_app = AuditIntegration.integrate_with_app(self.modern_app)
    
    def run(self):
        # Запуск главного цикла приложения
        self.root.mainloop()

# Точка входа в программу с системой аудита
if __name__ == "__main__":
    print("🚀 Запуск системы распознавания лиц с аудитом...")
    print("=" * 50)
    print("📊 Функции аудита:")
    print("   ✅ Логирование всех попыток распознавания")
    print("   ✅ Аудит действий с пользователями")
    print("   ✅ Статистика в реальном времени")
    print("   ✅ Графики и аналитика")
    print("   ✅ Экспорт отчетов в CSV")
    print("=" * 50)
    
    # Альтернативный способ запуска (более простой)
    root = tk.Tk()
    app = ModernFaceRecognitionApp(root)
    
    # 📊 ИНТЕГРАЦИЯ СИСТЕМЫ АУДИТА 📊
    app = AuditIntegration.integrate_with_app(app)
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
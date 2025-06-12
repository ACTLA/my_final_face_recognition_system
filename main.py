# Обновленный main.py с улучшенной обработкой импортов
import tkinter as tk
import sys
import os

def main():
    """Главная функция запуска приложения"""
    print("🎯 СИСТЕМА РАСПОЗНАВАНИЯ ЛИЦ С АУДИТОМ БЕЗОПАСНОСТИ")
    print("=" * 60)
    print("📋 ВКР: Автоматизированная система распознавания лиц")
    print("👨‍🎓 Студент 4 курса направления 'Информационная безопасность'")
    print("🛡️ Профиль: Безопасность компьютерных систем")
    print("=" * 60)
    
    # Проверка зависимостей
    if not check_dependencies():
        input("\nНажмите Enter для выхода...")
        return
    
    try:
        # Импорт после проверки зависимостей
        from gui.main_application import FaceRecognitionApp
        from audit.integration import AuditIntegration
        
        print("🔧 Инициализация приложения...")
        
        # Создание приложения
        root = tk.Tk()
        app = FaceRecognitionApp(root)
        
        # Интеграция системы аудита
        print("📊 Интеграция системы аудита...")
        app = AuditIntegration.integrate_with_app(app)
        
        # Настройка закрытия
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        print("✅ Система успешно запущена!")
        print("🎯 Готова к работе!")
        print("-" * 60)
        
        # Запуск приложения
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ Ошибка импорта модулей: {e}")
        print("🔍 Убедитесь, что все файлы находятся в правильных папках")
        input("Нажмите Enter для выхода...")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        input("Нажмите Enter для выхода...")

def check_dependencies():
    """Проверка зависимостей"""
    print("🔍 Проверка зависимостей...")
    
    dependencies = [
        ('tkinter', 'Встроенная библиотека GUI'),
        ('cv2', 'OpenCV для работы с камерой'), 
        ('face_recognition', 'Библиотека распознавания лиц'),
        ('PIL', 'Pillow для работы с изображениями'),
        ('numpy', 'NumPy для математических операций')
    ]
    
    missing = []
    
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"   ✅ {module} - {description}")
        except ImportError:
            print(f"   ❌ {module} - {description} (НЕ НАЙДЕНО)")
            missing.append(module)
    
    if missing:
        print("\n🚨 Для установки отсутствующих зависимостей выполните:")
        print("   pip install -r requirements.txt")
        print("\nИли установите по отдельности:")
        for module in missing:
            if module == 'cv2':
                print(f"   pip install opencv-python")
            elif module == 'PIL':
                print(f"   pip install Pillow")  
            else:
                print(f"   pip install {module}")
        return False
    
    print("✅ Все зависимости установлены!")
    return True

if __name__ == "__main__":
    main()
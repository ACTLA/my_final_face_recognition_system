# main.py - Главный файл запуска системы распознавания лиц
import tkinter as tk
import sys
import os

def main():
    """Главная функция запуска приложения"""
    # Выводим информацию о системе
    print("🎯 СИСТЕМА РАСПОЗНАВАНИЯ ЛИЦ С АУДИТОМ БЕЗОПАСНОСТИ")
    print("=" * 60)
    print("📋 ВКР: Автоматизированная система распознавания лиц")
    print("👨‍🎓 Студент 4 курса направления 'Информационная безопасность'")
    print("🛡️ Профиль: Безопасность компьютерных систем")
    print("=" * 60)
    
    # Проверяем наличие всех необходимых зависимостей
    if not check_dependencies():
        input("\nНажмите Enter для выхода...")
        return
    
    try:
        # Импортируем модули после проверки зависимостей
        from gui.main_application import FaceRecognitionApp
        from audit.integration import AuditIntegration
        
        print("🔧 Инициализация приложения...")
        
        # Создаем основное окно и приложение
        root = tk.Tk()
        app = FaceRecognitionApp(root)
        
        # Интегрируем систему аудита с приложением
        print("📊 Интеграция системы аудита...")
        app = AuditIntegration.integrate_with_app(app)
        
        # Настраиваем обработчик закрытия окна
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        print("✅ Система успешно запущена!")
        print("🎯 Готова к работе!")
        print("-" * 60)
        
        # Запускаем главный цикл приложения
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ Ошибка импорта модулей: {e}")
        print("🔍 Убедитесь, что все файлы находятся в правильных папках")
        input("Нажмите Enter для выхода...")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        input("Нажмите Enter для выхода...")

def check_dependencies():
    """Проверка наличия всех необходимых зависимостей"""
    print("🔍 Проверка зависимостей...")
    
    # Список необходимых модулей и их описания
    dependencies = [
        ('tkinter', 'Встроенная библиотека GUI'),
        ('cv2', 'OpenCV для работы с камерой'), 
        ('face_recognition', 'Библиотека распознавания лиц'),
        ('PIL', 'Pillow для работы с изображениями'),
        ('numpy', 'NumPy для математических операций')
    ]
    
    missing = []  # Список отсутствующих модулей
    
    # Проверяем каждый модуль
    for module, description in dependencies:
        try:
            # Пытаемся импортировать модуль
            __import__(module)
            print(f"   ✅ {module} - {description}")
        except ImportError:
            # Модуль не найден
            print(f"   ❌ {module} - {description} (НЕ НАЙДЕНО)")
            missing.append(module)
    
    # Если есть отсутствующие модули, показываем инструкции по установке
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

# Запускаем приложение только при прямом выполнении файла
if __name__ == "__main__":
    main()
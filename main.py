# main.py
# Главный файл запуска системы распознавания лиц с интегрированной системой аудита

import tkinter as tk
from modern_face_recognition import ModernFaceRecognitionApp
from audit_system import AuditIntegration

def main():
    """Главная функция запуска приложения"""
    
    print("🚀 Запуск системы распознавания лиц с расширенным аудитом...")
    print("=" * 60)
    print("📊 Новые функции аудита и безопасности:")
    print("   ✅ Логирование всех попыток распознавания")
    print("   ✅ Аудит действий с пользователями:")
    print("      ➕ Добавление пользователей")
    print("      🗑 Удаление пользователей") 
    print("      🔄 Обновление фотографий")
    print("   ✅ Контроль задержек распознавания (3 сек)")
    print("   ✅ Автоочистка информации (2 сек)")
    print("   ✅ Статистика в реальном времени")
    print("   ✅ Цветовые индикаторы состояний")
    print("   ✅ Экспорт отчетов в CSV")
    print("=" * 60)
    
    try:
        # Создание главного окна
        root = tk.Tk()
        
        # Настройка иконки окна (если есть)
        try:
            # root.iconbitmap('icon.ico')  # Раскомментируйте если есть иконка
            pass
        except:
            pass
        
        # Создание основного приложения
        print("🔧 Инициализация основного приложения...")
        app = ModernFaceRecognitionApp(root)
        
        # 📊 ИНТЕГРАЦИЯ СИСТЕМЫ АУДИТА 📊
        print("📊 Интеграция системы аудита...")
        app = AuditIntegration.integrate_with_app(app)
        
        # Настройка обработчика закрытия окна
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        print("✅ Система успешно запущена!")
        print("🎯 Готова к работе - переходите на вкладку 'Распознавание лиц'")
        print("📋 Журнал безопасности доступен на вкладке 'Журнал безопасности'")
        print("-" * 60)
        
        # Запуск главного цикла приложения
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Ошибка запуска приложения: {e}")
        print("🔍 Проверьте:")
        print("   - Установлены ли все зависимости (face_recognition, opencv-python, PIL)")
        print("   - Подключена ли камера к компьютеру")
        print("   - Доступны ли права на запись в текущую папку")
        input("Нажмите Enter для выхода...")

def check_dependencies():
    """Проверка наличия необходимых зависимостей"""
    print("🔍 Проверка зависимостей...")
    
    dependencies = {
        'tkinter': 'Встроенная библиотека GUI',
        'cv2': 'OpenCV для работы с камерой', 
        'face_recognition': 'Библиотека распознавания лиц',
        'PIL': 'Pillow для работы с изображениями',
        'numpy': 'NumPy для математических операций',
        'sqlite3': 'Встроенная база данных'
    }
    
    missing = []
    
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"   ✅ {module} - {description}")
        except ImportError:
            print(f"   ❌ {module} - {description} (НЕ НАЙДЕНО)")
            missing.append(module)
    
    if missing:
        print("\n🚨 Отсутствующие зависимости:")
        for module in missing:
            if module == 'cv2':
                print(f"   pip install opencv-python")
            elif module == 'PIL':
                print(f"   pip install Pillow")  
            else:
                print(f"   pip install {module}")
        print("\nУстановите отсутствующие зависимости и перезапустите программу.")
        return False
    
    print("✅ Все зависимости установлены!")
    return True

if __name__ == "__main__":
    print("🎯 СИСТЕМА РАСПОЗНАВАНИЯ ЛИЦ С АУДИТОМ БЕЗОПАСНОСТИ")
    print("=" * 60)
    print("📋 ВКР: Автоматизированная система распознавания лиц")
    print("👨‍🎓 Студент 4 курса направления 'Информационная безопасность'")
    print("🛡️ Профиль: Безопасность компьютерных систем")
    print("=" * 60)
    
    # Проверка зависимостей перед запуском
    if check_dependencies():
        print("")
        main()
    else:
        input("\nНажмите Enter для выхода...")

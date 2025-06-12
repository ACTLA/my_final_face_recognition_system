# main.py
"""
Главный модуль запуска системы распознавания лиц
Автор: Студент 4 курса ОмГУ им. Ф.М. Достоевского
ВКР: Автоматизированная система распознавания лиц
Направление: 10.03.01 «Информационная безопасность»
Профиль: «Безопасность компьютерных систем»
Учебное заведение: ОмГУ им. Ф.М. Достоевского, факультет ЦТК

Описание:
Точка входа в систему биометрической идентификации на основе
технологий распознавания лиц с интегрированной системой аудита
безопасности. Обеспечивает полную инициализацию всех компонентов
системы и graceful handling критических ошибок.

Архитектурные компоненты:
- Система управления зависимостями и их валидации
- Comprehensive error handling для production ready решения
- Graceful shutdown механизмы для корректного завершения
- Integration layer для audit системы безопасности
- User-friendly интерфейс для технических и нетехнических пользователей

Системные требования:
- Python 3.12+
- OpenCV для компьютерного зрения
- face_recognition для биометрической идентификации
- tkinter для графического интерфейса
- SQLite для persistence слоя
- PIL/Pillow для обработки изображений
"""

import tkinter as tk  # Основная библиотека графического интерфейса
import sys  # Системные функции для управления выполнением
import os  # Операции с операционной системой и файлами


def main():
    """
    Главная функция запуска системы биометрической идентификации
    
    Выполняет полную инициализацию системы распознавания лиц:
    1. Отображение информации о системе и авторе
    2. Валидация всех системных зависимостей
    3. Инициализация core компонентов приложения
    4. Интеграция системы аудита безопасности
    5. Настройка graceful shutdown механизмов
    6. Запуск главного цикла пользовательского интерфейса
    
    Error Handling:
    - Comprehensive валидация зависимостей перед запуском
    - Graceful degradation при отсутствии опциональных компонентов
    - User-friendly сообщения об ошибках с инструкциями по устранению
    - Safe shutdown при критических ошибках
    
    Returns:
        None
    """
    # Отображение заголовка системы и информации об авторе
    display_system_header()
    
    # Критически важная валидация всех зависимостей перед запуском
    if not validate_system_dependencies():
        # Graceful exit при отсутствии критических зависимостей
        input("\n⏸️  Нажмите Enter для завершения...")
        return
    
    try:
        print("🔧 Инициализация компонентов системы...")
        
        # Динамические импорты после валидации зависимостей для избежания ImportError
        from gui.main_application import FaceRecognitionSystem
        from audit.integration import SecurityAuditIntegration
        
        print("🎯 Создание главного приложения...")
        
        # Инициализация корневого окна tkinter
        root = tk.Tk()
        
        # Создание экземпляра системы распознавания лиц
        face_recognition_app = FaceRecognitionSystem(root)
        
        print("🛡️  Интеграция системы аудита безопасности...")
        
        # Интеграция comprehensive системы аудита безопасности
        face_recognition_app = SecurityAuditIntegration.integrate_comprehensive_audit_system(
            face_recognition_app
        )
        
        # Настройка обработчика корректного завершения работы приложения
        root.protocol("WM_DELETE_WINDOW", face_recognition_app.handle_application_shutdown)
        
        print("✅ Система успешно инициализирована!")
        print("🚀 Запуск пользовательского интерфейса...")
        print("-" * 70)
        
        # Запуск главного цикла GUI приложения
        root.mainloop()
        
    except ImportError as e:
        # Обработка ошибок импорта модулей системы
        print(f"❌ Ошибка импорта компонентов системы: {e}")
        print("🔍 Проверьте целостность файлов проекта:")
        print("   📁 Убедитесь, что все модули находятся в правильных папках")
        print("   🔗 Проверьте корректность путей импорта")
        print("   📋 Убедитесь в наличии всех __init__.py файлов")
        input("\n⏸️  Нажмите Enter для завершения...")
        
    except Exception as e:
        # Обработка всех прочих критических ошибок запуска
        print(f"❌ Критическая ошибка инициализации системы: {e}")
        print("🛠️  Возможные причины:")
        print("   💾 Недостаточно прав доступа для создания файлов БД")
        print("   📸 Проблемы с доступом к веб-камере")
        print("   🖥️  Ошибки инициализации графического интерфейса")
        input("\n⏸️  Нажмите Enter для завершения...")


def display_system_header():
    """
    Отображение заголовка системы с информацией о проекте и авторе
    
    Выводит comprehensive информацию о системе, авторе и назначении
    для идентификации и документирования запуска системы.
    """
    print("🎯 СИСТЕМА БИОМЕТРИЧЕСКОЙ ИДЕНТИФИКАЦИИ НА ОСНОВЕ РАСПОЗНАВАНИЯ ЛИЦ")
    print("=" * 80)
    print("📋 ВКР: Автоматизированная система распознавания лиц")
    print("🎓 Студент 4 курса очной формы обучения")
    print("📚 Направление: 10.03.01 «Информационная безопасность»")
    print("🎯 Профиль: «Безопасность компьютерных систем»")
    print("🏛️  ОмГУ им. Ф.М. Достоевского, факультет ЦТК")
    print("📅 Год защиты: 2025")
    print("=" * 80)


def validate_system_dependencies():
    """
    Валидация всех системных зависимостей перед запуском
    
    Проверяет наличие и доступность всех критически важных библиотек
    и компонентов, необходимых для корректной работы системы.
    
    Returns:
        bool: True если все зависимости доступны, False при критических ошибках
        
    Validation categories:
    - Core Python libraries (встроенные модули)
    - Computer Vision dependencies (OpenCV, face_recognition)
    - GUI framework dependencies (tkinter, PIL)
    - Mathematical and data processing libraries (numpy, etc.)
    """
    print("🔍 Валидация системных зависимостей...")
    
    # Определение критически важных зависимостей с описаниями
    critical_dependencies = [
        ('tkinter', 'Встроенная библиотека графического интерфейса'),
        ('cv2', 'OpenCV для компьютерного зрения и работы с камерой'), 
        ('face_recognition', 'Библиотека биометрического распознавания лиц'),
        ('PIL', 'Pillow для обработки и отображения изображений'),
        ('numpy', 'NumPy для математических операций с массивами')
    ]
    
    # Список отсутствующих критических зависимостей
    missing_dependencies = []
    
    # Проверка каждой зависимости с detailed logging
    for module_name, description in critical_dependencies:
        try:
            # Попытка импорта модуля
            __import__(module_name)
            print(f"   ✅ {module_name} - {description}")
        except ImportError:
            # Логирование отсутствующей зависимости
            print(f"   ❌ {module_name} - {description} (НЕ НАЙДЕНО)")
            missing_dependencies.append(module_name)
    
    # Обработка результатов валидации
    if missing_dependencies:
        print(f"\n🚨 Обнаружены отсутствующие критические зависимости: {len(missing_dependencies)}")
        display_dependency_installation_instructions(missing_dependencies)
        return False
    
    print("✅ Все системные зависимости успешно проверены!")
    return True


def display_dependency_installation_instructions(missing_dependencies):
    """
    Отображение инструкций по установке отсутствующих зависимостей
    
    Предоставляет пользователю clear и actionable инструкции для
    установки всех отсутствующих компонентов системы.
    
    Args:
        missing_dependencies (list): Список отсутствующих модулей
    """
    print("\n🛠️  ИНСТРУКЦИИ ПО УСТАНОВКЕ ЗАВИСИМОСТЕЙ:")
    print("-" * 50)
    
    print("📦 Рекомендуемый способ (requirements.txt):")
    print("   pip install -r requirements.txt")
    
    print("\n📦 Альтернативная установка по отдельности:")
    
    # Mapping модулей к pip package names
    pip_package_mapping = {
        'cv2': 'opencv-python',
        'PIL': 'Pillow',
        'face_recognition': 'face_recognition',
        'numpy': 'numpy',
        'tkinter': 'обычно встроен в Python (переустановите Python)'
    }
    
    # Отображение команд установки для каждой отсутствующей зависимости
    for module in missing_dependencies:
        package_name = pip_package_mapping.get(module, module)
        if module == 'tkinter':
            print(f"   ⚠️  {module}: {package_name}")
        else:
            print(f"   pip install {package_name}")
    
    print("\n💡 Дополнительные рекомендации:")
    print("   🐍 Убедитесь, что используете Python 3.12+")
    print("   🔄 Обновите pip: python -m pip install --upgrade pip")
    print("   🌐 При проблемах с сетью используйте: pip install --user")
    print("   🪟 Windows: Возможно потребуется Visual Studio Build Tools")


if __name__ == "__main__":
    """
    Точка входа в программу при прямом запуске скрипта
    
    Обеспечивает корректный запуск системы только при выполнении
    данного файла как основного модуля (не при импорте).
    """
    main()
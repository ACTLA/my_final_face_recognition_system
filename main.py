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
системы и корректную обработку критических ошибок.

Архитектурные компоненты:
- Система управления зависимостями и их проверки
- Всеобъемлющая обработка ошибок для готового к производству решения
- Механизмы корректного завершения для правильного завершения работы
- Слой интеграции для системы аудита безопасности
- Удобный для пользователя интерфейс для технических и нетехнических пользователей

Системные требования:
- Python 3.12+
- OpenCV для компьютерного зрения
- face_recognition для биометрической идентификации
- tkinter для графического интерфейса
- SQLite для слоя постоянства данных
- PIL/Pillow для обработки изображений
"""

import tkinter as tk  # Основная библиотека графического интерфейса
import sys  # Системные функции для управления выполнением
import os  # Операции с операционной системой и файлами
import time  # Библиотека для измерения времени выполнения

# Добавленный импорт для мониторинга памяти
try:
    import psutil  # Для мониторинга системных ресурсов
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil не установлен. Мониторинг памяти недоступен.")
    print("   Для установки: pip install psutil")


def get_memory_usage():
    """
    Получение текущего потребления памяти процессом
    
    Возвращает:
        dict: Словарь с информацией о памяти в МБ
    """
    if not PSUTIL_AVAILABLE:
        return {'rss': 0, 'vms': 0, 'percent': 0}
    
    try:
        # Получаем информацию о текущем процессе
        process = psutil.Process(os.getpid())
        
        # Получаем информацию о памяти
        memory_info = process.memory_info()
        
        # Конвертируем в МБ
        memory_data = {
            'rss': round(memory_info.rss / 1024 / 1024, 2),  # Резидентная память (RAM)
            'vms': round(memory_info.vms / 1024 / 1024, 2),  # Виртуальная память
            'percent': round(process.memory_percent(), 2)     # Процент от общей памяти системы
        }
        
        return memory_data
    except Exception as e:
        print(f"Ошибка получения информации о памяти: {e}")
        return {'rss': 0, 'vms': 0, 'percent': 0}


def display_memory_stats(stage_name, memory_before, memory_after):
    """
    Отображение статистики использования памяти для этапа
    
    Аргументы:
        stage_name (str): Название этапа
        memory_before (dict): Память до этапа
        memory_after (dict): Память после этапа
    """
    if not PSUTIL_AVAILABLE:
        return
    
    memory_diff = memory_after['rss'] - memory_before['rss']
    print(f"   💾 Память после {stage_name}: {memory_after['rss']} МБ (изменение: {memory_diff:+.2f} МБ)")


def measure_loading_performance():
    """
    Измерение производительности загрузки системы с детализацией по этапам
    
    Выполняет пошаговое измерение времени инициализации всех компонентов
    системы для анализа производительности и выявления узких мест.
    
    Возвращает:
        tuple: (словарь_времен, словарь_памяти, root_окно, экземпляр_приложения) или None при ошибке
    """
    times = {}
    memory_stats = {}
    
    # Измерение памяти в начале
    initial_memory = get_memory_usage()
    memory_stats['initial'] = initial_memory
    if PSUTIL_AVAILABLE:
        print(f"🔋 Начальное потребление памяти: {initial_memory['rss']} МБ")
    print("📊 Начало измерения производительности загрузки...")
    
    # Этап 1: Проверка зависимостей и отображение заголовка
    start = time.time()
    memory_before = get_memory_usage()
    
    # Отображение заголовка системы и информации об авторе
    display_system_header()
    
    # Критически важная проверка всех зависимостей перед запуском
    if not validate_system_dependencies():
        # Корректный выход при отсутствии критических зависимостей
        print("❌ Не удалось пройти проверку зависимостей")
        return None
    
    times['dependencies'] = time.time() - start
    memory_after = get_memory_usage()
    memory_stats['dependencies'] = memory_after
    
    print(f"   ✅ Проверка зависимостей: {times['dependencies']:.3f} сек")
    display_memory_stats("проверки зависимостей", memory_before, memory_after)
    
    # Этап 2: Импорт основных модулей системы
    start = time.time()
    memory_before = get_memory_usage()
    print("🔧 Инициализация компонентов системы...")
    
    # Динамические импорты после проверки зависимостей для избежания ошибок импорта
    from gui.main_application import FaceRecognitionSystem
    from audit.integration import SecurityAuditIntegration
    
    times['imports'] = time.time() - start
    memory_after = get_memory_usage()
    memory_stats['imports'] = memory_after
    
    print(f"   ✅ Импорт модулей: {times['imports']:.3f} сек")
    display_memory_stats("импорта модулей", memory_before, memory_after)
    
    # Этап 3: Создание главного приложения
    start = time.time()
    memory_before = get_memory_usage()
    print("🎯 Создание главного приложения...")
    
    # Инициализация корневого окна tkinter
    root = tk.Tk()
    
    # Создание экземпляра системы распознавания лиц
    face_recognition_app = FaceRecognitionSystem(root)
    
    times['app_creation'] = time.time() - start
    memory_after = get_memory_usage()
    memory_stats['app_creation'] = memory_after
    
    print(f"   ✅ Создание приложения: {times['app_creation']:.3f} сек")
    display_memory_stats("создания приложения", memory_before, memory_after)
    
    # Этап 4: Интеграция системы аудита безопасности
    start = time.time()
    memory_before = get_memory_usage()
    print("🛡️  Интеграция системы аудита безопасности...")
    
    # Интеграция всеобъемлющей системы аудита безопасности
    face_recognition_app = SecurityAuditIntegration.integrate_comprehensive_audit_system(
        face_recognition_app
    )
    
    times['audit_integration'] = time.time() - start
    memory_after = get_memory_usage()
    memory_stats['audit_integration'] = memory_after
    
    print(f"   ✅ Интеграция аудита: {times['audit_integration']:.3f} сек")
    display_memory_stats("интеграции аудита", memory_before, memory_after)
    
    return times, memory_stats, root, face_recognition_app


def main():
    """
    Главная функция запуска системы биометрической идентификации
    
    Выполняет полную инициализацию системы распознавания лиц:
    1. Отображение информации о системе и авторе
    2. Проверка всех системных зависимостей
    3. Инициализация основных компонентов приложения
    4. Интеграция системы аудита безопасности
    5. Настройка механизмов корректного завершения
    6. Запуск главного цикла пользовательского интерфейса
    
    Обработка ошибок:
    - Всеобъемлющая проверка зависимостей перед запуском
    - Корректное ухудшение при отсутствии дополнительных компонентов
    - Удобные для пользователя сообщения об ошибках с инструкциями по устранению
    - Безопасное завершение при критических ошибках
    
    Возвращает:
        None
    """
    # Общий таймер загрузки системы для измерения производительности
    total_start_time = time.time()
    
    print("📊 РЕЖИМ ИЗМЕРЕНИЯ ПРОИЗВОДИТЕЛЬНОСТИ И ПАМЯТИ")
    print("=" * 80)
    
    try:
        # Выполнение измерений по этапам
        result = measure_loading_performance()
        if result is None:
            # Корректный выход при отсутствии критических зависимостей
            input("\n⏸️  Нажмите Enter для завершения...")
            return
        
        times, memory_stats, root, face_recognition_app = result
        
        # Настройка обработчика корректного завершения работы приложения
        root.protocol("WM_DELETE_WINDOW", face_recognition_app.handle_application_shutdown)
        
        # Вычисление общего времени загрузки
        total_time = time.time() - total_start_time
        final_memory = get_memory_usage()
        
        # Вывод детальной статистики производительности
        print("\n" + "=" * 70)
        print("📈 ДЕТАЛЬНАЯ СТАТИСТИКА ПРОИЗВОДИТЕЛЬНОСТИ")
        print("=" * 70)
        print(f"📋 Проверка зависимостей:     {times['dependencies']:.3f} сек")
        print(f"📦 Импорт модулей:            {times['imports']:.3f} сек")
        print(f"🎯 Создание приложения:       {times['app_creation']:.3f} сек")
        print(f"🛡️  Интеграция аудита:        {times['audit_integration']:.3f} сек")
        print("-" * 70)
        print(f"🏁 ОБЩЕЕ ВРЕМЯ ЗАГРУЗКИ:      {total_time:.3f} СЕКУНД")
        
        # Статистика памяти (только если psutil доступен)
        if PSUTIL_AVAILABLE:
            print("\n" + "=" * 70)
            print("💾 СТАТИСТИКА ПОТРЕБЛЕНИЯ ПАМЯТИ")
            print("=" * 70)
            print(f"🔋 Начальная память:          {memory_stats['initial']['rss']} МБ")
            print(f"📋 После проверки зависимостей: {memory_stats['dependencies']['rss']} МБ")
            print(f"📦 После импорта модулей:     {memory_stats['imports']['rss']} МБ")
            print(f"🎯 После создания приложения: {memory_stats['app_creation']['rss']} МБ")
            print(f"🛡️  После интеграции аудита:  {memory_stats['audit_integration']['rss']} МБ")
            print("-" * 70)
            print(f"💿 ИТОГОВОЕ ПОТРЕБЛЕНИЕ:      {final_memory['rss']} МБ")
            print(f"📊 ОБЩИЙ ПРИРОСТ ПАМЯТИ:      {final_memory['rss'] - memory_stats['initial']['rss']:.2f} МБ")
            print(f"🔄 ПРОЦЕНТ ОТ СИСТЕМНОЙ ПАМЯТИ: {final_memory['percent']:.2f}%")
        
        print("=" * 70)
        
        # Анализ производительности
        print("\n📊 АНАЛИЗ ПРОИЗВОДИТЕЛЬНОСТИ:")
        slowest_stage = max(times.items(), key=lambda x: x[1])
        print(f"   🐌 Самый медленный этап: {slowest_stage[0]} ({slowest_stage[1]:.3f} сек)")
        
        fastest_stage = min(times.items(), key=lambda x: x[1])
        print(f"   ⚡ Самый быстрый этап: {fastest_stage[0]} ({fastest_stage[1]:.3f} сек)")
        
        # Анализ памяти (только если psutil доступен)
        if PSUTIL_AVAILABLE:
            memory_growth = {}
            prev_memory = memory_stats['initial']['rss']
            for stage, memory_info in list(memory_stats.items())[1:]:
                growth = memory_info['rss'] - prev_memory
                memory_growth[stage] = growth
                prev_memory = memory_info['rss']
            
            largest_memory_growth = max(memory_growth.items(), key=lambda x: x[1])
            print(f"   🐘 Наибольший прирост памяти: {largest_memory_growth[0]} (+{largest_memory_growth[1]:.2f} МБ)")
        
        # Процентное соотношение времени по этапам
        print(f"\n📈 РАСПРЕДЕЛЕНИЕ ВРЕМЕНИ:")
        for stage, stage_time in times.items():
            percentage = (stage_time / total_time) * 100
            print(f"   {stage}: {percentage:.1f}%")
        
        print("\n✅ Система успешно инициализирована!")
        print("🚀 Запуск пользовательского интерфейса...")
        print("-" * 70)
        
        # Запуск главного цикла графического интерфейса приложения
        root.mainloop()
        
    except ImportError as e:
        # Обработка ошибок импорта модулей системы
        total_time = time.time() - total_start_time
        print(f"❌ Ошибка импорта компонентов системы: {e}")
        print(f"⏱️  Время до ошибки: {total_time:.3f} секунд")
        print("🔍 Проверьте целостность файлов проекта:")
        print("   📁 Убедитесь, что все модули находятся в правильных папках")
        print("   🔗 Проверьте корректность путей импорта")
        print("   📋 Убедитесь в наличии всех файлов __init__.py")
        input("\n⏸️  Нажмите Enter для завершения...")
        
    except Exception as e:
        # Обработка всех прочих критических ошибок запуска
        total_time = time.time() - total_start_time
        print(f"❌ Критическая ошибка инициализации системы: {e}")
        print(f"⏱️  Время до ошибки: {total_time:.3f} секунд")
        print("🛠️  Возможные причины:")
        print("   💾 Недостаточно прав доступа для создания файлов БД")
        print("   📸 Проблемы с доступом к веб-камере")
        print("   🖥️  Ошибки инициализации графического интерфейса")
        input("\n⏸️  Нажмите Enter для завершения...")


def display_system_header():
    """
    Отображение заголовка системы с информацией о проекте и авторе
    
    Выводит всеобъемлющую информацию о системе, авторе и назначении
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
    Проверка всех системных зависимостей перед запуском
    
    Проверяет наличие и доступность всех критически важных библиотек
    и компонентов, необходимых для корректной работы системы.
    
    Возвращает:
        bool: True если все зависимости доступны, False при критических ошибках
        
    Категории проверки:
    - Основные библиотеки Python (встроенные модули)
    - Зависимости компьютерного зрения (OpenCV, face_recognition)
    - Зависимости платформы графического интерфейса (tkinter, PIL)
    - Математические библиотеки и библиотеки обработки данных (numpy, и т.д.)
    """
    print("🔍 Проверка системных зависимостей...")
    
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
    
    # Проверка каждой зависимости с подробным логированием
    for module_name, description in critical_dependencies:
        try:
            # Попытка импорта модуля
            __import__(module_name)
            print(f"   ✅ {module_name} - {description}")
        except ImportError:
            # Логирование отсутствующей зависимости
            print(f"   ❌ {module_name} - {description} (НЕ НАЙДЕНО)")
            missing_dependencies.append(module_name)
    
    # Обработка результатов проверки
    if missing_dependencies:
        print(f"\n🚨 Обнаружены отсутствующие критические зависимости: {len(missing_dependencies)}")
        display_dependency_installation_instructions(missing_dependencies)
        return False
    
    print("✅ Все системные зависимости успешно проверены!")
    return True


def display_dependency_installation_instructions(missing_dependencies):
    """
    Отображение инструкций по установке отсутствующих зависимостей
    
    Предоставляет пользователю четкие и выполнимые инструкции для
    установки всех отсутствующих компонентов системы.
    
    Аргументы:
        missing_dependencies (list): Список отсутствующих модулей
    """
    print("\n🛠️  ИНСТРУКЦИИ ПО УСТАНОВКЕ ЗАВИСИМОСТЕЙ:")
    print("-" * 50)
    
    print("📦 Рекомендуемый способ (requirements.txt):")
    print("   pip install -r requirements.txt")
    
    print("\n📦 Альтернативная установка по отдельности:")
    
    # Соответствие модулей именам пакетов pip
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
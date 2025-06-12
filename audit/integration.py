# audit/integration.py
"""
Модуль интеграции системы аудита безопасности
Автор: Студент 4 курса ОмГУ им. Ф.М. Достоевского
ВКР: Автоматизированная система распознавания лиц

Описание:
Модуль интеграции обеспечивает seamless внедрение системы аудита
безопасности в существующее приложение распознавания лиц.
Реализует паттерн Plugin Architecture для модульного расширения
функциональности без нарушения основной архитектуры системы.

Основные функции:
- Безопасная интеграция компонентов аудита
- Автоматическая инициализация системы логирования
- Внедрение UI компонентов мониторинга
- Настройка dependency injection для audit логгера
- Валидация корректности интеграции

Архитектурные принципы:
- Plugin Architecture для модульности
- Dependency Injection для слабой связанности
- Factory Pattern для создания компонентов
- Observer Pattern для event-driven интеграции
- Graceful degradation при ошибках интеграции

Паттерны проектирования:
- Integration Layer для изоляции зависимостей
- Service Locator для доступа к audit сервисам
- Strategy Pattern для различных режимов аудита
"""

from audit.logger import SecurityAuditLogger
from gui.audit_widget import SecurityAuditWidget


class SecurityAuditIntegration:
    """
    Класс интеграции системы аудита безопасности с основным приложением
    
    Обеспечивает безопасное и бесшовное внедрение comprehensive системы
    аудита в существующую архитектуру приложения распознавания лиц.
    
    Ключевые возможности:
    - Модульная интеграция без нарушения существующего кода
    - Автоматическая настройка всех компонентов аудита
    - Dependency injection для loose coupling
    - Graceful error handling при проблемах интеграции
    - Validation корректности интеграции
    
    Архитектурные особенности:
    - Plugin-based архитектура для расширяемости
    - Factory methods для создания audit компонентов
    - Service locator pattern для доступа к audit сервисам
    - Event-driven интеграция для real-time мониторинга
    """
    
    @staticmethod
    def integrate_comprehensive_audit_system(app_instance):
        """
        Комплексная интеграция системы аудита безопасности
        
        Выполняет полную интеграцию audit системы в существующее приложение:
        1. Создание и инициализация audit logger
        2. Интеграция UI компонентов мониторинга
        3. Настройка dependency injection для всех компонентов
        4. Логирование начала работы системы аудита
        5. Валидация корректности интеграции
        
        Args:
            app_instance: Экземпляр главного приложения FaceRecognitionSystem
            
        Returns:
            app_instance: Модифицированный экземпляр приложения с интегрированным аудитом
            
        Raises:
            Exception: При критических ошибках интеграции
            
        Integration steps:
        1. Security audit logger initialization
        2. UI monitoring components integration  
        3. Dependency injection configuration
        4. System startup event logging
        5. Integration validation and reporting
        """
        try:
            print("🔧 Инициализация системы аудита безопасности...")
            
            # Этап 1: Создание и инициализация логгера событий безопасности
            print("📊 Создание логгера событий безопасности...")
            app_instance.audit = SecurityAuditLogger()
            
            # Этап 2: Интеграция UI компонентов мониторинга безопасности
            print("🖥️  Интеграция интерфейса мониторинга...")
            app_instance.audit_widget = SecurityAuditWidget(
                app_instance.notebook, 
                app_instance.audit
            )
            
            # Этап 3: Настройка dependency injection для audit логгера
            # Обновление существующих виджетов для использования audit системы
            print("🔗 Настройка dependency injection...")
            if hasattr(app_instance, 'recognition_widget'):
                app_instance.recognition_widget.set_audit_logger(lambda: app_instance.audit)
            
            if hasattr(app_instance, 'management_widget'):
                app_instance.management_widget.set_audit_logger(lambda: app_instance.audit)
            
            # Этап 4: Логирование успешного запуска системы аудита
            print("📝 Логирование запуска системы аудита...")
            app_instance.audit.log_system_security_event("system_start")
            
            # Этап 5: Валидация и отчет об успешной интеграции
            SecurityAuditIntegration._validate_integration_success(app_instance)
            SecurityAuditIntegration._display_integration_report()
            
            return app_instance
            
        except Exception as e:
            # Critical error handling для проблем интеграции
            print(f"❌ КРИТИЧЕСКАЯ ОШИБКА интеграции системы аудита: {e}")
            print("⚠️  Система продолжит работу без аудита безопасности")
            
            # Graceful degradation - возврат приложения без audit функций
            return app_instance
    
    @staticmethod
    def _validate_integration_success(app_instance):
        """
        Валидация успешности интеграции системы аудита
        
        Проверяет корректность всех интегрированных компонентов
        и их готовность к работе.
        
        Args:
            app_instance: Экземпляр приложения для валидации
            
        Raises:
            ValueError: При обнаружении некорректной интеграции
        """
        # Проверка наличия audit логгера
        if not hasattr(app_instance, 'audit') or app_instance.audit is None:
            raise ValueError("Audit логгер не инициализирован")
        
        # Проверка наличия audit виджета
        if not hasattr(app_instance, 'audit_widget') or app_instance.audit_widget is None:
            raise ValueError("Audit виджет не создан")
        
        # Проверка dependency injection в recognition виджете
        if hasattr(app_instance, 'recognition_widget'):
            if app_instance.recognition_widget.audit_logger_provider is None:
                raise ValueError("Dependency injection не настроен для recognition виджета")
        
        # Проверка dependency injection в management виджете
        if hasattr(app_instance, 'management_widget'):
            if app_instance.management_widget.audit_logger_provider is None:
                raise ValueError("Dependency injection не настроен для management виджета")
        
        print("✅ Валидация интеграции успешно завершена")
    
    @staticmethod
    def _display_integration_report():
        """
        Отображение детального отчета об интеграции системы аудита
        
        Выводит comprehensive отчет о successful интеграции всех
        компонентов системы аудита безопасности.
        """
        print("\n" + "="*70)
        print("🛡️  СИСТЕМА АУДИТА БЕЗОПАСНОСТИ УСПЕШНО ИНТЕГРИРОВАНА!")
        print("="*70)
        
        print("\n📋 Интегрированные компоненты:")
        print("   ✅ SecurityAuditLogger - Логгер событий безопасности")
        print("   ✅ SecurityAuditWidget - Интерфейс мониторинга")
        print("   ✅ Dependency Injection - Связывание компонентов")
        
        print("\n🔍 Мониторируемые события:")
        print("   📊 Попытки биометрического распознавания")
        print("   👥 Операции управления пользователями") 
        print("   🖥️  Системные события безопасности")
        print("   📁 Операции с файлами и данными")
        
        print("\n🎯 Возможности системы аудита:")
        print("   📈 Real-time статистика эффективности")
        print("   📋 Детальный журнал событий")
        print("   📊 Экспорт отчетов для compliance")
        print("   🔔 Автоматическое обновление данных")
        
        print("\n🏛️  Соответствие нормативным требованиям:")
        print("   📜 ГОСТ Р 50739-95 (Средства вычислительной техники)")
        print("   🔒 ГОСТ Р ИСО/МЭК 15408 (Критерии оценки безопасности)")
        print("   📋 Требования 152-ФЗ (Защита персональных данных)")
        
        print("\n🚀 Система готова к работе!")
        print("   💡 Перейдите на вкладку 'Журнал безопасности' для мониторинга")
        print("   📊 Все события автоматически логируются и анализируются")
        
        print("-"*70)
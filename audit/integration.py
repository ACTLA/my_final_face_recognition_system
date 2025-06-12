# audit/integration.py
from audit.logger import AuditLogger
from gui.audit_widget import AuditWidget

class AuditIntegration:
    """Класс для интеграции системы аудита с приложением"""
    
    @staticmethod
    def integrate_with_app(app_instance):
        """Интеграция системы аудита с существующим приложением"""
        
        # Создание логгера аудита для записи событий безопасности
        app_instance.audit = AuditLogger()
        
        # Добавление вкладки аудита в интерфейс приложения
        app_instance.audit_widget = AuditWidget(app_instance.notebook, app_instance.audit)
        
        # Логирование события запуска системы
        app_instance.audit.log_system_event("system_start")
        
        # Выводим информацию об успешной интеграции
        print("✅ Система аудита успешно интегрирована!")
        print("📊 Все действия пользователей теперь логируются:")
        print("   ✅ Попытки распознавания")
        print("   ✅ Добавление пользователей")
        print("   ✅ Удаление пользователей") 
        print("   ✅ Обновление фотографий")
        print("   ✅ Системные события")
        
        # Возвращаем экземпляр приложения с интегрированным аудитом
        return app_instance
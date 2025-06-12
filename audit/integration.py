# audit/integration.py
from audit.logger import AuditLogger
from gui.audit_widget import AuditWidget

class AuditIntegration:
    """Класс для интеграции системы аудита с приложением"""
    
    @staticmethod
    def integrate_with_app(app_instance):
        """Интеграция системы аудита с существующим приложением"""
        
        # Создание логгера аудита
        app_instance.audit = AuditLogger()
        
        # Добавление вкладки аудита
        app_instance.audit_widget = AuditWidget(app_instance.notebook, app_instance.audit)
        
        # Логирование запуска системы
        app_instance.audit.log_system_event("system_start")
        
        print("✅ Система аудита успешно интегрирована!")
        print("📊 Все действия пользователей теперь логируются:")
        print("   ✅ Попытки распознавания")
        print("   ✅ Добавление пользователей")
        print("   ✅ Удаление пользователей") 
        print("   ✅ Обновление фотографий")
        print("   ✅ Системные события")
        
        return app_instance
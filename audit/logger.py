# audit/logger.py
import sqlite3
import datetime
import csv
from config.settings import AUDIT_DB

class AuditLogger:
    """Логгер событий безопасности"""
    
    def __init__(self, db_name=AUDIT_DB):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных аудита"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                user_id TEXT,
                result TEXT NOT NULL,
                confidence REAL
            )
        ''')
        
        # Создаем индексы
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON security_events(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON security_events(event_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON security_events(user_id)')
        
        conn.commit()
        conn.close()
    
    def log_recognition(self, user_id=None, success=False, confidence=0.0):
        """Логирование попытки распознавания"""
        result = "success" if success else "failed"
        self._log_event("recognition_attempt", user_id, result, confidence)
    
    def log_user_action(self, action, user_id, success=True):
        """Логирование действий с пользователями"""
        result = "success" if success else "failed"
        self._log_event(f"user_{action}", user_id, result, None)
    
    def log_system_event(self, event_type, result="success"):
        """Логирование системных событий"""
        self._log_event(event_type, None, result, None)
    
    def _log_event(self, event_type, user_id, result, confidence):
        """Внутренний метод записи события"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            timestamp = datetime.datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO security_events (timestamp, event_type, user_id, result, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, event_type, user_id, result, confidence))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Ошибка записи в аудит: {e}")
    
    def get_statistics(self, days=7):
        """Получение статистики"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            start_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            # Общая статистика
            cursor.execute('''
                SELECT event_type, result, COUNT(*), AVG(confidence)
                FROM security_events 
                WHERE timestamp >= ?
                GROUP BY event_type, result
            ''', (start_date.isoformat(),))
            
            stats = cursor.fetchall()
            
            # Последние события
            cursor.execute('''
                SELECT timestamp, event_type, user_id, result, confidence
                FROM security_events 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT 50
            ''', (start_date.isoformat(),))
            
            recent_events = cursor.fetchall()
            
            conn.close()
            
            return {
                'general_stats': stats,
                'recent_events': recent_events
            }
            
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return None
    
    def export_to_csv(self, file_path, days=7):
        """Экспорт в CSV"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            start_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            cursor.execute('''
                SELECT timestamp, event_type, user_id, result, confidence
                FROM security_events 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (start_date.isoformat(),))
            
            events = cursor.fetchall()
            conn.close()
            
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow(['Время', 'Тип события', 'ID пользователя', 'Результат', 'Уверенность'])
                
                for event in events:
                    timestamp = datetime.datetime.fromisoformat(event[0])
                    formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    
                    event_types = {
                        'recognition_attempt': 'Попытка распознавания',
                        'user_added': 'Добавление пользователя',
                        'user_deleted': 'Удаление пользователя',
                        'user_photo_updated': 'Обновление фото',
                        'system_start': 'Запуск системы',
                        'camera_start': 'Запуск камеры',
                        'camera_stop': 'Остановка камеры'
                    }
                    
                    event_type_ru = event_types.get(event[1], event[1])
                    result_ru = 'Успех' if event[3] == 'success' else 'Неудача'
                    confidence_str = f"{event[4]:.3f}" if event[4] is not None else 'Н/Д'
                    
                    writer.writerow([
                        formatted_time,
                        event_type_ru,
                        event[2] or 'Н/Д',
                        result_ru,
                        confidence_str
                    ])
            
            return True
            
        except Exception as e:
            print(f"Ошибка экспорта в CSV: {e}")
            return False
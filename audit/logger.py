# audit/logger.py
import sqlite3
import datetime
import csv
from config.settings import AUDIT_DB

class AuditLogger:
    """Логгер событий безопасности для системы распознавания лиц"""
    
    def __init__(self, db_name=AUDIT_DB):
        # Сохраняем имя файла базы данных аудита
        self.db_name = db_name
        # Инициализируем базу данных при создании логгера
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных аудита"""
        # Устанавливаем соединение с базой данных
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Создаем таблицу для хранения событий безопасности
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                user_id TEXT,
                result TEXT NOT NULL,
                distance REAL
            )
        ''')
        
        # Создаем индексы для ускорения поиска по часто используемым полям
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON security_events(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON security_events(event_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON security_events(user_id)')
        
        # Сохраняем изменения и закрываем соединение
        conn.commit()
        conn.close()
    
    def log_recognition(self, user_id=None, success=False, distance=1.0):
        """Логирование попытки распознавания лица
        
        Параметры:
            user_id: ID распознанного пользователя (None если лицо не распознано)
            success: True если лицо успешно распознано, False если нет
            distance: Расстояние до ближайшего известного лица (0.0-1.0+)
                     Чем меньше distance, тем больше схожесть между лицами
        """
        # Определяем результат операции в текстовом виде
        result = "success" if success else "failed"
        # Записываем событие в базу данных
        self._log_event("recognition_attempt", user_id, result, distance)
    
    def log_user_action(self, action, user_id, success=True):
        """Логирование действий с пользователями (добавление, удаление, обновление)"""
        # Определяем результат операции в текстовом виде
        result = "success" if success else "failed"
        # Записываем событие (для действий с пользователями distance не применимо)
        self._log_event(f"user_{action}", user_id, result, None)
    
    def log_system_event(self, event_type, result="success"):
        """Логирование системных событий (запуск, остановка, загрузка данных)"""
        # Записываем системное событие (без user_id и distance)
        self._log_event(event_type, None, result, None)
    
    def _log_event(self, event_type, user_id, result, distance):
        """Внутренний метод для записи события в базу данных"""
        try:
            # Устанавливаем соединение с базой данных
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Получаем текущее время в формате ISO
            timestamp = datetime.datetime.now().isoformat()
            
            # Вставляем новую запись в таблицу событий
            cursor.execute('''
                INSERT INTO security_events (timestamp, event_type, user_id, result, distance)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, event_type, user_id, result, distance))
            
            # Сохраняем изменения и закрываем соединение
            conn.commit()
            conn.close()
            
        except Exception as e:
            # Выводим ошибку если не удалось записать событие
            print(f"Ошибка записи в аудит: {e}")
    
    def get_statistics(self, days=7):
        """Получение статистики событий за указанное количество дней"""
        try:
            # Устанавливаем соединение с базой данных
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Вычисляем дату начала периода
            start_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            # Получаем общую статистику по типам событий и результатам
            cursor.execute('''
                SELECT event_type, result, COUNT(*), AVG(distance)
                FROM security_events 
                WHERE timestamp >= ?
                GROUP BY event_type, result
            ''', (start_date.isoformat(),))
            
            stats = cursor.fetchall()
            
            # Получаем последние события для отображения в таблице
            cursor.execute('''
                SELECT timestamp, event_type, user_id, result, distance
                FROM security_events 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT 50
            ''', (start_date.isoformat(),))
            
            recent_events = cursor.fetchall()
            
            # Закрываем соединение
            conn.close()
            
            # Возвращаем статистику в виде словаря
            return {
                'general_stats': stats,      # Общая статистика по типам событий
                'recent_events': recent_events  # Последние события
            }
            
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return None
    
    def export_to_csv(self, file_path, days=7):
        """Экспорт событий аудита в CSV файл"""
        try:
            # Устанавливаем соединение с базой данных
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Вычисляем дату начала периода для экспорта
            start_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            # Получаем все события за указанный период
            cursor.execute('''
                SELECT timestamp, event_type, user_id, result, distance
                FROM security_events 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (start_date.isoformat(),))
            
            events = cursor.fetchall()
            conn.close()
            
            # Создаем CSV файл с результатами
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                
                # Записываем заголовки колонок
                writer.writerow(['Время', 'Тип события', 'ID пользователя', 'Результат', 'Схожесть'])
                
                # Обрабатываем каждое событие
                for event in events:
                    # Форматируем временную метку
                    timestamp = datetime.datetime.fromisoformat(event[0])
                    formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Переводим типы событий на русский язык
                    event_types = {
                        'recognition_attempt': 'Попытка распознавания',
                        'user_added': 'Добавление пользователя',
                        'user_deleted': 'Удаление пользователя',
                        'user_photo_updated': 'Обновление фото',
                        'system_start': 'Запуск системы распознавания лиц',
                        'camera_start': 'Запуск камеры',
                        'camera_stop': 'Остановка камеры'
                    }
                    
                    # Получаем русское название типа события
                    event_type_ru = event_types.get(event[1], event[1])
                    
                    # Переводим результат на русский язык
                    result_ru = 'Успех' if event[3] == 'success' else 'Неудача'
                    
                    # Обрабатываем значение схожести (distance)
                    if event[4] is not None:
                        # Форматируем distance с тремя знаками после запятой
                        distance_str = f"{event[4]:.3f}"
                    else:
                        # Для системных событий схожесть не применима
                        distance_str = 'Н/Д'
                    
                    # Записываем строку в CSV файл
                    writer.writerow([
                        formatted_time,           # Время события
                        event_type_ru,           # Тип события на русском
                        event[2] or 'Н/Д',       # ID пользователя (или "Н/Д" если отсутствует)
                        result_ru,               # Результат на русском
                        distance_str             # Значение схожести
                    ])
            
            return True  # Экспорт успешно завершен
            
        except Exception as e:
            print(f"Ошибка экспорта в CSV: {e}")
            return False  # Ошибка при экспорте
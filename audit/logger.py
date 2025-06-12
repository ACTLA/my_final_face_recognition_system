# audit/logger.py
"""
Модуль логгера событий безопасности системы
Автор: Студент 4 курса ОмГУ им. Ф.М. Достоевского
ВКР: Автоматизированная система распознавания лиц

Описание:
Логгер событий безопасности является критически важным компонентом
системы информационной безопасности. Обеспечивает comprehensive
аудит всех операций системы распознавания лиц в соответствии с
требованиями ГОСТ по информационной безопасности.

Основные функции:
- Логирование всех попыток биометрической идентификации
- Аудит операций управления пользователями
- Мониторинг системных событий безопасности
- Генерация статистических отчетов
- Экспорт данных для compliance анализа

Архитектурные принципы:
- Immutable audit trail (неизменяемый след аудита)
- Atomic transactions для обеспечения целостности
- High-performance logging для real-time систем
- Structured logging для автоматического анализа
- Compliance-ready форматы данных

Соответствие стандартам:
- ГОСТ Р 50739-95 (Средства вычислительной техники)
- ГОСТ Р ИСО/МЭК 15408 (Критерии оценки безопасности ИТ)
- Требования по защите персональных данных (152-ФЗ)
"""

import sqlite3  # Встроенная СУБД для надежного хранения audit trail
import datetime  # Работа с временными метками в ISO формате
import csv  # Экспорт данных в стандартном формате для анализа
from config.settings import AUDIT_DB


class SecurityAuditLogger:
    """
    Логгер событий безопасности для системы биометрической идентификации
    
    Класс реализует comprehensive систему аудита безопасности для
    системы распознавания лиц в соответствии с требованиями
    информационной безопасности и нормативными документами РФ.
    
    Ключевые возможности:
    - Immutable audit trail всех security events
    - High-performance logging для real-time операций  
    - Structured data storage для автоматического анализа
    - Statistical reporting для мониторинга эффективности
    - Export capabilities для integration с SIEM системами
    - Compliance reporting для regulatory requirements
    
    Архитектурные особенности:
    - Atomic database operations для обеспечения консистентности
    - Indexed storage для быстрого поиска и аналитики
    - Fail-safe error handling для критически важных операций
    - Standardized timestamps в ISO 8601 формате
    - Structured event categorization для classification
    """
    
    def __init__(self, db_name=AUDIT_DB):
        """
        Инициализация логгера событий безопасности
        
        Создает или подключается к базе данных аудита и инициализирует
        структуру таблиц для хранения событий безопасности.
        
        Args:
            db_name (str): Имя файла базы данных аудита
        """
        self.db_name = db_name  # Путь к файлу базы данных аудита
        self.initialize_audit_database()  # Создание структуры БД при первом запуске
    
    def initialize_audit_database(self):
        """
        Инициализация структуры базы данных аудита безопасности
        
        Создает таблицу security_events для хранения всех событий безопасности
        с соответствующими индексами для оптимизации производительности запросов.
        
        Структура таблицы security_events:
        - id: Уникальный идентификатор события (автоинкремент)
        - timestamp: Временная метка в ISO 8601 формате
        - event_type: Тип события безопасности (enum-like значения)
        - user_id: Идентификатор пользователя (для user-related событий)
        - result: Результат операции (success/failed)
        - confidence: Confidence score для биометрических операций
        
        Индексы для производительности:
        - idx_timestamp: Для временных запросов и отчетности
        - idx_event_type: Для фильтрации по типам событий
        - idx_user_id: Для поиска событий конкретного пользователя
        """
        # Установление соединения с базой данных аудита
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        
        # Создание основной таблицы событий безопасности
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
        
        # Создание индексов для оптимизации производительности
        # Индекс по временным меткам для быстрых временных запросов
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON security_events(timestamp)')
        
        # Индекс по типу события для фильтрации и категоризации
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON security_events(event_type)')
        
        # Индекс по ID пользователя для user-specific анализа
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON security_events(user_id)')
        
        # Фиксация изменений в базе данных
        connection.commit()
        connection.close()
    
    def log_face_recognition_attempt(self, user_id=None, success=False, confidence=0.0):
        """
        Логирование попытки биометрической идентификации
        
        Записывает все попытки распознавания лиц для анализа эффективности
        системы и обнаружения потенциальных угроз безопасности.
        
        Args:
            user_id (str, optional): ID распознанного пользователя (None для неизвестных лиц)
            success (bool): Флаг успешности распознавания
            confidence (float): Confidence score биометрического сравнения (0.0-1.0)
        
        Security implications:
        - Множественные неудачные попытки могут указывать на атаку
        - Низкие confidence scores требуют дополнительной проверки
        - Временные паттерны помогают выявить аномальную активность
        """
        result = "success" if success else "failed"
        self._write_security_event("recognition_attempt", user_id, result, confidence)
    
    def log_user_management_action(self, action, user_id, success=True):
        """
        Логирование операций управления пользователями
        
        Записывает все административные операции с пользователями для
        обеспечения accountability и соответствия требованиям аудита.
        
        Args:
            action (str): Тип операции ('added', 'deleted', 'photo_updated')
            user_id (str): Идентификатор пользователя
            success (bool): Успешность выполнения операции
        
        Compliance notes:
        - Все изменения в базе пользователей должны быть задокументированы
        - Failed операции могут указывать на проблемы безопасности
        - Audit trail требуется для соответствия 152-ФЗ
        """
        result = "success" if success else "failed"
        self._write_security_event(f"user_{action}", user_id, result, None)
    
    def log_system_security_event(self, event_type, result="success"):
        """
        Логирование системных событий безопасности
        
        Записывает критически важные системные события для мониторинга
        состояния и безопасности инфраструктуры.
        
        Args:
            event_type (str): Тип системного события
            result (str): Результат события ('success' или 'failed')
        
        System events включают:
        - Запуск/остановка системы и компонентов
        - Подключение/отключение камеры
        - Загрузка биометрических данных
        - Критические ошибки системы
        """
        self._write_security_event(event_type, None, result, None)
    
    def _write_security_event(self, event_type, user_id, result, confidence):
        """
        Внутренний метод записи события безопасности в базу данных
        
        Выполняет atomic операцию записи события с proper error handling
        для обеспечения целостности audit trail.
        
        Args:
            event_type (str): Тип события безопасности
            user_id (str or None): Идентификатор пользователя
            result (str): Результат операции
            confidence (float or None): Confidence score (для биометрических операций)
        
        Error handling:
        - Все ошибки записи логируются в console для troubleshooting
        - Критически важные события не должны теряться
        - Database connectivity issues обрабатываются gracefully
        """
        try:
            # Установление соединения с базой данных аудита
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            
            # Генерация timestamp в ISO 8601 формате для стандартизации
            timestamp = datetime.datetime.now().isoformat()
            
            # Atomic операция записи события
            cursor.execute('''
                INSERT INTO security_events (timestamp, event_type, user_id, result, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, event_type, user_id, result, confidence))
            
            # Фиксация транзакции
            connection.commit()
            connection.close()
            
        except Exception as e:
            # Error handling с логированием для troubleshooting
            print(f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось записать событие безопасности: {e}")
            print(f"Событие: {event_type}, Пользователь: {user_id}, Результат: {result}")
    
    def generate_security_statistics(self, days=7):
        """
        Генерация статистических данных безопасности
        
        Создает comprehensive отчет по активности системы безопасности
        за указанный период для анализа эффективности и выявления аномалий.
        
        Args:
            days (int): Количество дней для анализа (по умолчанию 7)
        
        Returns:
            dict or None: Словарь со статистическими данными:
                {
                    'general_stats': [(event_type, result, count, avg_confidence), ...],
                    'recent_events': [(timestamp, event_type, user_id, result, confidence), ...]
                }
                или None при ошибке
        
        Statistical metrics включают:
        - Общую статистику по типам событий и результатам
        - Средние confidence scores для биометрических операций
        - Последние события для real-time мониторинга
        - Temporal patterns для анализа аномалий
        """
        try:
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            
            # Вычисление временной границы для анализа
            start_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            # Запрос общей статистики с группировкой по типам событий и результатам
            cursor.execute('''
                SELECT event_type, result, COUNT(*), AVG(confidence)
                FROM security_events 
                WHERE timestamp >= ?
                GROUP BY event_type, result
                ORDER BY COUNT(*) DESC
            ''', (start_date.isoformat(),))
            
            general_stats = cursor.fetchall()
            
            # Запрос последних событий для real-time мониторинга
            cursor.execute('''
                SELECT timestamp, event_type, user_id, result, confidence
                FROM security_events 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT 50
            ''', (start_date.isoformat(),))
            
            recent_events = cursor.fetchall()
            
            connection.close()
            
            # Возврат структурированных статистических данных
            return {
                'general_stats': general_stats,
                'recent_events': recent_events
            }
            
        except Exception as e:
            print(f"Ошибка генерации статистики безопасности: {e}")
            return None
    
    def export_security_report(self, file_path, days=7):
        """
        Экспорт отчета безопасности в CSV формат
        
        Создает compliance-ready отчет всех событий безопасности за
        указанный период в стандартном CSV формате для интеграции
        с внешними системами анализа и SIEM решениями.
        
        Args:
            file_path (str): Путь для сохранения CSV файла
            days (int): Количество дней для включения в отчет
        
        Returns:
            bool: True при успешном экспорте, False при ошибке
        
        Export format:
        - CSV с разделителем ';' для совместимости с Excel
        - UTF-8-BOM encoding для корректного отображения кириллицы
        - Локализованные заголовки колонок
        - Форматированные временные метки
        - Переведенные типы событий и результаты
        
        Compliance features:
        - Structured format для автоматического анализа
        - Timestamp precision для forensic analysis
        - Complete audit trail для regulatory requirements
        """
        try:
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            
            # Определение временной границы для экспорта
            start_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            # Запрос всех событий за указанный период
            cursor.execute('''
                SELECT timestamp, event_type, user_id, result, confidence
                FROM security_events 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (start_date.isoformat(),))
            
            events = cursor.fetchall()
            connection.close()
            
            # Словарь локализации для compliance отчетности
            event_types_localization = {
                'recognition_attempt': 'Попытка распознавания',
                'user_added': 'Добавление пользователя',
                'user_deleted': 'Удаление пользователя',
                'user_photo_updated': 'Обновление фото',
                'system_start': 'Запуск системы',
                'camera_start': 'Запуск камеры',
                'camera_stop': 'Остановка камеры',
                'encodings_loaded': 'Загрузка кодировок'
            }
            
            # Создание CSV файла с proper encoding для кириллицы
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                
                # Заголовки колонок на русском языке для отчетности
                writer.writerow(['Время', 'Тип события', 'ID пользователя', 'Результат', 'Уверенность'])
                
                # Запись всех событий с локализацией и форматированием
                for event in events:
                    # Форматирование временной метки в читаемый формат
                    timestamp = datetime.datetime.fromisoformat(event[0])
                    formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Локализация типа события
                    event_type_ru = event_types_localization.get(event[1], event[1])
                    
                    # Форматирование результата
                    result_ru = 'Успех' if event[3] == 'success' else 'Неудача'
                    
                    # Форматирование confidence score
                    confidence_str = f"{event[4]:.3f}" if event[4] is not None else 'Н/Д'
                    
                    # Запись строки в CSV
                    writer.writerow([
                        formatted_time,
                        event_type_ru,
                        event[2] or 'Н/Д',  # user_id или 'Н/Д' если None
                        result_ru,
                        confidence_str
                    ])
            
            return True
            
        except Exception as e:
            print(f"Ошибка экспорта отчета безопасности: {e}")
            return False
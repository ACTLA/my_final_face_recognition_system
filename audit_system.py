# audit_system.py
import sqlite3
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import defaultdict
import csv
import os
import cv2
import face_recognition
import shutil
import numpy as np
from PIL import Image, ImageTk

class AuditLogger:
    """Класс для логирования событий безопасности"""
    
    def __init__(self, db_name="audit.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных аудита"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Создаем таблицу событий безопасности
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
        
        # Создаем индексы для быстрого поиска
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON security_events(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON security_events(event_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON security_events(user_id)')
        
        conn.commit()
        conn.close()
        
        # Логируем запуск системы аудита
        self._log_event("system_audit", None, "started", None)
    
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
        """Внутренний метод для записи события в БД"""
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
        """Получение статистики за указанное количество дней"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Вычисляем дату начала
            start_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            # Общая статистика
            cursor.execute('''
                SELECT event_type, result, COUNT(*), AVG(confidence)
                FROM security_events 
                WHERE timestamp >= ?
                GROUP BY event_type, result
            ''', (start_date.isoformat(),))
            
            stats = cursor.fetchall()
            
            # Активность по часам
            cursor.execute('''
                SELECT strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                       COUNT(*) as count
                FROM security_events 
                WHERE timestamp >= ? AND event_type = 'recognition_attempt'
                GROUP BY hour
                ORDER BY hour
            ''', (start_date.isoformat(),))
            
            hourly_stats = cursor.fetchall()
            
            # Топ пользователей
            cursor.execute('''
                SELECT user_id, COUNT(*) as attempts,
                       SUM(CASE WHEN result = 'success' THEN 1 ELSE 0 END) as successes
                FROM security_events 
                WHERE timestamp >= ? AND event_type = 'recognition_attempt' AND user_id IS NOT NULL
                GROUP BY user_id
                ORDER BY attempts DESC
                LIMIT 5
            ''', (start_date.isoformat(),))
            
            top_users = cursor.fetchall()
            
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
                'hourly_stats': hourly_stats,
                'top_users': top_users,
                'recent_events': recent_events
            }
            
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return None
    
    def export_to_csv(self, file_path, days=7):
        """Экспорт данных аудита в CSV"""
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
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Время', 'Тип события', 'ID пользователя', 'Результат', 'Уверенность'])
                
                for event in events:
                    # Форматируем время для удобочитаемости
                    timestamp = datetime.datetime.fromisoformat(event[0])
                    formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Переводим типы событий
                    event_types = {
                        'recognition_attempt': 'Попытка распознавания',
                        'user_added': 'Добавление пользователя',
                        'user_deleted': 'Удаление пользователя',
                        'user_photo_updated': 'Обновление фото',
                        'system_start': 'Запуск системы',
                        'camera_start': 'Запуск камеры',
                        'camera_stop': 'Остановка камеры',
                        'encodings_loaded': 'Загрузка кодировок',
                        'system_error': 'Ошибка системы',
                        'system_audit': 'Аудит системы',
                        'audit_integrated': 'Интеграция аудита'
                    }
                    
                    event_type_ru = event_types.get(event[1], event[1])
                    result_ru = 'Успех' if event[3] == 'success' else 'Неудача'
                    
                    writer.writerow([
                        formatted_time,
                        event_type_ru,
                        event[2] or 'Н/Д',
                        result_ru,
                        f"{event[4]:.3f}" if event[4] is not None else 'Н/Д'
                    ])
            
            return True
            
        except Exception as e:
            print(f"Ошибка экспорта в CSV: {e}")
            return False

class AuditTab:
    """Класс для создания вкладки аудита в существующем приложении"""
    
    def __init__(self, parent_notebook, audit_logger):
        self.notebook = parent_notebook
        self.audit = audit_logger
        
        # Создаем новую вкладку
        self.audit_frame = tk.Frame(self.notebook, bg="#6B46C1")
        self.notebook.add(self.audit_frame, text="  📋 Журнал безопасности  ")
        
        self.setup_audit_ui()
        
        # Автообновление каждые 5 секунд
        self.auto_refresh()
    
    def setup_audit_ui(self):
        """Создание интерфейса вкладки аудита"""
        
        # Основной контейнер
        main_container = tk.Frame(self.audit_frame, bg="#6B46C1")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Верхняя часть - статистика в реальном времени
        stats_container = tk.Frame(main_container, bg="white", relief="raised", bd=2)
        stats_container.pack(fill="x", pady=(0, 15))
        
        # Заголовок статистики
        stats_header = tk.Frame(stats_container, bg="#7C3AED", height=40)
        stats_header.pack(fill="x")
        stats_header.pack_propagate(False)
        
        stats_title = tk.Label(stats_header, text="СТАТИСТИКА В РЕАЛЬНОМ ВРЕМЕНИ", 
                             font=("Arial", 12, "bold"), bg="#7C3AED", fg="white")
        stats_title.pack(expand=True)
        
        # Контент статистики в горизонтальном расположении
        stats_content = tk.Frame(stats_container, bg="white")
        stats_content.pack(fill="x", padx=15, pady=15)
        
        # Создаем 4 карточки в одну строку
        stats_row = tk.Frame(stats_content, bg="white")
        stats_row.pack(fill="x")
        
        # Карточки статистики
        card1 = tk.Frame(stats_row, bg="#F8FAFC", relief="solid", bd=1)
        card1.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        tk.Label(card1, text="Всего попыток сегодня:", font=("Arial", 9), 
                bg="#F8FAFC", fg="#6B7280").pack(anchor="w", padx=10, pady=(8, 2))
        self.total_attempts_label = tk.Label(card1, text="0", font=("Arial", 14, "bold"), 
                                           bg="#F8FAFC", fg="#3B82F6")
        self.total_attempts_label.pack(anchor="w", padx=10, pady=(0, 8))
        
        card2 = tk.Frame(stats_row, bg="#F8FAFC", relief="solid", bd=1)
        card2.pack(side="left", fill="both", expand=True, padx=(5, 5))
        
        tk.Label(card2, text="Успешных:", font=("Arial", 9), 
                bg="#F8FAFC", fg="#6B7280").pack(anchor="w", padx=10, pady=(8, 2))
        self.successful_label = tk.Label(card2, text="0", font=("Arial", 14, "bold"), 
                                       bg="#F8FAFC", fg="#10B981")
        self.successful_label.pack(anchor="w", padx=10, pady=(0, 8))
        
        card3 = tk.Frame(stats_row, bg="#F8FAFC", relief="solid", bd=1)
        card3.pack(side="left", fill="both", expand=True, padx=(5, 5))
        
        tk.Label(card3, text="Успешность:", font=("Arial", 9), 
                bg="#F8FAFC", fg="#6B7280").pack(anchor="w", padx=10, pady=(8, 2))
        self.success_rate_label = tk.Label(card3, text="0%", font=("Arial", 14, "bold"), 
                                         bg="#F8FAFC", fg="#F59E0B")
        self.success_rate_label.pack(anchor="w", padx=10, pady=(0, 8))
        
        card4 = tk.Frame(stats_row, bg="#F8FAFC", relief="solid", bd=1)
        card4.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        tk.Label(card4, text="Последняя активность:", font=("Arial", 9), 
                bg="#F8FAFC", fg="#6B7280").pack(anchor="w", padx=10, pady=(8, 2))
        self.last_activity_label = tk.Label(card4, text="Нет данных", font=("Arial", 14, "bold"), 
                                          bg="#F8FAFC", fg="#6B7280")
        self.last_activity_label.pack(anchor="w", padx=10, pady=(0, 8))
        
        # Основная часть - журнал событий (занимает все оставшееся место)
        log_container = tk.Frame(main_container, bg="white", relief="raised", bd=2)
        log_container.pack(fill="both", expand=True)
        
        # Заголовок лога
        log_header = tk.Frame(log_container, bg="#7C3AED", height=40)
        log_header.pack(fill="x")
        log_header.pack_propagate(False)
        
        log_title = tk.Label(log_header, text="ЖУРНАЛ СОБЫТИЙ", 
                           font=("Arial", 12, "bold"), bg="#7C3AED", fg="white")
        log_title.pack(side="left", expand=True)
        
        # Кнопки управления справа
        export_btn = tk.Button(log_header, text="📥 Экспорт CSV", 
                             font=("Arial", 10, "bold"), bg="#10B981", fg="white",
                             relief="flat", padx=15, pady=6, command=self.export_csv)
        export_btn.pack(side="right", padx=(5, 15))
        
        refresh_btn = tk.Button(log_header, text="🔄 Обновить", 
                              font=("Arial", 10, "bold"), bg="#6366F1", fg="white",
                              relief="flat", padx=15, pady=6, command=self.refresh_data)
        refresh_btn.pack(side="right", padx=5)
        
        # Таблица событий
        log_content = tk.Frame(log_container, bg="white")
        log_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("Время", "Тип события", "Пользователь", "Результат", "Уверенность")
        self.events_tree = ttk.Treeview(log_content, columns=columns, show="headings")
        
        # Настройка колонок
        self.events_tree.heading("Время", text="Время")
        self.events_tree.heading("Тип события", text="Тип события")
        self.events_tree.heading("Пользователь", text="Пользователь")
        self.events_tree.heading("Результат", text="Результат")
        self.events_tree.heading("Уверенность", text="Уверенность")
        
        self.events_tree.column("Время", width=120)
        self.events_tree.column("Тип события", width=180)
        self.events_tree.column("Пользователь", width=120)
        self.events_tree.column("Результат", width=100)
        self.events_tree.column("Уверенность", width=100)
        
        # Скроллбар для таблицы
        scrollbar_events = ttk.Scrollbar(log_content, orient="vertical", command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=scrollbar_events.set)
        
        self.events_tree.pack(side="left", fill="both", expand=True)
        scrollbar_events.pack(side="right", fill="y")
        
        # Настройка цветов для строк
        self.events_tree.tag_configure("success", background="#F0FDF4")
        self.events_tree.tag_configure("failed", background="#FEF2F2")
        self.events_tree.tag_configure("system", background="#F8FAFC")
        
        # Загружаем начальные данные
        self.refresh_data()
    
    def refresh_data(self):
        """Обновление всех данных на вкладке"""
        try:
            stats = self.audit.get_statistics(days=1)  # Статистика за сегодня
            if stats:
                self.update_statistics(stats)
                self.update_events_table(stats)
        except Exception as e:
            print(f"Ошибка обновления данных аудита: {e}")
    
    def update_statistics(self, stats):
        """Обновление статистических карточек"""
        # Подсчитываем статистику из данных
        total_attempts = 0
        successful = 0
        
        for stat in stats['general_stats']:
            event_type, result, count, avg_confidence = stat
            if event_type == 'recognition_attempt':
                total_attempts += count
                if result == 'success':
                    successful += count
        
        success_rate = (successful / total_attempts * 100) if total_attempts > 0 else 0
        
        # Последняя активность
        last_activity = "Нет данных"
        if stats['recent_events']:
            last_timestamp = stats['recent_events'][0][0]
            last_time = datetime.datetime.fromisoformat(last_timestamp)
            last_activity = last_time.strftime('%H:%M:%S')
        
        # Обновляем лейблы
        self.total_attempts_label.config(text=str(total_attempts))
        self.successful_label.config(text=str(successful))
        self.success_rate_label.config(text=f"{success_rate:.1f}%")
        self.last_activity_label.config(text=last_activity)
    
    def update_events_table(self, stats):
        """Обновление таблицы событий"""
        # Очищаем таблицу
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        
        # Заполняем новыми данными
        for event in stats['recent_events']:
            timestamp = datetime.datetime.fromisoformat(event[0])
            formatted_time = timestamp.strftime('%H:%M:%S')
            
            # 🆕 РАСШИРЕННЫЙ СЛОВАРЬ ПЕРЕВОДОВ ДЛЯ НОВЫХ СОБЫТИЙ
            event_types = {
                'recognition_attempt': 'Распознавание',
                'user_added': '➕ Добавлен пользователь',
                'user_deleted': '🗑 Удален пользователь',
                'user_photo_updated': '🔄 Обновлено фото',
                'system_start': 'Запуск системы',
                'camera_start': 'Запуск камеры',
                'camera_stop': 'Остановка камеры',
                'system_audit': 'Аудит системы',
                'encodings_loaded': 'Загрузка кодировок',
                'system_error': 'Ошибка системы',
                'audit_integrated': 'Интеграция аудита'
            }
            
            event_type = event_types.get(event[1], event[1])
            user_id = event[2] if event[2] else "—"
            result = "✅ Успех" if event[3] == 'success' else "❌ Неудача"
            confidence = f"{event[4]:.3f}" if event[4] is not None else "—"
            
            # Определяем тег для цвета строки
            tag = ""
            if event[1] == 'recognition_attempt':
                tag = "success" if event[3] == 'success' else "failed"
            elif event[1] in ['user_added', 'user_deleted', 'user_photo_updated']:
                # 🆕 Специальная подсветка для действий с пользователями
                tag = "success" if event[3] == 'success' else "failed"
            else:
                tag = "system"
            
            self.events_tree.insert("", "end", 
                                  values=(formatted_time, event_type, user_id, result, confidence),
                                  tags=(tag,))
    
    def export_csv(self):
        """Экспорт данных в CSV"""
        file_path = filedialog.asksaveasfilename(
            title="Сохранить отчет аудита",
            defaultextension=".csv",
            filetypes=[("CSV файлы", "*.csv")]
        )
        
        if file_path:
            if self.audit.export_to_csv(file_path, days=7):
                messagebox.showinfo("Успех", f"Отчет экспортирован в:\n{file_path}")
            else:
                messagebox.showerror("Ошибка", "Не удалось экспортировать отчет!")
    
    def auto_refresh(self):
        """Автоматическое обновление каждые 5 секунд"""
        self.refresh_data()
        # Планируем следующее обновление через 5 секунд
        self.audit_frame.after(5000, self.auto_refresh)

# Класс для интеграции с существующим приложением
class AuditIntegration:
    """Класс для интеграции системы аудита с существующим приложением"""
    
    @staticmethod
    def integrate_with_app(app_instance):
        """Интеграция системы аудита с существующим приложением"""
        
        # Создаем логгер аудита
        app_instance.audit = AuditLogger()
        
        # Добавляем переменные для таймера и времени последнего распознавания
        app_instance.last_recognition_time = None
        app_instance.last_recognition_timer = None
        
        # Добавляем новую вкладку
        app_instance.audit_tab = AuditTab(app_instance.notebook, app_instance.audit)
        
        # 🆕 Больше не перезаписываем методы - логирование уже встроено в основной код!
        # Просто логируем успешную интеграцию
        app_instance.audit.log_system_event("audit_integrated")
        
        print("✅ Система аудита успешно интегрирована!")
        print("📊 Все действия пользователей теперь логируются:")
        print("   ✅ Попытки распознавания")
        print("   ✅ Добавление пользователей")
        print("   ✅ Удаление пользователей") 
        print("   ✅ Обновление фотографий")
        print("   ✅ Системные события")
        return app_instance

# Пример использования - добавить в main.py:
"""
if __name__ == "__main__":
    import tkinter as tk
    from modern_face_recognition import ModernFaceRecognitionApp
    from audit_system import AuditIntegration
    
    root = tk.Tk()
    app = ModernFaceRecognitionApp(root)
    
    # 🆕 ИНТЕГРИРУЕМ СИСТЕМУ АУДИТА
    app = AuditIntegration.integrate_with_app(app)
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
"""
        
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
                        'system_error': 'Ошибка системы'
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
        log_title.pack(side="left", expand=True)  # Слева с расширением как у статистики
        
        # Кнопки управления справа
        export_btn = tk.Button(log_header, text="📥 Экспорт CSV", 
                             font=("Arial", 10, "bold"), bg="#10B981", fg="white",
                             relief="flat", padx=15, pady=6, command=self.export_csv)
        export_btn.pack(side="right", padx=(5, 15))  # Справа с отступом
        
        refresh_btn = tk.Button(log_header, text="🔄 Обновить", 
                              font=("Arial", 10, "bold"), bg="#6366F1", fg="white",
                              relief="flat", padx=15, pady=6, command=self.refresh_data)
        refresh_btn.pack(side="right", padx=5)  # Справа перед экспортом
        
        # Таблица событий (теперь занимает большую часть экрана)
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
    
    def create_stat_card(self, parent, title, value, color):
        """Создание карточки со статистикой (не используется в новой версии)"""
        pass
    
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
    
    def update_charts(self, stats):
        """Обновление графиков (удалено)"""
        pass
    
    def update_events_table(self, stats):
        """Обновление таблицы событий"""
        # Очищаем таблицу
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        
        # Заполняем новыми данными
        for event in stats['recent_events']:
            timestamp = datetime.datetime.fromisoformat(event[0])
            formatted_time = timestamp.strftime('%H:%M:%S')
            
            # Переводим типы событий
            event_types = {
                'recognition_attempt': 'Распознавание',
                'user_added': 'Добавлен пользователь',
                'user_deleted': 'Удален пользователь',
                'user_photo_updated': 'Обновлено фото',
                'system_start': 'Запуск системы',
                'camera_start': 'Запуск камеры',
                'camera_stop': 'Остановка камеры',
                'system_audit': 'Аудит системы',
                'encodings_loaded': 'Загрузка кодировок',
                'system_error': 'Ошибка системы'
            }
            
            event_type = event_types.get(event[1], event[1])
            user_id = event[2] if event[2] else "—"
            result = "✅ Успех" if event[3] == 'success' else "❌ Неудача"
            confidence = f"{event[4]:.3f}" if event[4] is not None else "—"
            
            # Определяем тег для цвета строки
            tag = ""
            if event[1] == 'recognition_attempt':
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
        
        # Добавляем новую вкладку
        app_instance.audit_tab = AuditTab(app_instance.notebook, app_instance.audit)
        
        # Сохраняем оригинальные методы
        app_instance._original_process_frame = app_instance.process_frame
        app_instance._original_add_user = app_instance.add_user
        app_instance._original_delete_user = app_instance.delete_user
        app_instance._original_start_camera = app_instance.start_camera
        app_instance._original_stop_camera = app_instance.stop_camera
        app_instance._original_load_encodings = app_instance.load_encodings
        app_instance._original_update_user_photo = app_instance.update_user_photo
        
        # Заменяем методы на версии с логированием
        app_instance.process_frame = lambda: AuditIntegration._process_frame_with_audit(app_instance)
        app_instance.add_user = lambda: AuditIntegration._add_user_with_audit(app_instance)
        app_instance.delete_user = lambda: AuditIntegration._delete_user_with_audit(app_instance)
        app_instance.start_camera = lambda: AuditIntegration._start_camera_with_audit(app_instance)
        app_instance.stop_camera = lambda: AuditIntegration._stop_camera_with_audit(app_instance)
        app_instance.load_encodings = lambda: AuditIntegration._load_encodings_with_audit(app_instance)
        app_instance.update_user_photo = lambda: AuditIntegration._update_user_photo_with_audit(app_instance)
        
        # Логируем интеграцию
        app_instance.audit.log_system_event("audit_integrated")
        
        print("✅ Система аудита успешно интегрирована!")
        return app_instance
    
    @staticmethod
    def _process_frame_with_audit(app_instance):
        """Версия process_frame с логированием"""
        # Вызываем оригинальный метод
        if not app_instance.is_running or not app_instance.cap:
            return
        
        ret, frame = app_instance.cap.read()
        if not ret:
            print("Не удалось получить кадр с камеры")
            app_instance.root.after(30, app_instance.process_frame)
            return
        
        # Уменьшаем размер кадра для ускорения распознавания
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Поиск лиц на кадре
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        recognized_user = None
        
        # Обработка найденных лиц
        for face_encoding, face_location in zip(face_encodings, face_locations):
            if app_instance.known_encodings:
                matches = face_recognition.compare_faces(app_instance.known_encodings, face_encoding)
                face_distances = face_recognition.face_distance(app_instance.known_encodings, face_encoding)
                
                best_match_index = np.argmin(face_distances)
                confidence = 1 - face_distances[best_match_index]  # Преобразуем расстояние в уверенность
                
                if matches[best_match_index]:
                    user_id = app_instance.known_user_ids[best_match_index]
                    user_data = app_instance.db.get_user(user_id)
                    if user_data:
                        recognized_user = user_data
                        name = user_data[2]
                        # 🆕 ЛОГИРУЕМ УСПЕШНОЕ РАСПОЗНАВАНИЕ
                        app_instance.audit.log_recognition(user_id, True, confidence)
                    else:
                        name = "Ошибка БД"
                        # 🆕 ЛОГИРУЕМ ОШИБКУ БД
                        app_instance.audit.log_recognition(None, False, confidence)
                else:
                    name = "Неизвестный"
                    # 🆕 ЛОГИРУЕМ НЕИЗВЕСТНОГО ПОЛЬЗОВАТЕЛЯ
                    app_instance.audit.log_recognition(None, False, confidence)
            else:
                name = "Нет кодировок"
            
            # Рисуем рамку вокруг лица
            top, right, bottom, left = face_location
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            color = (0, 255, 0) if recognized_user else (0, 0, 255)
            
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        # Обновляем информацию о пользователе
        if recognized_user:
            app_instance.update_user_info(recognized_user)
        elif not face_locations:
            app_instance.reset_user_info()
        
        # Конвертируем кадр для отображения в Tkinter
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        photo = ImageTk.PhotoImage(pil_image)
        
        app_instance.video_label.config(image=photo, text="")
        app_instance.video_label.image = photo
        
        app_instance.root.after(30, app_instance.process_frame)
    
    @staticmethod
    def _add_user_with_audit(app_instance):
        """Версия add_user с логированием"""
        user_id = app_instance.user_id_entry.get().strip()
        name = app_instance.name_entry.get().strip()
        
        if not user_id or not name:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        
        if not app_instance.photo_path:
            messagebox.showerror("Ошибка", "Выберите фотографию!")
            return
        
        photo_filename = f"{user_id}.jpg"
        photo_destination = os.path.join("photos", photo_filename)
        
        try:
            shutil.copy2(app_instance.photo_path, photo_destination)
            face_encoding = app_instance.create_face_encoding(photo_destination)
            
            if app_instance.db.add_user(user_id, name, photo_destination, face_encoding):
                # 🆕 ЛОГИРУЕМ УСПЕШНОЕ ДОБАВЛЕНИЕ
                app_instance.audit.log_user_action("added", user_id, True)
                
                messagebox.showinfo("Успех", "✅ Пользователь добавлен!")
                
                # Очищаем поля
                app_instance.user_id_entry.delete(0, tk.END)
                app_instance.name_entry.delete(0, tk.END)
                app_instance.photo_path = ""
                app_instance.photo_status_label.config(text="Фото не выбрано", fg="#6B7280")
                
                # Очищаем превью
                app_instance.photo_preview.config(image="", text="Превью", font=("Arial", 8), fg="#6B7280")
                
                # Обновляем данные
                app_instance.refresh_user_list()
                app_instance.load_encodings()
            else:
                # 🆕 ЛОГИРУЕМ НЕУДАЧНОЕ ДОБАВЛЕНИЕ
                app_instance.audit.log_user_action("added", user_id, False)
                
                messagebox.showerror("Ошибка", "Пользователь с таким ID уже существует!")
                if os.path.exists(photo_destination):
                    os.remove(photo_destination)
                    
        except Exception as e:
            # 🆕 ЛОГИРУЕМ ОШИБКУ ДОБАВЛЕНИЯ
            app_instance.audit.log_user_action("added", user_id, False)
            app_instance.audit.log_system_event("system_error", "failed")
            messagebox.showerror("Ошибка", f"Не удалось добавить пользователя: {str(e)}")
    
    @staticmethod
    def _delete_user_with_audit(app_instance):
        """Версия delete_user с логированием"""
        selected_item = app_instance.users_tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления!")
            return
        
        user_data = app_instance.users_tree.item(selected_item)
        user_id = user_data['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить пользователя {user_id}?"):
            if app_instance.db.delete_user(user_id):
                # 🆕 ЛОГИРУЕМ УСПЕШНОЕ УДАЛЕНИЕ
                app_instance.audit.log_user_action("deleted", user_id, True)
                
                messagebox.showinfo("Успех", "✅ Пользователь удален!")
                app_instance.refresh_user_list()
                app_instance.load_encodings()
            else:
                # 🆕 ЛОГИРУЕМ НЕУДАЧНОЕ УДАЛЕНИЕ
                app_instance.audit.log_user_action("deleted", user_id, False)
                messagebox.showerror("Ошибка", "Не удалось удалить пользователя!")
    
    @staticmethod
    def _start_camera_with_audit(app_instance):
        """Версия start_camera с логированием"""
        try:
            app_instance.cap = cv2.VideoCapture(0)
            if not app_instance.cap.isOpened():
                # 🆕 ЛОГИРУЕМ ОШИБКУ ЗАПУСКА КАМЕРЫ
                app_instance.audit.log_system_event("camera_start", "failed")
                messagebox.showerror("Ошибка", "Не удалось подключиться к камере!")
                return
            
            app_instance.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            app_instance.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            app_instance.is_running = True
            app_instance.start_button.config(state="disabled")
            app_instance.stop_button.config(state="normal")
            
            # 🆕 ЛОГИРУЕМ УСПЕШНЫЙ ЗАПУСК КАМЕРЫ
            app_instance.audit.log_system_event("camera_start", "success")
            
            app_instance.process_frame()
            
        except Exception as e:
            # 🆕 ЛОГИРУЕМ ОШИБКУ ЗАПУСКА КАМЕРЫ
            app_instance.audit.log_system_event("camera_start", "failed")
            messagebox.showerror("Ошибка", f"Ошибка запуска камеры: {str(e)}")
    
    @staticmethod
    def _stop_camera_with_audit(app_instance):
        """Версия stop_camera с логированием"""
        app_instance.is_running = False
        if app_instance.cap:
            app_instance.cap.release()
        
        app_instance.start_button.config(state="normal")
        app_instance.stop_button.config(state="disabled")
        
        app_instance.video_label.config(image="", text="Камера остановлена")
        app_instance.reset_user_info()
        
        # 🆕 ЛОГИРУЕМ ОСТАНОВКУ КАМЕРЫ
        app_instance.audit.log_system_event("camera_stop", "success")
    
    @staticmethod
    def _load_encodings_with_audit(app_instance):
        """Версия load_encodings с логированием"""
        try:
            app_instance.known_encodings, app_instance.known_user_ids = app_instance.db.get_all_encodings()
            print(f"Загружено кодировок из БД: {len(app_instance.known_encodings)}")
            
            # 🆕 ЛОГИРУЕМ УСПЕШНУЮ ЗАГРУЗКУ КОДИРОВОК
            app_instance.audit.log_system_event("encodings_loaded", "success")
            
            if not app_instance.known_encodings:
                print("Кодировки не найдены. Добавьте пользователей.")
                
        except Exception as e:
            print(f"Ошибка загрузки кодировок: {e}")
            # 🆕 ЛОГИРУЕМ ОШИБКУ ЗАГРУЗКИ КОДИРОВОК
            app_instance.audit.log_system_event("encodings_loaded", "failed")
            app_instance.known_encodings = []
            app_instance.known_user_ids = []
    
    @staticmethod
    def _update_user_photo_with_audit(app_instance):
        """Версия update_user_photo с логированием"""
        selected_item = app_instance.users_tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для обновления фото!")
            return
        
        if not app_instance.photo_path:
            messagebox.showerror("Ошибка", "Сначала выберите новую фотографию!")
            return
        
        # Получаем данные выбранного пользователя
        user_data = app_instance.users_tree.item(selected_item)
        user_id = user_data['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Обновить фото для пользователя {user_id}?"):
            try:
                # Копируем новое фото
                photo_filename = f"{user_id}.jpg"
                photo_destination = os.path.join("photos", photo_filename)
                
                # Удаляем старое фото если существует
                if os.path.exists(photo_destination):
                    os.remove(photo_destination)
                
                # Копируем новое фото
                shutil.copy2(app_instance.photo_path, photo_destination)
                
                # Создаем новую кодировку
                face_encoding = app_instance.create_face_encoding(photo_destination)
                
                # Обновляем в БД
                if app_instance.db.update_user_encoding(user_id, face_encoding):
                    # 🆕 ЛОГИРУЕМ УСПЕШНОЕ ОБНОВЛЕНИЕ ФОТО
                    app_instance.audit.log_user_action("photo_updated", user_id, True)
                    
                    messagebox.showinfo("Успех", "✅ Фото пользователя обновлено!")
                    
                    # Очищаем выбранное фото
                    app_instance.photo_path = ""
                    app_instance.photo_status_label.config(text="Фото не выбрано", fg="#6B7280")
                    app_instance.photo_preview.config(image="", text="Превью", font=("Arial", 8), fg="#6B7280")
                    
                    # Обновляем данные
                    app_instance.refresh_user_list()
                    app_instance.load_encodings()
                else:
                    # 🆕 ЛОГИРУЕМ НЕУДАЧНОЕ ОБНОВЛЕНИЕ ФОТО
                    app_instance.audit.log_user_action("photo_updated", user_id, False)
                    messagebox.showerror("Ошибка", "Не удалось обновить фото в БД!")
                    
            except Exception as e:
                # 🆕 ЛОГИРУЕМ ОШИБКУ ОБНОВЛЕНИЯ ФОТО
                app_instance.audit.log_user_action("photo_updated", user_id, False)
                app_instance.audit.log_system_event("system_error", "failed")
                messagebox.showerror("Ошибка", f"Не удалось обновить фото: {str(e)}")

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
# gui/audit_widget.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime

class AuditWidget:
    """Виджет аудита безопасности"""
    
    def __init__(self, parent_notebook, audit_logger):
        # Сохраняем ссылки на основные компоненты
        self.notebook = parent_notebook
        self.audit = audit_logger
        
        # Создание виджета
        self.setup_widget()
        
        # Автообновление каждые 5 секунд
        self.auto_refresh()
    
    def setup_widget(self):
        """Создание интерфейса вкладки аудита"""
        # Создание фрейма вкладки
        self.frame = tk.Frame(self.notebook, bg="#6B46C1")
        self.notebook.add(self.frame, text="  📋 Журнал безопасности  ")
        
        # Основной контейнер
        main_container = tk.Frame(self.frame, bg="#6B46C1")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Верхняя часть - статистика
        self.create_statistics_panel(main_container)
        
        # Нижняя часть - журнал событий
        self.create_events_panel(main_container)
    
    def create_statistics_panel(self, parent):
        """Создание панели статистики"""
        # Контейнер для статистики
        stats_container = tk.Frame(parent, bg="white", relief="raised", bd=2)
        stats_container.pack(fill="x", pady=(0, 15))
        
        # Заголовок статистики
        stats_header = tk.Frame(stats_container, bg="#7C3AED", height=40)
        stats_header.pack(fill="x")
        stats_header.pack_propagate(False)
        
        stats_title = tk.Label(stats_header, text="СТАТИСТИКА В РЕАЛЬНОМ ВРЕМЕНИ", 
                             font=("Arial", 12, "bold"), bg="#7C3AED", fg="white")
        stats_title.pack(expand=True)
        
        # Контент статистики
        stats_content = tk.Frame(stats_container, bg="white")
        stats_content.pack(fill="x", padx=15, pady=15)
        
        # Карточки статистики в горизонтальном расположении
        self.create_statistics_cards(stats_content)
    
    def create_statistics_cards(self, parent):
        """Создание карточек статистики"""
        # Горизонтальный ряд карточек
        stats_row = tk.Frame(parent, bg="white")
        stats_row.pack(fill="x")
        
        # Карточка 1 - Всего попыток распознавания за сегодня
        card1 = tk.Frame(stats_row, bg="#F8FAFC", relief="solid", bd=1)
        card1.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        tk.Label(card1, text="Всего попыток сегодня:", font=("Arial", 9), 
                bg="#F8FAFC", fg="#6B7280").pack(anchor="w", padx=10, pady=(8, 2))
        self.total_attempts_label = tk.Label(card1, text="0", font=("Arial", 14, "bold"), 
                                           bg="#F8FAFC", fg="#3B82F6")
        self.total_attempts_label.pack(anchor="w", padx=10, pady=(0, 8))
        
        # Карточка 2 - Успешные распознавания
        card2 = tk.Frame(stats_row, bg="#F8FAFC", relief="solid", bd=1)
        card2.pack(side="left", fill="both", expand=True, padx=(5, 5))
        
        tk.Label(card2, text="Успешных:", font=("Arial", 9), 
                bg="#F8FAFC", fg="#6B7280").pack(anchor="w", padx=10, pady=(8, 2))
        self.successful_label = tk.Label(card2, text="0", font=("Arial", 14, "bold"), 
                                       bg="#F8FAFC", fg="#10B981")
        self.successful_label.pack(anchor="w", padx=10, pady=(0, 8))
        
        # Карточка 3 - Процент успешности
        card3 = tk.Frame(stats_row, bg="#F8FAFC", relief="solid", bd=1)
        card3.pack(side="left", fill="both", expand=True, padx=(5, 5))
        
        tk.Label(card3, text="Успешность:", font=("Arial", 9), 
                bg="#F8FAFC", fg="#6B7280").pack(anchor="w", padx=10, pady=(8, 2))
        self.success_rate_label = tk.Label(card3, text="0%", font=("Arial", 14, "bold"), 
                                         bg="#F8FAFC", fg="#F59E0B")
        self.success_rate_label.pack(anchor="w", padx=10, pady=(0, 8))
        
        # Карточка 4 - Время последней активности
        card4 = tk.Frame(stats_row, bg="#F8FAFC", relief="solid", bd=1)
        card4.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        tk.Label(card4, text="Последняя активность:", font=("Arial", 9), 
                bg="#F8FAFC", fg="#6B7280").pack(anchor="w", padx=10, pady=(8, 2))
        self.last_activity_label = tk.Label(card4, text="Нет данных", font=("Arial", 14, "bold"), 
                                          bg="#F8FAFC", fg="#6B7280")
        self.last_activity_label.pack(anchor="w", padx=10, pady=(0, 8))
    
    def create_events_panel(self, parent):
        """Создание панели журнала событий"""
        # Контейнер для журнала событий
        log_container = tk.Frame(parent, bg="white", relief="raised", bd=2)
        log_container.pack(fill="both", expand=True)
        
        # Заголовок с кнопкой экспорта
        self.create_events_header(log_container)
        
        # Таблица событий
        self.create_events_table(log_container)
    
    def create_events_header(self, parent):
        """Создание заголовка журнала событий"""
        # Заголовок журнала
        log_header = tk.Frame(parent, bg="#7C3AED", height=40)
        log_header.pack(fill="x")
        log_header.pack_propagate(False)
        
        log_title = tk.Label(log_header, text="ЖУРНАЛ СОБЫТИЙ", 
                           font=("Arial", 12, "bold"), bg="#7C3AED", fg="white")
        log_title.pack(side="left", expand=True)
        
        # Кнопка экспорта отчета в CSV
        export_btn = tk.Button(log_header, text="Экспорт", 
                             font=("Arial", 10, "bold"), bg="#10B981", fg="white",
                             relief="flat", padx=15, pady=6, command=self.export_csv)
        export_btn.pack(side="right", padx=(5, 15))
    
    def create_events_table(self, parent):
        """Создание таблицы событий"""
        # Контейнер для таблицы
        log_content = tk.Frame(parent, bg="white")
        log_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Определяем колонки таблицы (заменили "Уверенность" на "Схожесть")
        columns = ("Время", "Тип события", "ID пользователя", "Результат", "Схожесть")
        self.events_tree = ttk.Treeview(log_content, columns=columns, show="headings")
        
        # Настройка заголовков и ширины колонок
        for col in columns:
            self.events_tree.heading(col, text=col)
        
        self.events_tree.column("Время", width=120)
        self.events_tree.column("Тип события", width=180)
        self.events_tree.column("ID пользователя", width=120)
        self.events_tree.column("Результат", width=100)
        self.events_tree.column("Схожесть", width=100)  # Заменили "Уверенность" на "Схожесть"
        
        # Вертикальная полоса прокрутки
        scrollbar_events = ttk.Scrollbar(log_content, orient="vertical", 
                                        command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=scrollbar_events.set)
        
        # Размещение таблицы и полосы прокрутки
        self.events_tree.pack(side="left", fill="both", expand=True)
        scrollbar_events.pack(side="right", fill="y")
        
        # Настройка цветовой схемы строк
        self.events_tree.tag_configure("success", background="#F0FDF4")   # Зеленый фон для успешных
        self.events_tree.tag_configure("failed", background="#FEF2F2")    # Красный фон для неудачных
        self.events_tree.tag_configure("system", background="#F8FAFC")    # Серый фон для системных
        
        # Загрузка начальных данных
        self.refresh_data()
    
    def refresh_data(self):
        """Обновление всех данных на вкладке"""
        try:
            # Получаем статистику за сегодня
            stats = self.audit.get_statistics(days=1)
            if stats:
                # Обновляем статистические карточки
                self.update_statistics(stats)
                # Обновляем таблицу событий
                self.update_events_table(stats)
        except Exception as e:
            print(f"Ошибка обновления данных аудита: {e}")
    
    def update_statistics(self, stats):
        """Обновление статистических карточек"""
        # Подсчет общей статистики
        total_attempts = 0  # Общее количество попыток распознавания
        successful = 0      # Количество успешных распознаваний
        
        # Анализируем статистику по типам событий
        for stat in stats['general_stats']:
            event_type, result, count, avg_distance = stat
            if event_type == 'recognition_attempt':  # Только попытки распознавания
                total_attempts += count
                if result == 'success':
                    successful += count
        
        # Вычисляем процент успешности
        success_rate = (successful / total_attempts * 100) if total_attempts > 0 else 0
        
        # Определяем время последней активности
        last_activity = "Нет данных"
        if stats['recent_events']:
            # Берем время из самого последнего события
            last_timestamp = stats['recent_events'][0][0]
            last_time = datetime.datetime.fromisoformat(last_timestamp)
            last_activity = last_time.strftime('%H:%M:%S')
        
        # Обновляем текст в карточках статистики
        self.total_attempts_label.config(text=str(total_attempts))
        self.successful_label.config(text=str(successful))
        self.success_rate_label.config(text=f"{success_rate:.1f}%")
        self.last_activity_label.config(text=last_activity)
    
    def update_events_table(self, stats):
        """Обновление таблицы событий"""
        # Очищаем существующие записи в таблице
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        
        # Заполняем таблицу новыми данными
        for event in stats['recent_events']:
            # Парсим временную метку
            timestamp = datetime.datetime.fromisoformat(event[0])
            formatted_time = timestamp.strftime('%H:%M:%S')
            
            # Переводим типы событий на русский язык
            event_types = {
                'recognition_attempt': 'Распознавание',
                'user_added': 'Добавлен пользователь',
                'user_deleted': 'Удален пользователь',
                'user_photo_updated': 'Обновлено фото',
                'system_start': 'Запуск системы',
                'camera_start': 'Запуск камеры',
                'camera_stop': 'Остановка камеры',
                'encodings_loaded': 'Загрузка кодировок'
            }
            
            # Получаем русское название события
            event_type = event_types.get(event[1], event[1])
            
            # Обрабатываем ID пользователя (может быть None)
            user_id = event[2] if event[2] else "—"
            
            # Переводим результат на русский
            result = "✅ Успех" if event[3] == 'success' else "❌ Неудача"
            
            # Обрабатываем значение схожести (distance вместо confidence)
            # Чем меньше distance, тем больше схожесть
            if event[4] is not None:
                distance_value = event[4]
                # Отображаем distance с тремя знаками после запятой
                similarity = f"{distance_value:.3f}"
            else:
                # Для системных событий схожесть не применима
                similarity = "—"
            
            # Определяем цветовую схему строки
            if event[1] == 'recognition_attempt':
                # Для попыток распознавания цвет зависит от результата
                tag = "success" if event[3] == 'success' else "failed"
            elif event[1] in ['user_added', 'user_deleted', 'user_photo_updated']:
                # Для операций с пользователями цвет зависит от результата
                tag = "success" if event[3] == 'success' else "failed"
            else:
                # Для системных событий используем нейтральный цвет
                tag = "system"
            
            # Добавляем строку в таблицу
            self.events_tree.insert("", "end", 
                                  values=(formatted_time, event_type, user_id, result, similarity),
                                  tags=(tag,))
    
    def export_csv(self):
        """Экспорт данных в CSV файл"""
        # Открываем диалог сохранения файла
        file_path = filedialog.asksaveasfilename(
            title="Сохранить отчет аудита",
            defaultextension=".csv",
            filetypes=[("CSV файлы", "*.csv")]
        )
        
        if file_path:
            # Экспортируем данные за последние 7 дней
            if self.audit.export_to_csv(file_path, days=7):
                messagebox.showinfo("Успех", f"Отчет экспортирован в:\n{file_path}")
            else:
                messagebox.showerror("Ошибка", "Не удалось экспортировать отчет!")
    
    def auto_refresh(self):
        """Автоматическое обновление данных каждые 5 секунд"""
        # Обновляем данные
        self.refresh_data()
        # Планируем следующее обновление через 5 секунд
        self.frame.after(5000, self.auto_refresh)
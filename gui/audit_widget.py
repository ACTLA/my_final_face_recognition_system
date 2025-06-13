# gui/audit_widget.py
"""
Модуль виджета аудита безопасности системы
Автор: Студент 4 курса ОмГУ им. Ф.М. Достоевского
ВКР: Автоматизированная система распознавания лиц

Описание:
Виджет аудита безопасности обеспечивает мониторинг и анализ всех
событий системы распознавания лиц в режиме реального времени.
Является критически важным компонентом для обеспечения информационной
безопасности и соответствия требованиям аудита.

Основные функции:
- Мониторинг событий безопасности в режиме реального времени
- Визуализация статистики попыток распознавания
- Детальный журнал всех операций системы
- Экспорт отчетов для внешнего анализа
- Автоматическое обновление данных

Компоненты безопасности:
- Статистические показатели эффективности системы
- Журнал событий с временными метками
- Индикаторы подозрительной активности
- Отчеты для соответствия нормативным требованиям

Архитектурные решения:
- Обновление в режиме реального времени через периодические таймеры
- Цветовая индикация статусов для быстрого анализа
- Экспорт в стандартных форматах для интеграции
"""

import tkinter as tk  # Основная библиотека для создания графического интерфейса
from tkinter import ttk, filedialog, messagebox  # Дополнительные компоненты графического интерфейса
import datetime  # Работа с датой и временем для форматирования
from config.settings import AUDIT_DATA_REFRESH_INTERVAL, THEME_COLOR, SECOND_COLOR, TEXT_COLOR


class SecurityAuditWidget:
    """
    Виджет аудита безопасности для мониторинга системы распознавания лиц
    
    Предоставляет всеобъемлющий интерфейс для мониторинга всех аспектов
    безопасности системы биометрической идентификации в режиме реального времени.
    
    Ключевые возможности:
    - Панель управления с ключевыми показателями производительности
    - Журнал событий безопасности в режиме реального времени
    - Статистический анализ эффективности распознавания
    - Экспорт данных для отчетности о соответствии требованиям
    - Автоматические предупреждения при подозрительной активности
    
    Архитектурные особенности:
    - Обновления, управляемые событиями, для минимальной задержки
    - Цветовая индикация для быстрого анализа статусов
    - Масштабируемый дизайн для обработки больших объемов событий
    - Готовые к интеграции форматы экспорта данных
    """
    
    def __init__(self, parent_notebook, audit_logger):
        """
        Инициализация виджета аудита безопасности
        
        Аргументы:
            parent_notebook (ttk.Notebook): Родительский контейнер вкладок
            audit_logger (SecurityAuditLogger): Логгер событий безопасности
        """
        self.notebook = parent_notebook  # Контейнер вкладок
        self.audit = audit_logger  # Система аудита безопасности
        
        # Инициализация интерфейса мониторинга
        self.initialize_security_monitoring_interface()
        
        # Запуск автоматического обновления данных
        self.schedule_automatic_refresh()
    
    def initialize_security_monitoring_interface(self):
        """
        Создание интерфейса мониторинга безопасности
        
        Интерфейс состоит из двух основных секций:
        1. Верхняя панель: Статистические показатели в режиме реального времени
        2. Нижняя панель: Детальный журнал событий безопасности
        """
        # Создание основного фрейма вкладки аудита
        self.frame = tk.Frame(self.notebook, bg=THEME_COLOR)
        self.notebook.add(self.frame, text="  Журнал безопасности  ")
        
        # Основной контейнер для компонентов
        main_container = tk.Frame(self.frame, bg=THEME_COLOR)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Создание секций интерфейса
        self.create_security_statistics_panel(main_container)  # Верхняя панель - статистика
        self.create_event_log_panel(main_container)           # Нижняя панель - журнал событий
    
    def create_security_statistics_panel(self, parent):
        """
        Создание панели статистических показателей безопасности
        
        Панель включает ключевые показатели производительности в режиме реального времени для мониторинга:
        - Общее количество попыток идентификации
        - Количество успешных распознаваний
        - Процент успешности (коэффициент эффективности)
        - Временная метка последней активности системы
        
        Аргументы:
            parent (tk.Widget): Родительский контейнер
        """
        # Контейнер статистики с рамкой
        stats_container = tk.Frame(parent, bg="white", relief="raised", bd=2)
        stats_container.pack(fill="x", pady=(0, 15))
        
        # Заголовок панели статистики
        stats_header = tk.Frame(stats_container, bg=SECOND_COLOR, height=40)
        stats_header.pack(fill="x")
        stats_header.pack_propagate(False)
        
        stats_title = tk.Label(stats_header, text="СТАТИСТИКА БЕЗОПАСНОСТИ В РЕАЛЬНОМ ВРЕМЕНИ", 
                             font=("Arial", 12, "bold"), bg=SECOND_COLOR, fg=TEXT_COLOR)
        stats_title.pack(expand=True)
        
        # Контейнер содержимого статистики
        stats_content = tk.Frame(stats_container, bg="white")
        stats_content.pack(fill="x", padx=15, pady=15)
        
        # Создание панели управления с показателями
        self.create_metrics_display_cards(stats_content)
    
    def create_metrics_display_cards(self, parent):
        """
        Создание карточек показателей для панели мониторинга
        
        Создает горизонтальное размещение с четырьмя ключевыми показателями производительности:
        1. Общее количество попыток идентификации за сегодня
        2. Количество успешных распознаваний
        3. Процент эффективности системы (коэффициент успешности)
        4. Временная метка последней активности
        
        Аргументы:
            parent (tk.Widget): Родительский контейнер для карточек
        """
        # Горизонтальный контейнер для карточек показателей
        stats_row = tk.Frame(parent, bg="white")
        stats_row.pack(fill="x")
        
        # Карточка 1: Общее количество попыток идентификации
        card1 = tk.Frame(stats_row, bg="#F8FAFC", relief="solid", bd=1)
        card1.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        tk.Label(card1, text="Всего попыток сегодня:", font=("Arial", 9), 
                bg="#F8FAFC", fg="#6B7280").pack(anchor="w", padx=10, pady=(8, 2))
        self.total_attempts_label = tk.Label(card1, text="0", font=("Arial", 14, "bold"), 
                                           bg="#F8FAFC", fg="#3B82F6")
        self.total_attempts_label.pack(anchor="w", padx=10, pady=(0, 8))
        
        # Карточка 2: Успешные распознавания
        card2 = tk.Frame(stats_row, bg="#F8FAFC", relief="solid", bd=1)
        card2.pack(side="left", fill="both", expand=True, padx=(5, 5))
        
        tk.Label(card2, text="Успешных:", font=("Arial", 9), 
                bg="#F8FAFC", fg="#6B7280").pack(anchor="w", padx=10, pady=(8, 2))
        self.successful_label = tk.Label(card2, text="0", font=("Arial", 14, "bold"), 
                                       bg="#F8FAFC", fg="#10B981")
        self.successful_label.pack(anchor="w", padx=10, pady=(0, 8))
        
        # Карточка 3: Процент эффективности системы
        card3 = tk.Frame(stats_row, bg="#F8FAFC", relief="solid", bd=1)
        card3.pack(side="left", fill="both", expand=True, padx=(5, 5))
        
        tk.Label(card3, text="Эффективность:", font=("Arial", 9), 
                bg="#F8FAFC", fg="#6B7280").pack(anchor="w", padx=10, pady=(8, 2))
        self.success_rate_label = tk.Label(card3, text="0%", font=("Arial", 14, "bold"), 
                                         bg="#F8FAFC", fg="#F59E0B")
        self.success_rate_label.pack(anchor="w", padx=10, pady=(0, 8))
        
        # Карточка 4: Последняя активность системы
        card4 = tk.Frame(stats_row, bg="#F8FAFC", relief="solid", bd=1)
        card4.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        tk.Label(card4, text="Последняя активность:", font=("Arial", 9), 
                bg="#F8FAFC", fg="#6B7280").pack(anchor="w", padx=10, pady=(8, 2))
        self.last_activity_label = tk.Label(card4, text="Нет данных", font=("Arial", 14, "bold"), 
                                          bg="#F8FAFC", fg="#6B7280")
        self.last_activity_label.pack(anchor="w", padx=10, pady=(0, 8))
    
    def create_event_log_panel(self, parent):
        """
        Создание панели журнала событий безопасности
        
        Включает:
        - Заголовок с функциями экспорта
        - Таблицу событий с сортировкой и фильтрацией
        - Цветовую индикацию статусов событий
        
        Аргументы:
            parent (tk.Widget): Родительский контейнер
        """
        # Контейнер журнала событий
        log_container = tk.Frame(parent, bg="white", relief="raised", bd=2)
        log_container.pack(fill="both", expand=True)
        
        # Заголовок с кнопками управления
        self.create_event_log_header(log_container)
        
        # Таблица событий с прокруткой
        self.initialize_events_table(log_container)
    
    def create_event_log_header(self, parent):
        """
        Создание заголовка журнала событий с функциями экспорта
        
        Включает:
        - Название секции
        - Кнопку экспорта отчетов для соответствия требованиям
        
        Аргументы:
            parent (tk.Widget): Родительский контейнер
        """
        # Заголовок журнала событий
        log_header = tk.Frame(parent, bg=SECOND_COLOR, height=40)
        log_header.pack(fill="x")
        log_header.pack_propagate(False)
        
        # Название секции
        log_title = tk.Label(log_header, text="ЖУРНАЛ СОБЫТИЙ БЕЗОПАСНОСТИ", 
                           font=("Arial", 12, "bold"), bg=SECOND_COLOR, fg=TEXT_COLOR)
        log_title.pack(side="left", expand=True)
        
        # Кнопка экспорта отчетов
        export_btn = tk.Button(log_header, text="Экспорт отчета", 
                             font=("Arial", 10, "bold"), bg="#10B981", fg=TEXT_COLOR,
                             relief="flat", padx=15, pady=6, command=self.export_security_report)
        export_btn.pack(side="right", padx=(5, 15))
    
    def initialize_events_table(self, parent):
        """
        Создание таблицы событий безопасности
        
        Таблица включает колонки:
        - Время: Временная метка события
        - Тип события: Категория события безопасности
        - ID пользователя: Идентификатор при попытках распознавания
        - Результат: Статус выполнения операции
        - Схожесть: Расстояние схожести для биометрического распознавания (меньше = лучше)
        
        Аргументы:
            parent (tk.Widget): Родительский контейнер
        """
        # Контейнер содержимого журнала
        log_content = tk.Frame(parent, bg="white")
        log_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Определение структуры таблицы
        columns = ("Время", "Тип события", "ID пользователя", "Результат", "Схожесть")
        self.events_tree = ttk.Treeview(log_content, columns=columns, show="headings")
        
        # Настройка заголовков и ширины колонок
        for col in columns:
            self.events_tree.heading(col, text=col)
        
        # Оптимизированная ширина колонок для читаемости
        self.events_tree.column("Время", width=120)
        self.events_tree.column("Тип события", width=180)
        self.events_tree.column("ID пользователя", width=120)
        self.events_tree.column("Результат", width=100)
        self.events_tree.column("Схожесть", width=100)
        
        # Вертикальная прокрутка для больших объемов данных
        scrollbar_events = ttk.Scrollbar(log_content, orient="vertical", 
                                        command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=scrollbar_events.set)
        
        # Размещение компонентов
        self.events_tree.pack(side="left", fill="both", expand=True)
        scrollbar_events.pack(side="right", fill="y")
        
        # Настройка цветовой схемы для быстрой идентификации статусов
        self.events_tree.tag_configure("success", background="#F0FDF4")    # Светло-зеленый для успешных
        self.events_tree.tag_configure("failed", background="#FEF2F2")     # Светло-красный для неудачных
        self.events_tree.tag_configure("system", background="#F8FAFC")     # Светло-серый для системных
        
        # Загрузка начальных данных
        self.reload_audit_data()
    
    def reload_audit_data(self):
        """
        Перезагрузка всех данных аудита с обновлением интерфейса
        
        Синхронизирует интерфейс с актуальным состоянием базы данных аудита,
        обновляя как статистические показатели, так и журнал событий.
        """
        try:
            # Получение статистики за последние 24 часа
            stats = self.audit.generate_security_statistics(days=1)
            if stats:
                self.refresh_security_metrics(stats)
                self.refresh_events_display(stats)
        except Exception as e:
            print(f"Ошибка обновления данных аудита безопасности: {e}")
    
    def refresh_security_metrics(self, stats):
        """
        Обновление статистических показателей безопасности
        
        Вычисляет и отображает ключевые показатели производительности на основе
        данных из системы аудита за заданный период.
        
        Аргументы:
            stats (dict): Статистические данные из логгера аудита
        """
        # Инициализация счетчиков
        total_attempts = 0
        successful = 0
        
        # Подсчет статистики по типам событий
        for stat in stats['general_stats']:
            event_type, result, count, avg_distance = stat
            if event_type == 'recognition_attempt':
                total_attempts += count
                if result == 'success':
                    successful += count
        
        # Вычисление процента эффективности
        success_rate = (successful / total_attempts * 100) if total_attempts > 0 else 0
        
        # Определение временной метки последней активности
        last_activity = "Нет данных"
        if stats['recent_events']:
            last_timestamp = stats['recent_events'][0][0]
            last_time = datetime.datetime.fromisoformat(last_timestamp)
            last_activity = last_time.strftime('%H:%M:%S')
        
        # Обновление показателей панели управления
        self.total_attempts_label.config(text=str(total_attempts))
        self.successful_label.config(text=str(successful))
        self.success_rate_label.config(text=f"{success_rate:.1f}%")
        self.last_activity_label.config(text=last_activity)
    
    def refresh_events_display(self, stats):
        """
        Обновление отображения журнала событий безопасности
        
        Загружает и форматирует последние события безопасности для
        отображения в таблице с соответствующей цветовой индикацией.
        
        Аргументы:
            stats (dict): Данные событий из логгера аудита
        """
        # Очистка существующих записей
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        
        # Словарь локализации типов событий
        event_types_localization = {
            'recognition_attempt': 'Попытка распознавания',
            'user_added': 'Добавлен пользователь',
            'user_deleted': 'Удален пользователь',
            'user_photo_updated': 'Обновлено фото',
            'system_start': 'Запуск системы распознавания',
            'camera_start': 'Запуск камеры',
            'camera_stop': 'Остановка камеры',
            'encodings_loaded': 'Обновление данных в БД',
            'system_shutdown': 'Завершение работы системы распознавания'
        }
        
        # Заполнение таблицы новыми событиями
        for event in stats['recent_events']:
            # Форматирование временной метки
            timestamp = datetime.datetime.fromisoformat(event[0])
            formatted_time = timestamp.strftime('%H:%M:%S')
            
            # Локализация типа события
            event_type = event_types_localization.get(event[1], event[1])
            
            # Обработка ID пользователя
            user_id = event[2] if event[2] else "—"
            
            # Форматирование результата с эмодзи-индикаторами
            result = "✅ Успех" if event[3] == 'success' else "❌ Неудача"
            
            # Форматирование расстояния схожести (меньше = лучше соответствие)
            distance = f"{event[4]:.3f}" if event[4] is not None else "—"
            
            # Определение цветового тега для строки
            if event[1] == 'recognition_attempt':
                # События распознавания: зеленый для успешных, красный для неудачных
                tag = "success" if event[3] == 'success' else "failed"
            elif event[1] in ['user_added', 'user_deleted', 'user_photo_updated']:
                # События управления пользователями
                tag = "success" if event[3] == 'success' else "failed"
            else:
                # Системные события
                tag = "system"
            
            # Добавление записи в таблицу с цветовой индикацией
            self.events_tree.insert("", "end", 
                                  values=(formatted_time, event_type, user_id, result, distance),
                                  tags=(tag,))
    
    def export_security_report(self):
        """
        Экспорт отчета безопасности в формат CSV
        
        Создает всеобъемлющий отчет всех событий безопасности для:
        - Аудита соответствия требованиям
        - Анализа инцидентов безопасности
        - Архивирования данных
        - Интеграции с внешними системами управления информацией и событиями безопасности
        """
        # Диалог выбора места сохранения отчета
        file_path = filedialog.asksaveasfilename(
            title="Сохранить отчет безопасности",
            defaultextension=".csv",
            filetypes=[("Файлы CSV", "*.csv"), ("Все файлы", "*.*")]
        )
        
        if file_path:
            # Экспорт данных за последнюю неделю (стандартный период для отчетности)
            if self.audit.export_security_report(file_path, days=7):
                messagebox.showinfo("Экспорт завершен", 
                                  f"Отчет безопасности успешно экспортирован:\n{file_path}\n\n"
                                  f"Отчет включает события за последние 7 дней.")
            else:
                messagebox.showerror("Ошибка экспорта", 
                                   "Не удалось создать отчет безопасности!\n"
                                   "Проверьте права доступа к выбранной папке.")
    
    def schedule_automatic_refresh(self):
        """
        Планирование автоматического обновления данных аудита
        
        Устанавливает повторяющийся таймер для обновления интерфейса мониторинга
        в режиме реального времени. Интервал обновления настраивается
        в конфигурации системы.
        """
        # Обновление текущих данных
        self.reload_audit_data()
        
        # Планирование следующего обновления
        self.frame.after(AUDIT_DATA_REFRESH_INTERVAL, self.schedule_automatic_refresh)
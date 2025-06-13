# gui/recognition_widget.py
"""
Модуль виджета распознавания лиц в режиме реального времени
Автор: Студент 4 курса ОмГУ им. Ф.М. Достоевского
ВКР: Автоматизированная система распознавания лиц

Описание:
Виджет распознавания лиц является основным интерфейсом взаимодействия
с системой биометрической идентификации. Обеспечивает обработку
видеопотока с камеры в режиме реального времени и визуализацию результатов распознавания.

Основные функции:
- Управление состоянием веб-камеры
- Обработка видеопотока в режиме реального времени
- Визуализация результатов распознавания
- Система защиты от избыточных срабатываний
- Интеграция с системой аудита безопасности

Архитектурные решения:
- Обработка видео, управляемая событиями, через tkinter.after()
- Временное ограничение для предотвращения избыточных срабатываний
- Управление состоянием для корректного жизненного цикла камеры
"""

import tkinter as tk  # Основная библиотека для создания графического интерфейса
from tkinter import messagebox  # Диалоговые окна для уведомлений пользователя
from PIL import Image, ImageTk  # Библиотеки для обработки и отображения изображений в tkinter
import datetime  # Работа с датой и временем для логирования и контроля задержек
import os  # Операции с файловой системой
import cv2  # Библиотека компьютерного зрения для обработки видеопотока
from config.settings import *


class FaceRecognitionWidget:
    """
    Виджет распознавания лиц в режиме реального времени
    
    Основной компонент интерфейса для работы с видеопотоком и распознаванием лиц.
    Объединяет в себе:
    - Управление камерой (запуск/остановка)
    - Обработку видеопотока в режиме реального времени
    - Отображение результатов распознавания
    - Контроль частоты распознавания (защита от избыточных срабатываний)
    - Логирование событий безопасности
    
    Архитектурные особенности:
    - Неблокирующая обработка видео через tkinter.after()
    - Система таймеров для предотвращения избыточных срабатываний
    - Интеграция с системой аудита безопасности
    - Корректное управление ресурсами камеры
    """
    
    def __init__(self, parent_notebook, camera_manager, face_engine, db):
        """
        Инициализация виджета распознавания лиц
        
        Аргументы:
            parent_notebook (ttk.Notebook): Родительский контейнер вкладок
            camera_manager (CameraController): Контроллер управления веб-камерой
            face_engine (FaceAnalysisEngine): Движок анализа лиц
            db (DatabaseManager): Менеджер базы данных пользователей
        """
        # Сохранение ссылок на внешние компоненты системы
        self.notebook = parent_notebook  # Контейнер вкладок для размещения виджета
        self.camera_manager = camera_manager  # Контроллер веб-камеры
        self.face_engine = face_engine  # Движок анализа лиц
        self.db = db  # База данных зарегистрированных пользователей
        
        # Система контроля частоты распознавания (временное ограничение)
        # Предотвращает избыточные срабатывания и переполнение логов
        self.last_successful_recognition_timestamp = None  # Время последнего успешного распознавания
        self.last_unknown_face_detection_timestamp = None  # Время последней детекции неизвестного лица
        self.user_info_display_timer = None  # Таймер для автоматической очистки информации
        
        # Поставщик системы аудита (устанавливается через внедрение зависимостей)
        self.audit_logger_provider = None
        
        # Инициализация графического интерфейса
        self.initialize_user_interface()
    
    def set_audit_logger(self, audit_provider_function):
        """
        Установка поставщика системы аудита через внедрение зависимостей
        
        Этот паттерн позволяет виджету получать доступ к системе аудита
        без жесткой зависимости, что улучшает тестируемость кода.
        
        Аргументы:
            audit_provider_function (callable): Функция, возвращающая экземпляр логгера аудита
        """
        self.audit_logger_provider = audit_provider_function
    
    def initialize_user_interface(self):
        """
        Создание графического интерфейса виджета распознавания
        
        Интерфейс состоит из двух основных панелей:
        1. Левая панель: видеопоток с камеры и кнопки управления
        2. Правая панель: информация о распознанном пользователе
        """
        # Создание основного фрейма вкладки с фирменным цветом
        self.frame = tk.Frame(self.notebook, bg=THEME_COLOR)
        self.notebook.add(self.frame, text="  Распознавание лиц  ")
        
        # Основной контейнер с отступами для эстетичного вида
        main_container = tk.Frame(self.frame, bg=THEME_COLOR)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Создание двухпанельного интерфейса
        self.create_camera_panel(main_container)  # Левая панель - камера
        self.create_info_panel(main_container)    # Правая панель - информация
    
    def create_camera_panel(self, parent):
        """
        Создание панели управления камерой и отображения видеопотока
        
        Панель включает:
        - Область отображения видеопотока (480x360 пикселей)
        - Кнопки запуска и остановки камеры
        - Заголовок с названием секции
        
        Аргументы:
            parent (tk.Widget): Родительский контейнер для размещения панели
        """
        # Создание левой панели с фиксированной шириной
        left_panel = tk.Frame(parent, bg="white", relief="raised", bd=2, width=500)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)  # Предотвращение автоматического изменения размера
        
        # Заголовок панели с фирменным стилем
        video_header = tk.Frame(left_panel, bg=SECOND_COLOR, height=40)
        video_header.pack(fill="x")
        video_header.pack_propagate(False)
        
        video_title = tk.Label(video_header, text="КАМЕРА", 
                              font=("Arial", 12, "bold"), bg=SECOND_COLOR, fg=TEXT_COLOR)
        video_title.pack(expand=True)
        
        # Контейнер для отображения видеопотока
        # Размер 480x360 обеспечивает соотношение сторон 4:3 для веб-камер
        video_container = tk.Frame(left_panel, bg="black", width=480, height=360)
        video_container.pack(padx=10, pady=10)
        video_container.pack_propagate(False)
        
        # Метка для отображения кадров видео или сообщений о состоянии
        self.video_label = tk.Label(video_container, text="Камера не запущена", 
                                   bg="black", fg="white", font=("Arial", 12))
        self.video_label.pack(fill="both", expand=True)
        
        # Панель кнопок управления камерой
        self.create_camera_controls(left_panel)
    
    def create_camera_controls(self, parent):
        """
        Создание кнопок управления состоянием камеры
        
        Кнопки:
        - "Запуск": инициирует захват видео с веб-камеры
        - "Стоп": останавливает видеопоток и освобождает ресурсы камеры
        
        Кнопки блокируются/разблокируются в зависимости от состояния камеры
        для предотвращения некорректных операций.
        
        Аргументы:
            parent (tk.Widget): Родительский контейнер для кнопок
        """
        # Контейнер для кнопок с фиксированной высотой
        controls = tk.Frame(parent, bg="white", height=50)
        controls.pack(fill="x", padx=10, pady=(0, 10))
        controls.pack_propagate(False)
        
        # Кнопка запуска камеры (изначально активна)
        self.start_button = tk.Button(controls, text="Запуск", 
                                     font=("Arial", 10, "bold"), bg="#10B981", fg=TEXT_COLOR,
                                     relief="flat", padx=GUI_BUTTON_PADDING_X, pady=GUI_BUTTON_PADDING_Y, 
                                     command=self.start_camera)
        self.start_button.pack(side="left", padx=(0, 5))
        
        # Кнопка остановки камеры (изначально заблокирована)
        self.stop_button = tk.Button(controls, text="Стоп", 
                                    font=("Arial", 10, "bold"), bg="#EF4444", fg=TEXT_COLOR,
                                    relief="flat", padx=GUI_BUTTON_PADDING_X, pady=GUI_BUTTON_PADDING_Y, 
                                    command=self.stop_camera, state="disabled")
        self.stop_button.pack(side="left", padx=(0, 5))
    
    def create_info_panel(self, parent):
        """
        Создание панели информации о распознанном пользователе
        
        Панель включает:
        - Статус распознавания
        - Информационные поля пользователя
        - Область отображения фотографии
        
        Аргументы:
            parent (tk.Widget): Родительский контейнер для панели
        """
        # Правая панель с информацией о пользователе
        right_panel = tk.Frame(parent, bg="white", relief="raised", bd=2)
        right_panel.pack(side="right", fill="both", expand=True)
        
        info_content = tk.Frame(right_panel, bg="white")
        info_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Заголовок информационной панели
        header = tk.Label(info_content, text="РАСПОЗНАННЫЙ ПОЛЬЗОВАТЕЛЬ", 
                         font=("Arial", 14, "bold"), bg="white", fg="#374151")
        header.pack(anchor="w", pady=(0, 15))
        
        # Статус распознавания
        self.status_label = tk.Label(info_content, text="⏳ Ожидание...", 
                                    font=("Arial", 16, "bold"), bg="white", fg="#6B7280")
        self.status_label.pack(anchor="w", pady=(0, 15))
        
        # Информация о пользователе
        self.create_user_info_section(info_content)
        
        # Секция отображения фотографии
        self.create_photo_display_section(info_content)
    
    def create_user_info_section(self, parent):
        """
        Создание секции с информацией о пользователе
        
        Включает поля:
        - ID пользователя
        - Имя пользователя
        
        Аргументы:
            parent (tk.Widget): Родительский контейнер
        """
        # Контейнер для информации с рамкой
        info_container = tk.Frame(parent, bg="#F9FAFB", relief="solid", bd=1)
        info_container.pack(fill="x", pady=(0, 15))
        
        # Поле ID пользователя
        id_frame = tk.Frame(info_container, bg="#F9FAFB")
        id_frame.pack(fill="x", padx=GUI_CARD_PADDING, pady=8)
        
        tk.Label(id_frame, text="ID:", font=("Arial", 11, "bold"), 
                bg="#F9FAFB", fg="#374151").pack(side="left")
        self.user_id_label = tk.Label(id_frame, text="—", font=("Arial", 11), 
                                     bg="#F9FAFB", fg="#6B7280")
        self.user_id_label.pack(side="right")
        
        # Поле имени пользователя
        name_frame = tk.Frame(info_container, bg="#F9FAFB")
        name_frame.pack(fill="x", padx=GUI_CARD_PADDING, pady=8)
        
        tk.Label(name_frame, text="Имя:", font=("Arial", 11, "bold"), 
                bg="#F9FAFB", fg="#374151").pack(side="left")
        self.name_label = tk.Label(name_frame, text="—", font=("Arial", 11), 
                                  bg="#F9FAFB", fg="#6B7280")
        self.name_label.pack(side="right")
    
    def create_photo_display_section(self, parent):
        """
        Создание секции отображения фотографии пользователя
        
        Аргументы:
            parent (tk.Widget): Родительский контейнер
        """
        photo_frame = tk.Frame(parent, bg="white")
        photo_frame.pack(fill="x")
        
        tk.Label(photo_frame, text="Фотография:", font=("Arial", 11, "bold"), 
                bg="white", fg="#374151").pack(anchor="w", pady=(0, 8))
        
        # Контейнер для фотографии с фиксированным размером
        photo_container = tk.Frame(photo_frame, bg="#F3F4F6", relief="solid", bd=1, 
                                  width=USER_PHOTO_DISPLAY_SIZE[0], height=USER_PHOTO_DISPLAY_SIZE[1])
        photo_container.pack(pady=(0, 10))
        photo_container.pack_propagate(False)
        
        self.photo_display = tk.Label(photo_container, text="Нет фото", 
                                     bg="#F3F4F6", font=("Arial", 10), fg="#6B7280")
        self.photo_display.pack(fill="both", expand=True)
    
    def start_camera(self):
        """
        Запуск системы видеозахвата и начало обработки кадров
        
        Процедура запуска:
        1. Инициализация камеры через контроллер камеры
        2. Обновление состояния кнопок интерфейса
        3. Логирование события в систему аудита
        4. Запуск цикла обработки кадров
        
        В случае ошибки подключения к камере показывается предупреждение.
        """
        # Попытка инициализации камеры
        if self.camera_manager.start_camera():
            # Успешный запуск - обновление интерфейса
            self.start_button.config(state="disabled")  # Блокировка кнопки запуска
            self.stop_button.config(state="normal")     # Разблокировка кнопки остановки
            
            # Логирование успешного запуска камеры в систему аудита
            audit = self.audit_logger_provider() if self.audit_logger_provider else None
            if audit:
                audit.log_system_security_event("camera_start", "success")
            
            # Запуск цикла обработки видеокадров
            self.process_video_frame()
        else:
            # Ошибка запуска - логирование и уведомление пользователя
            audit = self.audit_logger_provider() if self.audit_logger_provider else None
            if audit:
                audit.log_system_security_event("camera_start", "failed")
            
            # Показ диалогового окна с ошибкой
            messagebox.showerror("Ошибка", "Не удалось подключиться к камере!")
    
    def stop_camera(self):
        """
        Остановка камеры и сброс состояния интерфейса
        
        Выполняет полную очистку:
        1. Остановку захвата видео
        2. Отмену всех активных таймеров
        3. Сброс временных меток
        4. Обновление состояния интерфейса
        5. Логирование события
        """
        # Остановка камеры
        self.camera_manager.stop_camera()
        
        # Очистка всех активных таймеров
        if self.user_info_display_timer:
            self.frame.after_cancel(self.user_info_display_timer)
            self.user_info_display_timer = None
        
        # Сброс временных меток системы защиты от избыточных срабатываний
        self.last_successful_recognition_timestamp = None
        self.last_unknown_face_detection_timestamp = None
        
        # Обновление состояния кнопок
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        # Сброс отображения
        self.video_label.config(image="", text="Камера остановлена")
        self.clear_user_display_info()
        
        # Логирование остановки камеры
        audit = self.audit_logger_provider() if self.audit_logger_provider else None
        if audit:
            audit.log_system_security_event("camera_stop", "success")
    
    def process_video_frame(self):
        """
        Основной цикл обработки видеокадров в режиме реального времени
        
        Цикл выполняется непрерывно пока камера активна и включает:
        1. Захват кадра с камеры
        2. Анализ лиц на кадре с помощью движка лиц
        3. Проверку ограничений по времени (защита от избыточных срабатываний)
        4. Отрисовку прямоугольников вокруг лиц
        5. Обновление информации о пользователе
        6. Планирование следующей итерации
        
        Использует неблокирующий подход через tkinter.after() для
        предотвращения замораживания интерфейса.
        """
        # Проверка активности камеры
        if not self.camera_manager.is_camera_active():
            return  # Выход из цикла если камера остановлена
        
        # Захват кадра с веб-камеры
        frame = self.camera_manager.capture_frame()
        if frame is None:
            # Кадр не получен - планируем повторную попытку
            self.frame.after(VIDEO_FRAME_PROCESSING_INTERVAL, self.process_video_frame)
            return
        
        # Анализ лиц на текущем кадре
        recognized_faces = self.face_engine.detect_and_recognize_faces(frame, FRAME_SCALE)
        
        # Получение текущего времени для контроля частоты распознавания
        current_time = datetime.datetime.now()
        recognized_user = None  # Переменная для хранения данных распознанного пользователя
        
        # Проверка временных ограничений для предотвращения избыточных срабатываний
        can_recognize_known = self._is_known_user_cooldown_expired(current_time)
        can_recognize_unknown = self._is_unknown_user_cooldown_expired(current_time)
        
        # Обработка каждого обнаруженного лица на кадре
        for face_info in recognized_faces:
            # Анализ конкретного лица с учетом временных ограничений
            name, color = self._analyze_detected_face(face_info, current_time, 
                                                     can_recognize_known, can_recognize_unknown)
            
            # Отрисовка прямоугольника вокруг лица с соответствующим цветом
            self.face_engine.draw_detection_rectangle(frame, face_info, color, name)
            
            # Если лицо распознано и прошло достаточно времени - обновляем информацию
            if face_info['is_known'] and can_recognize_known:
                user_data = self.db.get_user_by_id(face_info['user_id'])
                if user_data:
                    recognized_user = user_data
                    self.last_successful_recognition_timestamp = current_time
                    self._schedule_user_info_reset()  # Планируем очистку через заданное время
        
        # Обновление информационной панели
        if recognized_user:
            self.display_recognized_user_info(recognized_user)
        elif not recognized_faces and not self.user_info_display_timer:
            # Если лиц нет и нет активного таймера - очищаем информацию
            self.clear_user_display_info()
        
        # Отображение обработанного кадра в интерфейсе
        self._render_video_frame(frame)
        
        # Планирование следующей итерации
        self.frame.after(VIDEO_FRAME_PROCESSING_INTERVAL, self.process_video_frame)
    
    def _is_known_user_cooldown_expired(self, current_time):
        """
        Проверка истечения периода ожидания для распознанных пользователей
        
        Защитный механизм против избыточного логирования одного и того же
        пользователя. После успешного распознавания система игнорирует
        последующие распознавания в течение RECOGNITION_DELAY секунд.
        
        Аргументы:
            current_time (datetime): Текущее время для сравнения
            
        Возвращает:
            bool: True если можно выполнить распознавание, False если нужно подождать
        """
        if not self.last_successful_recognition_timestamp:
            return True  # Первое распознавание всегда разрешено
        
        # Вычисление времени, прошедшего с последнего успешного распознавания
        elapsed_seconds = (current_time - self.last_successful_recognition_timestamp).total_seconds()
        return elapsed_seconds >= RECOGNITION_DELAY
    
    def _is_unknown_user_cooldown_expired(self, current_time):
        """
        Проверка истечения периода ожидания для неизвестных лиц
        
        Аналогичный механизм защиты для неизвестных лиц с отдельным
        интервалом ожидания для снижения нагрузки на систему.
        
        Аргументы:
            current_time (datetime): Текущее время для сравнения
            
        Возвращает:
            bool: True если можно обработать неизвестное лицо
        """
        if not self.last_unknown_face_detection_timestamp:
            return True  # Первая детекция всегда разрешена
        
        elapsed_seconds = (current_time - self.last_unknown_face_detection_timestamp).total_seconds()
        return elapsed_seconds >= UNKNOWN_FACE_DELAY
    
    def _analyze_detected_face(self, face_info, current_time, can_recognize_known, can_recognize_unknown):
        """
        Анализ обнаруженного лица и определение визуального представления
        
        Логика определения цветовой схемы и подписей:
        1. Известное лицо + разрешено распознавание → зеленая рамка + имя + логирование
        2. Известное лицо + ожидание → желтая рамка + таймер
        3. Неизвестное лицо + разрешено → красная рамка + логирование
        4. Неизвестное лицо + ожидание → желтая рамка + таймер
        
        Аргументы:
            face_info (dict): Информация о лице с результатами распознавания
            current_time (datetime): Текущее время
            can_recognize_known (bool): Разрешено ли распознавание известных лиц
            can_recognize_unknown (bool): Разрешено ли обработка неизвестных лиц
            
        Возвращает:
            tuple: (название_для_отображения, цвет_рамки_BGR)
        """
        # Получение ссылки на систему аудита для логирования
        audit = self.audit_logger_provider() if self.audit_logger_provider else None
        
        if face_info['is_known']:
            # Обработка распознанного пользователя
            if can_recognize_known:
                # Разрешено логирование - записываем успешное распознавание
                # Передаем расстояние схожести в систему аудита (меньше = лучше соответствие)
                if audit:
                    audit.log_face_recognition_attempt(face_info['user_id'], True, face_info['distance'])
                
                # Получение имени пользователя из базы данных
                user_data = self.db.get_user_by_id(face_info['user_id'])
                name = user_data[2] if user_data else "Неизвестно"
                color = (0, 255, 0)  # Зеленый цвет рамки (формат BGR)
            else:
                # Период ожидания - показываем оставшееся время
                time_left = RECOGNITION_DELAY - (current_time - self.last_successful_recognition_timestamp).total_seconds()
                name = f"{time_left:.1f}s"  # Форматирование до одного знака после запятой
                color = (0, 255, 255)  # Желтый цвет рамки
        else:
            # Обработка неизвестного лица
            if can_recognize_unknown:
                # Разрешено логирование - записываем неудачную попытку
                # Передаем расстояние схожести для анализа подозрительной активности
                if audit:
                    audit.log_face_recognition_attempt(None, False, face_info['distance'])
                
                # Обновляем время последней детекции неизвестного лица
                self.last_unknown_face_detection_timestamp = current_time
                name = ""  # Не показываем текст для неизвестных лиц
                color = (0, 0, 255)  # Красный цвет рамки
            else:
                # Период ожидания для неизвестных лиц
                time_left = UNKNOWN_FACE_DELAY - (current_time - self.last_unknown_face_detection_timestamp).total_seconds()
                name = f"{time_left:.1f}s"
                color = (0, 255, 255)  # Желтый цвет рамки
        
        return name, color
    
    def _schedule_user_info_reset(self):
        """
        Планирование автоматической очистки информации о пользователе
        
        Устанавливает таймер для автоматической очистки информации
        через заданный интервал для улучшения пользовательского опыта.
        """
        if self.user_info_display_timer:
            self.frame.after_cancel(self.user_info_display_timer)
        
        self.user_info_display_timer = self.frame.after(
            USER_INFO_AUTO_CLEAR_DELAY, 
            self.clear_user_display_info
        )
    
    def _render_video_frame(self, frame):
        """
        Отображение видеокадра в интерфейсе
        
        Конвертирует кадр OpenCV в формат tkinter и отображает в метке.
        
        Аргументы:
            frame (numpy.ndarray): Видеокадр в формате BGR
        """
        # Конвертация BGR → RGB для корректного отображения цветов
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Создание объекта изображения PIL
        pil_image = Image.fromarray(rgb_frame)
        
        # Конвертация в формат tkinter
        photo = ImageTk.PhotoImage(pil_image)
        
        # Отображение в метке
        self.video_label.config(image=photo, text="")
        self.video_label.image = photo  # Сохранение ссылки для предотвращения сборки мусора
    
    def display_recognized_user_info(self, user_data):
        """
        Отображение информации о распознанном пользователе
        
        Обновляет все элементы интерфейса информацией о пользователе:
        - Статус с временной меткой
        - ID и имя пользователя  
        - Фотография пользователя
        
        Аргументы:
            user_data (tuple): Данные пользователя из базы данных
        """
        user_id = user_data[1]
        name = user_data[2]
        photo_path = user_data[3]
        
        # Обновление статуса с временной меткой
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        self.status_label.config(text=f"✅ Распознан в {current_time}", fg="#10B981")
        
        # Обновление информационных полей
        self.user_id_label.config(text=user_id)
        self.name_label.config(text=name)
        
        # Загрузка и отображение фотографии пользователя
        if photo_path and os.path.exists(photo_path):
            try:
                # Загрузка и масштабирование фотографии
                pil_image = Image.open(photo_path)
                pil_image = pil_image.resize(USER_PHOTO_DISPLAY_SIZE, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(pil_image)
                
                # Отображение фотографии
                self.photo_display.config(image=photo, text="")
                self.photo_display.image = photo
                
            except Exception as e:
                print(f"Ошибка загрузки фотографии пользователя: {e}")
                self.photo_display.config(image="", text="Ошибка\nзагрузки", 
                                        font=("Arial", 9), fg="#EF4444")
        else:
            # Фотография не найдена
            self.photo_display.config(image="", text="Фото\nне найдено", 
                                    font=("Arial", 9), fg="#6B7280")
    
    def clear_user_display_info(self):
        """
        Очистка отображаемой информации о пользователе
        
        Сбрасывает все элементы интерфейса в состояние ожидания.
        """
        # Сброс статуса
        self.status_label.config(text="⏳ Ожидание...", fg="#6B7280")
        
        # Сброс информационных полей
        self.user_id_label.config(text="—")
        self.name_label.config(text="—")
        
        # Сброс отображения фотографии
        self.photo_display.config(image="", text="Нет фото", 
                                 font=("Arial", 10), fg="#6B7280")
        
        # Сброс таймера
        if self.user_info_display_timer:
            self.user_info_display_timer = None
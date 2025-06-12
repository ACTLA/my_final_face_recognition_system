# core/database_manager.py
"""
Модуль управления базой данных пользователей
Автор: Студент 4 курса ОмГУ им. Ф.М. Достоевского
ВКР: Автоматизированная система распознавания лиц

Описание:
Менеджер базы данных обеспечивает безопасное хранение и управление
данными зарегистрированных пользователей системы распознавания лиц.
Использует SQLite для локального хранения биометрических данных.

Основные функции:
- Создание и инициализация структуры БД
- Операции создания, чтения, обновления и удаления (CRUD) с пользователями
- Сериализация биометрических отпечатков лиц
- Управление файлами фотографий

Структура таблицы users:
- id: Автоинкрементный первичный ключ
- user_id: Уникальный текстовый идентификатор пользователя
- name: Имя пользователя
- photo_path: Путь к файлу фотографии
- face_encoding: Сериализованный биометрический отпечаток (BLOB)
"""

import sqlite3  # Встроенная СУБД для локального хранения данных
import os  # Операции с файловой системой
import pickle  # Сериализация объектов Python для хранения в БД
from config.settings import USERS_DB


class DatabaseManager:
    """
    Менеджер базы данных пользователей системы распознавания лиц
    
    Класс инкапсулирует всю логику работы с базой данных пользователей,
    обеспечивая безопасное хранение персональных данных и биометрических
    отпечатков лиц в соответствии с принципами информационной безопасности.
    
    Использует SQLite как встроенную СУБД Python для обеспечения:
    - Локального хранения данных без внешних зависимостей
    - Транзакций ACID для целостности данных
    - Простого развертывания системы
    
    Биометрические отпечатки сериализуются через pickle для хранения
    128-мерных векторов признаков лиц в двоичном формате.
    """
    
    def __init__(self, db_name=USERS_DB):
        """
        Инициализация менеджера базы данных
        
        Создает подключение к базе данных SQLite и инициализирует
        структуру таблиц при первом запуске системы.
        
        Аргументы:
            db_name (str): Имя файла базы данных (по умолчанию из настроек)
        """
        self.db_name = db_name  # Сохранение пути к файлу БД
        self.initialize_database_structure()  # Создание структуры при первом запуске
    
    def initialize_database_structure(self):
        """
        Создание структуры базы данных при первом запуске
        
        Инициализирует таблицу пользователей с необходимыми полями
        для хранения персональных данных и биометрических отпечатков.
        Использует IF NOT EXISTS для безопасного повторного запуска.
        
        Структура таблицы users:
        - id: INTEGER PRIMARY KEY AUTOINCREMENT - уникальный ID записи
        - user_id: TEXT UNIQUE NOT NULL - идентификатор пользователя (логин)
        - name: TEXT NOT NULL - полное имя пользователя
        - photo_path: TEXT - путь к файлу с фотографией
        - face_encoding: BLOB - сериализованный биометрический отпечаток
        """
        # Установка соединения с базой данных
        # SQLite автоматически создает файл БД если он не существует
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        
        # Создание таблицы пользователей с ограничениями целостности
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                photo_path TEXT,
                face_encoding BLOB
            )
        ''')
        
        # Фиксация изменений в базе данных
        connection.commit()
        connection.close()
    
    def add_user(self, user_id, name, photo_path, face_encoding=None):
        """
        Добавление нового пользователя в систему
        
        Регистрирует нового пользователя с его персональными данными
        и биометрическим отпечатком лица. Обеспечивает уникальность
        пользователей по полю user_id.
        
        Аргументы:
            user_id (str): Уникальный идентификатор пользователя
            name (str): Полное имя пользователя
            photo_path (str): Путь к файлу фотографии
            face_encoding (numpy.ndarray, необязательно): 128-мерный вектор признаков лица
            
        Возвращает:
            bool: True если пользователь успешно добавлен, False если уже существует
            
        Исключения:
            sqlite3.Error: При ошибках работы с базой данных
        """
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        
        try:
            # Сериализация биометрического отпечатка для хранения в БД
            encoding_blob = None
            if face_encoding is not None:
                # Преобразование массива numpy в двоичные данные через pickle
                encoding_blob = pickle.dumps(face_encoding)
            
            # Вставка нового пользователя с проверкой уникальности
            cursor.execute('''
                INSERT INTO users (user_id, name, photo_path, face_encoding) 
                VALUES (?, ?, ?, ?)
            ''', (user_id, name, photo_path, encoding_blob))
            
            # Фиксация транзакции
            connection.commit()
            connection.close()
            return True
            
        except sqlite3.IntegrityError:
            # Нарушение ограничения уникальности user_id
            connection.close()
            return False
    
    def get_all_facial_encodings(self):
        """
        Получение всех биометрических отпечатков для распознавания
        
        Извлекает и десериализует все биометрические отпечатки лиц
        зарегистрированных пользователей для загрузки в движок распознавания.
        
        Возвращает:
            tuple: Кортеж из двух синхронизированных списков:
                - encodings (list): Список массивов numpy с отпечатками лиц
                - user_ids (list): Список соответствующих ID пользователей
                
        Примечание:
            Списки синхронизированы по индексам: encodings[i] соответствует user_ids[i]
        """
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        
        # Выборка только записей с биометрическими отпечатками
        cursor.execute('SELECT user_id, face_encoding FROM users WHERE face_encoding IS NOT NULL')
        results = cursor.fetchall()
        
        # Списки для хранения десериализованных данных
        encodings = []
        user_ids = []
        
        # Десериализация каждого биометрического отпечатка
        for user_id, encoding_blob in results:
            if encoding_blob:
                # Восстановление массива numpy из двоичных данных
                encoding = pickle.loads(encoding_blob)
                encodings.append(encoding)
                user_ids.append(user_id)
        
        connection.close()
        return encodings, user_ids
    
    def update_user_facial_encoding(self, user_id, face_encoding):
        """
        Обновление биометрического отпечатка пользователя
        
        Заменяет существующий биометрический отпечаток на новый,
        например, при обновлении фотографии пользователя.
        
        Аргументы:
            user_id (str): Идентификатор пользователя для обновления
            face_encoding (numpy.ndarray): Новый 128-мерный вектор признаков лица
            
        Возвращает:
            bool: True если обновление успешно, False если пользователь не найден
        """
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        
        # Сериализация нового биометрического отпечатка
        encoding_blob = pickle.dumps(face_encoding)
        
        # Обновление записи пользователя
        cursor.execute('UPDATE users SET face_encoding = ? WHERE user_id = ?', 
                      (encoding_blob, user_id))
        
        # Проверка количества затронутых строк
        rows_affected = cursor.rowcount
        
        connection.commit()
        connection.close()
        
        return rows_affected > 0
    
    def get_user_by_id(self, user_id):
        """
        Получение полной информации о пользователе по ID
        
        Извлекает все данные пользователя для отображения в интерфейсе
        или для других операций системы.
        
        Аргументы:
            user_id (str): Идентификатор пользователя
            
        Возвращает:
            tuple или None: Кортеж с данными пользователя (id, user_id, name, photo_path, face_encoding)
                          или None если пользователь не найден
        """
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        
        # Поиск пользователя по уникальному идентификатору
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        connection.close()
        return user
    
    def get_all_users(self):
        """
        Получение списка всех зарегистрированных пользователей
        
        Извлекает полную информацию о всех пользователях для отображения
        в интерфейсе управления.
        
        Возвращает:
            list: Список кортежей с данными всех пользователей
        """
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        
        # Выборка всех пользователей
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        
        connection.close()
        return users
    
    def remove_user(self, user_id):
        """
        Удаление пользователя из системы
        
        Полностью удаляет пользователя из базы данных и связанные файлы.
        Обеспечивает целостность данных путем каскадного удаления файлов.
        
        Аргументы:
            user_id (str): Идентификатор пользователя для удаления
            
        Возвращает:
            bool: True если пользователь успешно удален, False если не найден
        """
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        
        # Получение пути к фотографии перед удалением записи
        cursor.execute('SELECT photo_path FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            photo_path = result[0]
            
            # Удаление файла фотографии если он существует
            if photo_path and os.path.exists(photo_path):
                try:
                    os.remove(photo_path)
                except OSError:
                    # Логирование ошибки удаления файла (файл может быть заблокирован)
                    pass
            
            # Удаление записи пользователя из базы данных
            cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
            connection.commit()
            connection.close()
            return True
        else:
            # Пользователь не найден
            connection.close()
            return False
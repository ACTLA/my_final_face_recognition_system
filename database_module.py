import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name="users.db"):
        # Инициализация базы данных
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        # Создание таблицы пользователей если её нет
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Создаем таблицу с простой структурой
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                photo_path TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, name, photo_path):
        # Добавление нового пользователя
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            # Вставляем нового пользователя
            cursor.execute('''
                INSERT INTO users (user_id, name, photo_path) 
                VALUES (?, ?, ?)
            ''', (user_id, name, photo_path))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Если пользователь уже существует
            conn.close()
            return False
    
    def get_user(self, user_id):
        # Получение пользователя по ID
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        return user
    
    def get_all_users(self):
        # Получение всех пользователей
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        
        conn.close()
        return users
    
    def delete_user(self, user_id):
        # Удаление пользователя
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Получаем путь к фото для удаления
        cursor.execute('SELECT photo_path FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            photo_path = result[0]
            # Удаляем файл фото если существует
            if photo_path and os.path.exists(photo_path):
                os.remove(photo_path)
            
            # Удаляем пользователя из БД
            cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
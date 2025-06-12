# core/database_manager.py
import sqlite3
import os
import pickle
from config.settings import USERS_DB

class DatabaseManager:
    """Менеджер базы данных пользователей"""
    
    def __init__(self, db_name=USERS_DB):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Создание таблицы пользователей"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                photo_path TEXT,
                face_encoding BLOB
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, name, photo_path, face_encoding=None):
        """Добавление нового пользователя"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            encoding_blob = None
            if face_encoding is not None:
                encoding_blob = pickle.dumps(face_encoding)
            
            cursor.execute('''
                INSERT INTO users (user_id, name, photo_path, face_encoding) 
                VALUES (?, ?, ?, ?)
            ''', (user_id, name, photo_path, encoding_blob))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
    
    def get_all_encodings(self):
        """Получение всех кодировок лиц"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id, face_encoding FROM users WHERE face_encoding IS NOT NULL')
        results = cursor.fetchall()
        
        encodings = []
        user_ids = []
        
        for user_id, encoding_blob in results:
            if encoding_blob:
                encoding = pickle.loads(encoding_blob)
                encodings.append(encoding)
                user_ids.append(user_id)
        
        conn.close()
        return encodings, user_ids
    
    def update_user_encoding(self, user_id, face_encoding):
        """Обновление кодировки лица пользователя"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        encoding_blob = pickle.dumps(face_encoding)
        cursor.execute('UPDATE users SET face_encoding = ? WHERE user_id = ?', 
                      (encoding_blob, user_id))
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def get_user(self, user_id):
        """Получение пользователя по ID"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        return user
    
    def get_all_users(self):
        """Получение всех пользователей"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        
        conn.close()
        return users
    
    def delete_user(self, user_id):
        """Удаление пользователя"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT photo_path FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            photo_path = result[0]
            if photo_path and os.path.exists(photo_path):
                os.remove(photo_path)
            
            cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
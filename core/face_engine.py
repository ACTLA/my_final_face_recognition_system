# core/face_engine.py
import cv2
import face_recognition
import numpy as np
from PIL import Image, ImageTk

class FaceRecognitionEngine:
    """Движок распознавания лиц"""
    
    def __init__(self):
        self.known_encodings = []
        self.known_user_ids = []
    
    def load_encodings(self, encodings, user_ids):
        """Загрузка кодировок лиц"""
        self.known_encodings = encodings
        self.known_user_ids = user_ids
        print(f"Загружено кодировок: {len(self.known_encodings)}")
    
    def create_face_encoding(self, image_path):
        """Создание кодировки лица из фотографии"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise Exception("Не удалось загрузить изображение")
            
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_encodings = face_recognition.face_encodings(rgb_image)
            
            if face_encodings:
                return face_encodings[0]
            else:
                raise Exception("Лицо не найдено на фотографии")
                
        except Exception as e:
            raise Exception(f"Ошибка создания кодировки: {str(e)}")
    
    def recognize_faces(self, frame, scale=0.25):
        """Распознавание лиц на кадре"""
        if not self.known_encodings:
            return []
        
        # Уменьшаем кадр для ускорения
        small_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Поиск лиц
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        recognized_faces = []
        
        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(self.known_encodings, face_encoding)
            face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
            
            best_match_index = np.argmin(face_distances)
            confidence = 1 - face_distances[best_match_index]
            
            # Восстанавливаем координаты
            top, right, bottom, left = face_location
            top = int(top / scale)
            right = int(right / scale)
            bottom = int(bottom / scale)
            left = int(left / scale)
            
            recognized_face = {
                'location': (top, right, bottom, left),
                'confidence': confidence,
                'user_id': None,
                'is_known': False
            }
            
            if matches[best_match_index] and confidence > 0.6:
                recognized_face['user_id'] = self.known_user_ids[best_match_index]
                recognized_face['is_known'] = True
            
            recognized_faces.append(recognized_face)
        
        return recognized_faces
    
    def draw_face_rectangle(self, frame, face_info, color, name=""):
        """Рисование рамки вокруг лица"""
        top, right, bottom, left = face_info['location']
        
        # Рисуем рамку
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Добавляем текст если есть имя
        if name.strip():
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), 
                       cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 0), 1)
        
        return frame
# core/face_engine.py
import cv2
import face_recognition
import numpy as np
from PIL import Image, ImageTk
from config.settings import FACE_DISTANCE_THRESHOLD

class FaceRecognitionEngine:
    """Движок распознавания лиц"""
    
    def __init__(self):
        # Списки для хранения известных кодировок лиц и соответствующих ID пользователей
        self.known_encodings = []
        self.known_user_ids = []
    
    def load_encodings(self, encodings, user_ids):
        """Загрузка кодировок лиц из базы данных"""
        # Сохраняем кодировки и соответствующие им ID пользователей
        self.known_encodings = encodings
        self.known_user_ids = user_ids
        print(f"Загружено кодировок: {len(self.known_encodings)}")
    
    def create_face_encoding(self, image_path):
        """Создание кодировки лица из фотографии"""
        try:
            # Загружаем изображение с диска
            image = cv2.imread(image_path)
            if image is None:
                raise Exception("Не удалось загрузить изображение")
            
            # Конвертируем изображение из BGR в RGB формат для face_recognition
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Извлекаем кодировки лиц из изображения
            face_encodings = face_recognition.face_encodings(rgb_image)
            
            if face_encodings:
                # Возвращаем первую найденную кодировку лица
                return face_encodings[0]
            else:
                raise Exception("Лицо не найдено на фотографии")
                
        except Exception as e:
            raise Exception(f"Ошибка создания кодировки: {str(e)}")
    
    def recognize_faces(self, frame, scale=0.25):
        """Распознавание лиц на кадре с камеры"""
        # Если нет загруженных кодировок, возвращаем пустой список
        if not self.known_encodings:
            return []
        
        # Уменьшаем размер кадра для ускорения обработки
        small_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
        
        # Конвертируем кадр из BGR в RGB формат
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Находим все лица на кадре и их местоположения
        face_locations = face_recognition.face_locations(rgb_small_frame)
        
        # Извлекаем кодировки для всех найденных лиц
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        recognized_faces = []  # Список результатов распознавания
        
        # Обрабатываем каждое найденное лицо
        for face_encoding, face_location in zip(face_encodings, face_locations):
            # Вычисляем расстояния между текущим лицом и всеми известными лицами
            face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
            
            # Находим индекс лица с минимальным расстоянием (наибольшая схожесть)
            best_match_index = np.argmin(face_distances)
            best_distance = face_distances[best_match_index]
            
            # Восстанавливаем реальные координаты лица (масштабируем обратно)
            top, right, bottom, left = face_location
            top = int(top / scale)
            right = int(right / scale)
            bottom = int(bottom / scale)
            left = int(left / scale)
            
            # Создаем структуру с информацией о распознанном лице
            recognized_face = {
                'location': (top, right, bottom, left),  # Координаты лица на кадре
                'distance': best_distance,               # Расстояние до ближайшего известного лица
                'user_id': None,                        # ID пользователя (заполняется ниже)
                'is_known': False                       # Флаг того, что лицо распознано
            }
            
            # Проверяем, превышает ли расстояние установленный порог
            if best_distance <= FACE_DISTANCE_THRESHOLD:
                # Лицо распознано - расстояние меньше порогового значения
                recognized_face['user_id'] = self.known_user_ids[best_match_index]
                recognized_face['is_known'] = True
            
            # Добавляем результат в список распознанных лиц
            recognized_faces.append(recognized_face)
        
        return recognized_faces
    
    def draw_face_rectangle(self, frame, face_info, color, name=""):
        """Рисование рамки вокруг распознанного лица"""
        # Извлекаем координаты лица
        top, right, bottom, left = face_info['location']
        
        # Рисуем прямоугольную рамку вокруг лица
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Если есть имя для отображения, добавляем его под рамкой
        if name.strip():
            # Рисуем фон для текста
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            # Добавляем текст с именем пользователя
            cv2.putText(frame, name, (left + 6, bottom - 6), 
                       cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 0), 1)
        
        return frame
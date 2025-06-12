# core/camera_manager.py
import cv2
from config.settings import CAMERA_WIDTH, CAMERA_HEIGHT

class CameraManager:
    """Менеджер камеры"""
    
    def __init__(self):
        self.cap = None
        self.is_running = False
    
    def start_camera(self):
        """Запуск камеры"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                return False
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            self.is_running = True
            return True
            
        except Exception:
            return False
    
    def stop_camera(self):
        """Остановка камеры"""
        self.is_running = False
        if self.cap:
            self.cap.release()
    
    def get_frame(self):
        """Получение кадра с камеры"""
        if not self.is_running or not self.cap:
            return None
        
        ret, frame = self.cap.read()
        return frame if ret else None
    
    def is_camera_running(self):
        """Проверка состояния камеры"""
        return self.is_running
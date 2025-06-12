# config/settings.py
"""Настройки приложения"""

# Параметры распознавания
RECOGNITION_DELAY = 3  # Задержка между успешными распознаваниями (секунды)
UNKNOWN_FACE_DELAY = 5  # Задержка для неизвестных лиц (секунды)
INFO_DISPLAY_DURATION = 2  # Время показа информации (секунды)

# Параметры камеры
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FRAME_SCALE = 0.25  # Масштаб для ускорения распознавания

# Параметры базы данных
USERS_DB = "users.db"
AUDIT_DB = "audit.db"

# Параметры интерфейса
WINDOW_SIZE = "1200x800"
APP_TITLE = "Система распознавания лиц"
THEME_COLOR = "#6B46C1"

# Папки
PHOTOS_DIR = "photos"
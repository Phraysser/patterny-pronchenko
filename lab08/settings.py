import os
import threading
from settings_storage import SettingsStorage
from json_settings_storage import JsonSettingsStorage


class Settings:

    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Settings, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.window_width = 800
        self.window_height = 600
        self.game_title = "Танки"
        self.tank_speed = 3.0
        self.bullet_speed = 8.0
        self.bullet_damage = 1
        self.default_level = "levels/level1.txt"
        
        # === Адаптер: используем JSON-хранилище по умолчанию ===
        # Можно легко переключиться на XmlSettingsStorage через set_storage()
        self._storage = JsonSettingsStorage()
        self._file_path = "settings.json"
        
        self._initialized = True
    
    @classmethod
    def get_instance(cls):
        """Получить единственный экземпляр настроек."""
        if cls._instance is None:
            cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Сбросить экземпляр (для тестирования)."""
        with cls._lock:
            cls._instance = None
    
    def set_storage(self, storage, file_path):

        self._storage = storage
        self._file_path = file_path
    
    def load_from_file(self, file_path=None):
        """Загрузить настройки из файла через текущее хранилище."""
        if file_path:
            self._file_path = file_path
        
        if os.path.exists(self._file_path):
            try:
                data = self._storage.load(self._file_path)
                self._apply_data(data)
            except Exception as e:
                print(f"Ошибка загрузки настроек: {e}")
        else:
            self.save_to_file()
    
    def save_to_file(self, file_path=None):
        """Сохранить настройки в файл через текущее хранилище."""
        if file_path:
            self._file_path = file_path
        try:
            data = self._to_data()
            self._storage.save(data, self._file_path)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def _to_data(self):
        """Преобразовать настройки в словарь."""
        return {
            'window_width': self.window_width,
            'window_height': self.window_height,
            'game_title': self.game_title,
            'tank_speed': self.tank_speed,
            'bullet_speed': self.bullet_speed,
            'bullet_damage': self.bullet_damage,
            'default_level': self.default_level
        }
    
    def _apply_data(self, data):
        """Применить данные из словаря к настройкам."""
        self.window_width = int(data.get('window_width', 800))
        self.window_height = int(data.get('window_height', 600))
        self.game_title = data.get('game_title', "Танки")
        self.tank_speed = float(data.get('tank_speed', 3.0))
        self.bullet_speed = float(data.get('bullet_speed', 8.0))
        self.bullet_damage = int(data.get('bullet_damage', 1))
        self.default_level = data.get('default_level', "levels/level1.txt")
import json
import os
import threading


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
        self.game_title = "Танк"
        self.tank_speed = 3.0
        self.bullet_speed = 8.0
        self.bullet_damage = 1
        self.default_level = "levels/level1.txt"
        
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
    
    def load_from_file(self, file_path="settings.json"):
        """Загрузить настройки из файла."""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.window_width = data.get('window_width', 800)
                    self.window_height = data.get('window_height', 600)
                    self.game_title = data.get('game_title', "Танк")
                    self.tank_speed = data.get('tank_speed', 3.0)
                    self.bullet_speed = data.get('bullet_speed', 8.0)
                    self.bullet_damage = data.get('bullet_damage', 1)
                    self.default_level = data.get('default_level', "levels/level1.txt")
            except Exception as e:
                print(f"Ошибка загрузки настроек: {e}")
        else:
            self.save_to_file(file_path)
    
    def save_to_file(self, file_path="settings.json"):
        """Сохранить настройки в файл."""
        try:
            data = {
                'window_width': self.window_width,
                'window_height': self.window_height,
                'game_title': self.game_title,
                'tank_speed': self.tank_speed,
                'bullet_speed': self.bullet_speed,
                'bullet_damage': self.bullet_damage,
                'default_level': self.default_level
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
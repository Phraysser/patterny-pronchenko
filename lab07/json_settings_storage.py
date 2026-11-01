import json
from settings_storage import SettingsStorage


class JsonSettingsStorage(SettingsStorage):
    
    def save(self, data, file_path):
        """Сохранить настройки в JSON-файл."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load(self, file_path):
        """Загрузить настройки из JSON-файла."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
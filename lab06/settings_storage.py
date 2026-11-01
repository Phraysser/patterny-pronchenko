from abc import ABC, abstractmethod


class SettingsStorage(ABC):

    
    @abstractmethod
    def save(self, data, file_path):
        """Сохранить словарь данных в файл."""
        pass
    
    @abstractmethod
    def load(self, file_path):
        """Загрузить данные из файла и вернуть словарь."""
        pass
from abc import ABC, abstractmethod


class GameObject(ABC):
    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self, renderer):
        pass

    @abstractmethod
    def get_bounds(self):
        pass
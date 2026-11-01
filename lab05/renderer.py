from abc import ABC, abstractmethod


class Renderer(ABC):

    
    @abstractmethod
    def clear(self, color):
        """Очистить экран заданным цветом."""
        pass
    
    @abstractmethod
    def draw_rect(self, x, y, width, height, color, outline=False, outline_width=1):
        """Нарисовать прямоугольник."""
        pass
    
    @abstractmethod
    def draw_line(self, x1, y1, x2, y2, color, width=1):
        """Нарисовать линию."""
        pass
    
    @abstractmethod
    def draw_circle(self, x, y, radius, color):
        """Нарисовать круг."""
        pass
    
    @abstractmethod
    def draw_ellipse(self, x, y, width, height, color):
        """Нарисовать эллипс."""
        pass
    
    @abstractmethod
    def draw_text(self, text, x, y, color, size=24, bold=False):
        """Нарисовать текст. Возвращает размер (width, height) отрисованного текста."""
        pass
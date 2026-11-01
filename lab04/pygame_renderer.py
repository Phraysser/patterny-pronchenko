import pygame
from renderer import Renderer


class PygameRenderer(Renderer):

    
    def __init__(self, screen):
        self.screen = screen
        self._font_cache = {}
    
    def _get_font(self, size, bold=False):
        """Получить или создать шрифт нужного размера (кэширование)."""
        key = (size, bold)
        if key not in self._font_cache:
            font = pygame.font.Font(None, size)
            if bold:
                try:
                    font.set_bold(True)
                except Exception:
                    pass  # Некоторые версии Pygame не поддерживают set_bold
            self._font_cache[key] = font
        return self._font_cache[key]
    
    def clear(self, color):
        """Очистить экран."""
        self.screen.fill(color)
    
    def draw_rect(self, x, y, width, height, color, outline=False, outline_width=1):
        """Нарисовать прямоугольник через pygame.draw.rect."""
        rect = pygame.Rect(int(x), int(y), int(width), int(height))
        if outline:
            pygame.draw.rect(self.screen, color, rect, outline_width)
        else:
            pygame.draw.rect(self.screen, color, rect)
    
    def draw_line(self, x1, y1, x2, y2, color, width=1):
        """Нарисовать линию через pygame.draw.line."""
        pygame.draw.line(self.screen, color, (int(x1), int(y1)), (int(x2), int(y2)), width)
    
    def draw_circle(self, x, y, radius, color):
        """Нарисовать круг через pygame.draw.circle."""
        pygame.draw.circle(self.screen, color, (int(x), int(y)), int(radius))
    
    def draw_ellipse(self, x, y, width, height, color):
        """Нарисовать эллипс через pygame.draw.ellipse."""
        rect = pygame.Rect(int(x), int(y), int(width), int(height))
        pygame.draw.ellipse(self.screen, color, rect)
    
    def draw_text(self, text, x, y, color, size=24, bold=False):
        """Нарисовать текст через pygame.font.Font."""
        font = self._get_font(size, bold)
        surface = font.render(str(text), True, color)
        self.screen.blit(surface, (int(x), int(y)))
        return surface.get_size()
import pygame


class Tank:

    
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.speed = speed
        self.direction = 'up'
        self.position = (int(x), int(y))
        self.bounds = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def move(self, dx, dy):
        """Переместить танк и обновить направление."""
        self.x += dx
        self.y += dy
        self.position = (int(self.x), int(self.y))
        
        if dx > 0:
            self.direction = 'right'
        elif dx < 0:
            self.direction = 'left'
        elif dy > 0:
            self.direction = 'down'
        elif dy < 0:
            self.direction = 'up'
        
        self.bounds = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self, screen_width, screen_height):
        """Ограничить танк границами экрана."""
        self.x = max(0, min(self.x, screen_width - self.width))
        self.y = max(0, min(self.y, screen_height - self.height))
        self.position = (int(self.x), int(self.y))
        self.bounds = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def render(self, renderer):

        # Корпус танка
        renderer.draw_rect(self.x, self.y, self.width, self.height, (0, 200, 0))
        
        # Вычисление позиции дула
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        turret_length = 20
        
        if self.direction == 'up':
            end_x, end_y = center_x, self.y - turret_length
        elif self.direction == 'down':
            end_x, end_y = center_x, self.y + self.height + turret_length
        elif self.direction == 'left':
            end_x, end_y = self.x - turret_length, center_y
        else:
            end_x, end_y = self.x + self.width + turret_length, center_y
        
        # Дуло танка
        renderer.draw_line(center_x, center_y, end_x, end_y, (0, 100, 0), 4)
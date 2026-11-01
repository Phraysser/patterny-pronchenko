import pygame
import copy


class Obstacle:
    """
    Класс препятствия с реализацией паттерна Прототип.
    Метод clone() позволяет создавать копии препятствий.
    """
    
    def __init__(self, data):
        self.x = data['x']
        self.y = data['y']
        self.width = data['width']
        self.height = data['height']
        self.health = data['health']
        self.max_health = data['health']
        self.points = data['points']
        self.type = data['type']
        
        self.position = (self.x, self.y)
        self.size = (self.width, self.height)
        self.center = (self.x + self.width // 2, self.y + self.height // 2)
        self.bounds = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def take_damage(self, damage):
        self.health -= damage
    
    @property
    def is_destroyed(self):
        return self.health <= 0
    
    def render(self, screen):
        if self.type == 'brick':
            base_color = (139, 69, 19)
        elif self.type == 'metal':
            base_color = (128, 128, 128)
        elif self.type == 'wood':
            base_color = (139, 90, 43)
        else:
            base_color = (139, 0, 0)
        
        health_ratio = self.health / self.max_health
        damage_color = (
            int(base_color[0] * health_ratio),
            int(base_color[1] * health_ratio),
            int(base_color[2] * health_ratio)
        )
        
        pygame.draw.rect(screen, damage_color, self.bounds)
        pygame.draw.rect(screen, (0, 0, 0), self.bounds, 2)
    
    def clone(self, new_x=None, new_y=None):
        """
        Паттерн Прототип: создаёт копию препятствия.
        Опционально можно указать новую позицию.
        """
        data = {
            'x': new_x if new_x is not None else self.x,
            'y': new_y if new_y is not None else self.y,
            'width': self.width,
            'height': self.height,
            'health': self.max_health,  # Копируем с полным здоровьем
            'points': self.points,
            'type': self.type
        }
        return Obstacle(data)
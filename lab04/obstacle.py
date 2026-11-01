import pygame
from game_object import GameObject


class Obstacle(GameObject):
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

    def update(self):
        pass

    def get_bounds(self):
        return self.bounds

    def render(self, renderer):
        if self.type == 'brick':
            base_color = (139, 69, 19)
        elif self.type == 'metal':
            base_color = (128, 128, 128)
        elif self.type == 'wood':
            base_color = (139, 90, 43)
        else:
            base_color = (139, 0, 0)

        health_ratio = self.health / self.max_health if self.max_health > 0 else 0
        damage_color = (
            int(base_color[0] * health_ratio),
            int(base_color[1] * health_ratio),
            int(base_color[2] * health_ratio)
        )

        renderer.draw_rect(self.x, self.y, self.width, self.height, damage_color)
        renderer.draw_rect(self.x, self.y, self.width, self.height,
                          (0, 0, 0), outline=True, outline_width=2)

    def clone(self, new_x=None, new_y=None):
        data = {
            'x': new_x if new_x is not None else self.x,
            'y': new_y if new_y is not None else self.y,
            'width': self.width,
            'height': self.height,
            'health': self.max_health,
            'points': self.points,
            'type': self.type
        }
        return Obstacle(data)
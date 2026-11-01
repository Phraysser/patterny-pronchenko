import pygame
from game_object import GameObject
from obstacle_flyweight import ObstacleFlyweightFactory


class Obstacle(GameObject):
    def __init__(self, data):
        self.x = data['x']
        self.y = data['y']
        self.width = data['width']
        self.height = data['height']
        self.type = data['type']

        self._flyweight = ObstacleFlyweightFactory.get_flyweight(self.type)

        self.health = data.get('health', self._flyweight.get_base_health())
        self.max_health = self.health
        self.points = data.get('points', self._flyweight.get_base_points())

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
        health_ratio = self.health / self.max_health if self.max_health > 0 else 0
        self._flyweight.render_base(
            renderer, self.x, self.y, self.width, self.height, health_ratio
        )

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
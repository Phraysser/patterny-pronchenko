import pygame
from game_object import GameObject


class Bullet(GameObject):
    def __init__(self, start_position, direction, speed, damage):
        self.x = start_position[0] + 15
        self.y = start_position[1] + 15
        self.width = 6
        self.height = 6
        self.damage = damage
        self.bounds = pygame.Rect(self.x, self.y, self.width, self.height)

        self.velocity_x = 0
        self.velocity_y = 0

        if direction == 'up':
            self.velocity_y = -speed
        elif direction == 'down':
            self.velocity_y = speed
        elif direction == 'left':
            self.velocity_x = -speed
        elif direction == 'right':
            self.velocity_x = speed

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.bounds = pygame.Rect(self.x, self.y, self.width, self.height)

    def is_out_of_bounds(self, screen_width, screen_height):
        return (self.x < 0 or self.x > screen_width or
                self.y < 0 or self.y > screen_height)

    def get_bounds(self):
        return self.bounds

    def render(self, renderer):
        renderer.draw_ellipse(self.x, self.y, self.width, self.height, (255, 255, 0))
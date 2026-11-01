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
        self.x = max(0, min(self.x, screen_width - self.width))
        self.y = max(0, min(self.y, screen_height - self.height))
        self.position = (int(self.x), int(self.y))
        self.bounds = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def render(self, screen):
        pygame.draw.rect(screen, (0, 200, 0), self.bounds)
        
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
        
        pygame.draw.line(screen, (0, 100, 0),
                        (center_x, center_y), (end_x, end_y), 4)
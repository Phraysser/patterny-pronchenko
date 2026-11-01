import random
from game_object import GameObject


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_x = random.uniform(-3, 3)
        self.velocity_y = random.uniform(-3, 3)
        self.size = random.randint(3, 8)
        self.color = random.choice([
            (255, 255, 0),
            (255, 165, 0),
            (255, 0, 0),
            (255, 69, 0)
        ])
        self.life = random.randint(15, 30)
        self.max_life = self.life


class Explosion(GameObject):
    def __init__(self, center, size):
        self.center = center
        self.size = size
        self.current_frame = 0
        self.max_frames = 30
        self.particles = []
        self._bounds = None

        for _ in range(20):
            self.particles.append(Particle(center[0], center[1]))

    def update(self):
        self.current_frame += 1

        for particle in self.particles:
            particle.x += particle.velocity_x
            particle.y += particle.velocity_y
            particle.velocity_x *= 0.95
            particle.velocity_y *= 0.95
            particle.life -= 1

        self.particles = [p for p in self.particles if p.life > 0]

    def is_finished(self):
        return self.current_frame >= self.max_frames or len(self.particles) == 0

    def get_bounds(self):
        return None

    def render(self, renderer):
        alpha = 1.0 - (self.current_frame / self.max_frames)

        for particle in self.particles:
            particle_alpha = alpha * (particle.life / particle.max_life)
            color = tuple(int(c * particle_alpha) for c in particle.color)
            renderer.draw_circle(particle.x, particle.y, particle.size // 2, color)
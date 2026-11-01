import pygame
from obstacle import Obstacle


class ObstacleDecorator(Obstacle):
    def __init__(self, obstacle):
        self._obstacle = obstacle

    @property
    def x(self):
        return self._obstacle.x

    @x.setter
    def x(self, value):
        self._obstacle.x = value

    @property
    def y(self):
        return self._obstacle.y

    @y.setter
    def y(self, value):
        self._obstacle.y = value

    @property
    def width(self):
        return self._obstacle.width

    @property
    def height(self):
        return self._obstacle.height

    @property
    def health(self):
        return self._obstacle.health

    @health.setter
    def health(self, value):
        self._obstacle.health = value

    @property
    def max_health(self):
        return self._obstacle.max_health

    @max_health.setter
    def max_health(self, value):
        self._obstacle.max_health = value

    @property
    def points(self):
        return self._obstacle.points

    @points.setter
    def points(self, value):
        self._obstacle.points = value

    @property
    def type(self):
        return self._obstacle.type

    @property
    def position(self):
        return self._obstacle.position

    @property
    def size(self):
        return self._obstacle.size

    @property
    def center(self):
        return self._obstacle.center

    @property
    def bounds(self):
        return self._obstacle.bounds

    @property
    def is_destroyed(self):
        return self._obstacle.is_destroyed

    def take_damage(self, damage):
        self._obstacle.take_damage(damage)

    def update(self):
        pass

    def get_bounds(self):
        return self._obstacle.get_bounds()

    def render(self, renderer):
        self._obstacle.render(renderer)

    def clone(self, new_x=None, new_y=None):
        cloned_inner = self._obstacle.clone(new_x, new_y)
        return self.__class__(cloned_inner)

    def get_inner_obstacle(self):
        return self._obstacle


class ArmoredObstacleDecorator(ObstacleDecorator):
    def __init__(self, obstacle, extra_health=5):
        super().__init__(obstacle)
        self._extra_health = extra_health
        self._obstacle.health += extra_health
        self._obstacle.max_health += extra_health

    def render(self, renderer):
        self._obstacle.render(renderer)
        renderer.draw_rect(
            self._obstacle.x, self._obstacle.y,
            self._obstacle.width, self._obstacle.height,
            (200, 200, 255), outline=True, outline_width=3
        )

    def clone(self, new_x=None, new_y=None):
        cloned_inner = self._obstacle.clone(new_x, new_y)
        return ArmoredObstacleDecorator(cloned_inner, self._extra_health)


class ValuableObstacleDecorator(ObstacleDecorator):
    def __init__(self, obstacle, bonus_points=25):
        super().__init__(obstacle)
        self._bonus_points = bonus_points
        self._obstacle.points += bonus_points

    def render(self, renderer):
        self._obstacle.render(renderer)
        star_x = self._obstacle.x + self._obstacle.width // 2
        star_y = self._obstacle.y + self._obstacle.height // 2
        renderer.draw_circle(star_x, star_y, 6, (255, 215, 0))

    def clone(self, new_x=None, new_y=None):
        cloned_inner = self._obstacle.clone(new_x, new_y)
        return ValuableObstacleDecorator(cloned_inner, self._bonus_points)


class RegeneratingObstacleDecorator(ObstacleDecorator):
    def __init__(self, obstacle, regen_rate=1, regen_interval=60):
        super().__init__(obstacle)
        self._regen_rate = regen_rate
        self._regen_interval = regen_interval
        self._frame_counter = 0

    def update(self):
        self._frame_counter += 1
        if self._frame_counter >= self._regen_interval:
            self._frame_counter = 0
            if self._obstacle.health < self._obstacle.max_health:
                self._obstacle.health = min(
                    self._obstacle.health + self._regen_rate,
                    self._obstacle.max_health
                )

    def render(self, renderer):
        self._obstacle.render(renderer)
        if self._obstacle.health < self._obstacle.max_health:
            bar_width = self._obstacle.width
            bar_height = 3
            bar_x = self._obstacle.x
            bar_y = self._obstacle.y - 6
            renderer.draw_rect(bar_x, bar_y, bar_width, bar_height, (60, 60, 60))
            ratio = self._obstacle.health / self._obstacle.max_health
            renderer.draw_rect(bar_x, bar_y, int(bar_width * ratio), bar_height, (0, 255, 0))

    def clone(self, new_x=None, new_y=None):
        cloned_inner = self._obstacle.clone(new_x, new_y)
        return RegeneratingObstacleDecorator(cloned_inner, self._regen_rate, self._regen_interval)
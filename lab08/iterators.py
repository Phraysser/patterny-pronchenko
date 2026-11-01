from obstacle_decorator import (
    ArmoredObstacleDecorator,
    ValuableObstacleDecorator,
    RegeneratingObstacleDecorator
)
from composite_game_object import CompositeGameObject


class ObstacleIterator:
    def __init__(self, obstacles):
        self._obstacles = obstacles
        self._index = 0

    def has_next(self):
        return self._index < len(self._obstacles)

    def next(self):
        if not self.has_next():
            raise StopIteration
        item = self._obstacles[self._index]
        self._index += 1
        return item

    def reset(self):
        self._index = 0


class ObstacleByTypeIterator:
    def __init__(self, obstacles, obstacle_type):
        self._filtered = [o for o in obstacles if o.type == obstacle_type]
        self._index = 0

    def has_next(self):
        return self._index < len(self._filtered)

    def next(self):
        if not self.has_next():
            raise StopIteration
        item = self._filtered[self._index]
        self._index += 1
        return item

    def reset(self):
        self._index = 0


class DamagedObstacleIterator:
    def __init__(self, obstacles):
        self._filtered = [o for o in obstacles if 0 < o.health < o.max_health]
        self._index = 0

    def has_next(self):
        return self._index < len(self._filtered)

    def next(self):
        if not self.has_next():
            raise StopIteration
        item = self._filtered[self._index]
        self._index += 1
        return item

    def reset(self):
        self._index = 0


class DecoratedObstacleIterator:
    def __init__(self, obstacles):
        self._filtered = [o for o in obstacles if isinstance(
            o, (ArmoredObstacleDecorator, ValuableObstacleDecorator, RegeneratingObstacleDecorator)
        )]
        self._index = 0

    def has_next(self):
        return self._index < len(self._filtered)

    def next(self):
        if not self.has_next():
            raise StopIteration
        item = self._filtered[self._index]
        self._index += 1
        return item

    def reset(self):
        self._index = 0


class CompositeIterator:
    def __init__(self, composite):
        self._composite = composite
        self._stack = None
        self._next_item = None
        self._has_next_item = False
        self.reset()

    def _advance(self):
        self._has_next_item = False
        self._next_item = None

        while self._stack:
            try:
                it = self._stack[-1]
                item = next(it)
                if isinstance(item, CompositeGameObject):
                    children = item.get_children()
                    if children:
                        self._stack.append(iter(children))
                else:
                    self._next_item = item
                    self._has_next_item = True
                    return
            except StopIteration:
                self._stack.pop()

    def has_next(self):
        return self._has_next_item

    def next(self):
        if not self._has_next_item:
            raise StopIteration
        result = self._next_item
        self._advance()
        return result

    def reset(self):
        children = self._composite.get_children()
        self._stack = [iter(children)] if children else []
        self._advance()


class HighValueObstacleIterator:
    def __init__(self, obstacles, min_points=15):
        self._filtered = [o for o in obstacles if o.points >= min_points]
        self._index = 0

    def has_next(self):
        return self._index < len(self._filtered)

    def next(self):
        if not self.has_next():
            raise StopIteration
        item = self._filtered[self._index]
        self._index += 1
        return item

    def reset(self):
        self._index = 0
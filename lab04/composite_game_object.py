from game_object import GameObject


class CompositeGameObject(GameObject):
    def __init__(self, name="Group"):
        self._children = []
        self.name = name

    def add(self, game_object):
        if game_object not in self._children:
            self._children.append(game_object)

    def remove(self, game_object):
        if game_object in self._children:
            self._children.remove(game_object)

    def get_child(self, index):
        return self._children[index]

    def get_children(self):
        return self._children

    def clear(self):
        self._children.clear()

    def update(self):
        for child in self._children[:]:
            child.update()

    def render(self, renderer):
        for child in self._children:
            child.render(renderer)

    def get_bounds(self):
        if not self._children:
            return None
        all_bounds = [child.get_bounds() for child in self._children]
        all_bounds = [b for b in all_bounds if b is not None]
        if not all_bounds:
            return None
        min_x = min(b.x for b in all_bounds)
        min_y = min(b.y for b in all_bounds)
        max_x = max(b.x + b.width for b in all_bounds)
        max_y = max(b.y + b.height for b in all_bounds)
        import pygame
        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def __len__(self):
        return len(self._children)

    def __iter__(self):
        return iter(self._children)
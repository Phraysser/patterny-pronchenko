import random
from command import Command
from bullet_factory import (
    StandardBulletFactory,
    FastBulletFactory,
    HeavyBulletFactory,
    ExplosiveBulletFactory
)
from obstacle_decorator import (
    ArmoredObstacleDecorator,
    ValuableObstacleDecorator,
    RegeneratingObstacleDecorator
)
from obstacle import Obstacle
from composite_game_object import CompositeGameObject
from json_settings_storage import JsonSettingsStorage
from xml_settings_storage import XmlSettingsStorage


class MoveCommand(Command):
    def __init__(self, tank, dx, dy, screen_width, screen_height):
        self._tank = tank
        self._dx = dx
        self._dy = dy
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._old_x = tank.x
        self._old_y = tank.y

    def execute(self):
        self._tank.move(self._dx, self._dy)
        self._tank.update_position(self._screen_width, self._screen_height)

    def undo(self):
        self._tank.x = self._old_x
        self._tank.y = self._old_y
        self._tank.position = (int(self._tank.x), int(self._tank.y))
        self._tank.update_position(self._screen_width, self._screen_height)

    def get_name(self):
        return f"Move({self._dx}, {self._dy})"


class ShootCommand(Command):
    def __init__(self, engine):
        self._engine = engine
        self._bullet = None

    def execute(self):
        self._bullet = self._engine.bullet_factory.create_bullet(
            self._engine.tank.position,
            self._engine.tank.direction,
            self._engine.settings.bullet_speed,
            self._engine.settings.bullet_damage
        )
        self._engine.bullets.append(self._bullet)

    def undo(self):
        if self._bullet in self._engine.bullets:
            self._engine.bullets.remove(self._bullet)

    def get_name(self):
        return "Shoot"


class SwitchBulletTypeCommand(Command):
    def __init__(self, engine, bullet_type):
        self._engine = engine
        self._new_type = bullet_type
        self._old_factory = engine.bullet_factory

    def execute(self):
        if self._new_type == 'standard':
            self._engine.bullet_factory = StandardBulletFactory()
        elif self._new_type == 'fast':
            self._engine.bullet_factory = FastBulletFactory()
        elif self._new_type == 'heavy':
            self._engine.bullet_factory = HeavyBulletFactory()
        elif self._new_type == 'explosive':
            self._engine.bullet_factory = ExplosiveBulletFactory()

    def undo(self):
        self._engine.bullet_factory = self._old_factory

    def get_name(self):
        return f"SwitchBullet({self._new_type})"


class CloneObstacleCommand(Command):
    def __init__(self, engine, obstacle_type, new_x, new_y):
        self._engine = engine
        self._obstacle_type = obstacle_type
        self._new_x = new_x
        self._new_y = new_y
        self._cloned = None

    def execute(self):
        if self._obstacle_type in self._engine.obstacle_prototypes:
            prototype = self._engine.obstacle_prototypes[self._obstacle_type]
            self._cloned = prototype.clone(self._new_x, self._new_y)
            self._engine.obstacles.append(self._cloned)
            self._engine.obstacle_groups.add(self._cloned)

    def undo(self):
        if self._cloned is not None:
            if self._cloned in self._engine.obstacles:
                self._engine.obstacles.remove(self._cloned)
            for group in self._engine.obstacle_groups:
                if isinstance(group, CompositeGameObject):
                    group.remove(self._cloned)
                elif group == self._cloned:
                    self._engine.obstacle_groups.remove(self._cloned)

    def get_name(self):
        return f"CloneObstacle({self._obstacle_type})"


class ResetGameCommand(Command):
    def __init__(self, engine):
        self._engine = engine

    def execute(self):
        self._engine.load_level(self._engine.settings.default_level)

    def undo(self):
        pass

    def get_name(self):
        return "ResetGame"


class ToggleStorageFormatCommand(Command):
    def __init__(self, settings):
        self._settings = settings

    def execute(self):
        if isinstance(self._settings._storage, JsonSettingsStorage):
            self._settings.set_storage(XmlSettingsStorage(), "settings.xml")
            self._settings.save_to_file()
        else:
            self._settings.set_storage(JsonSettingsStorage(), "settings.json")
            self._settings.save_to_file()

    def undo(self):
        self.execute()

    def get_name(self):
        return "ToggleStorageFormat"


class MacroCommand(Command):
    def __init__(self, commands, name="Macro"):
        self._commands = commands
        self._name = name

    def execute(self):
        for cmd in self._commands:
            cmd.execute()

    def undo(self):
        for cmd in reversed(self._commands):
            cmd.undo()

    def get_name(self):
        return self._name
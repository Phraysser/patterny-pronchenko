import pygame
import random
from tank import Tank
from bullet import Bullet
from obstacle import Obstacle
from explosion import Explosion
from composite_game_object import CompositeGameObject
from obstacle_decorator import (
    ArmoredObstacleDecorator,
    ValuableObstacleDecorator,
    RegeneratingObstacleDecorator
)
from level_loader import LevelLoader
from settings import Settings
from bullet_factory import (
    StandardBulletFactory,
    FastBulletFactory,
    HeavyBulletFactory,
    ExplosiveBulletFactory
)
from pygame_renderer import PygameRenderer


class GameEngine:
    def __init__(self, screen):
        self.settings = Settings.get_instance()
        self.settings.load_from_file()

        self.screen = screen
        self.renderer = PygameRenderer(screen)

        self.tank = None
        self.bullets = []
        self.obstacles = []
        self.obstacle_groups = CompositeGameObject("AllObstacles")
        self.explosions = []
        self.score = 0
        self.pressed_keys = set()

        self.bullet_factory = StandardBulletFactory()

        self.bullet_prototype = None
        self.obstacle_prototypes = {}

        self.level_loader = LevelLoader()
        self.load_level(self.settings.default_level)

    def reload_settings(self):
        self.settings = Settings.get_instance()
        self.settings.load_from_file()

        if self.tank:
            self.tank.speed = self.settings.tank_speed

    def update_screen(self, screen):
        self.screen = screen
        self.renderer = PygameRenderer(screen)

    def switch_storage_format(self, storage, file_path):
        self.settings.set_storage(storage, file_path)
        self.settings.save_to_file()

    def load_level(self, level_file):
        level_data = self.level_loader.load_level(level_file)

        self.tank = Tank(
            level_data['tank_start'][0],
            level_data['tank_start'][1],
            self.settings.tank_speed
        )

        self.obstacles = []
        self.bullets = []
        self.explosions = []
        self.score = 0

        self.obstacle_prototypes = {}
        self.obstacle_groups = CompositeGameObject("AllObstacles")

        group_map = {}
        for group_data in level_data.get('groups', []):
            group = CompositeGameObject(group_data['name'])
            self.obstacle_groups.add(group)
            group_map[group_data['name']] = group

        for obstacle_data in level_data['obstacles']:
            obstacle = Obstacle(obstacle_data)

            group_name = None
            for group_data in level_data.get('groups', []):
                if obstacle_data in group_data['obstacles']:
                    group_name = group_data['name']
                    break

            rand_val = random.random()
            if rand_val < 0.2:
                obstacle = ArmoredObstacleDecorator(obstacle, extra_health=3)
            elif rand_val < 0.4:
                obstacle = ValuableObstacleDecorator(obstacle, bonus_points=15)
            elif rand_val < 0.6:
                obstacle = RegeneratingObstacleDecorator(obstacle, regen_rate=1, regen_interval=90)

            self.obstacles.append(obstacle)

            if obstacle.type not in self.obstacle_prototypes:
                self.obstacle_prototypes[obstacle.type] = obstacle

            if group_name and group_name in group_map:
                group_map[group_name].add(obstacle)
            else:
                self.obstacle_groups.add(obstacle)

        self.bullet_prototype = Bullet(
            (0, 0),
            'up',
            self.settings.bullet_speed,
            self.settings.bullet_damage
        )

    def update(self):
        self.update_tank()
        self.update_bullets()
        self.update_obstacles()
        self.update_explosions()
        self.check_collisions()

    def update_tank(self):
        dx, dy = 0, 0

        if pygame.K_UP in self.pressed_keys:
            dy = -self.tank.speed
        if pygame.K_DOWN in self.pressed_keys:
            dy = self.tank.speed
        if pygame.K_LEFT in self.pressed_keys:
            dx = -self.tank.speed
        if pygame.K_RIGHT in self.pressed_keys:
            dx = self.tank.speed

        if dx != 0 or dy != 0:
            self.tank.move(dx, dy)

        self.tank.update_position(self.settings.window_width, self.settings.window_height)

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_out_of_bounds(self.settings.window_width,
                                       self.settings.window_height):
                self.bullets.remove(bullet)

    def update_obstacles(self):
        self.obstacle_groups.update()

    def update_explosions(self):
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.is_finished():
                self.explosions.remove(explosion)

    def check_collisions(self):
        for bullet in self.bullets[:]:
            for obstacle in self.obstacles[:]:
                if bullet.get_bounds().colliderect(obstacle.get_bounds()):
                    obstacle.take_damage(bullet.damage)

                    if bullet in self.bullets:
                        self.bullets.remove(bullet)

                    if obstacle.is_destroyed:
                        self.explosions.append(
                            Explosion(obstacle.center, obstacle.size)
                        )
                        self.score += obstacle.points
                        self.obstacles.remove(obstacle)
                        self._remove_from_groups(obstacle)
                    break

    def _remove_from_groups(self, obstacle):
        for group in self.obstacle_groups:
            if isinstance(group, CompositeGameObject):
                group.remove(obstacle)
            elif group == obstacle:
                self.obstacle_groups.remove(obstacle)

    def render(self):
        self.renderer.clear((0, 0, 0))

        self.obstacle_groups.render(self.renderer)

        for bullet in self.bullets:
            bullet.render(self.renderer)

        for explosion in self.explosions:
            explosion.render(self.renderer)

        self.tank.render(self.renderer)

        self.render_hud()

    def render_hud(self):
        self.renderer.draw_text(
            f"Очки: {self.score}", 10, 10, (255, 255, 255), size=36, bold=True
        )

        factory_name = self._get_factory_display_name()
        self.renderer.draw_text(
            f"Снаряды: {factory_name}", 10, 50, (200, 200, 200), size=36
        )

        storage_name = self.settings._storage.__class__.__name__
        self.renderer.draw_text(
            f"Настройки: {storage_name}", 10, 90, (150, 200, 255), size=24
        )

        total_groups = len([g for g in self.obstacle_groups if isinstance(g, CompositeGameObject)])
        total_obstacles = len(self.obstacles)
        self.renderer.draw_text(
            f"Групп: {total_groups} | Препятствий: {total_obstacles}",
            10, 120, (200, 255, 200), size=24
        )

        hints = [
            "Стрелки - движение | Пробел - выстрел",
            "1 - стандартные | 2 - быстрые | 3 - тяжёлые | 4 - разрывные",
            "X - формат настроек | C - клонировать | G - показать группы",
            "R - сброс | F1 - настройки | Esc - выход"
        ]

        y_offset = self.settings.window_height - 110
        for hint in hints:
            self.renderer.draw_text(hint, 10, y_offset, (150, 150, 150), size=22)
            y_offset += 22

    def _get_factory_display_name(self):
        if isinstance(self.bullet_factory, StandardBulletFactory):
            return "Стандартные"
        elif isinstance(self.bullet_factory, FastBulletFactory):
            return "Быстрые"
        elif isinstance(self.bullet_factory, HeavyBulletFactory):
            return "Тяжёлые"
        elif isinstance(self.bullet_factory, ExplosiveBulletFactory):
            return "Разрывные"
        return "Неизвестные"

    def handle_key_down(self, key):
        self.pressed_keys.add(key)

        if key == pygame.K_SPACE:
            self.shoot()

        elif key == pygame.K_1:
            self.switch_bullet_type('standard')
        elif key == pygame.K_2:
            self.switch_bullet_type('fast')
        elif key == pygame.K_3:
            self.switch_bullet_type('heavy')
        elif key == pygame.K_4:
            self.switch_bullet_type('explosive')

        elif key == pygame.K_x:
            self._toggle_storage_format()

        elif key == pygame.K_c:
            self._clone_random_obstacle()

        elif key == pygame.K_g:
            self._show_groups_info()

    def handle_key_up(self, key):
        self.pressed_keys.discard(key)

    def shoot(self):
        bullet = self.bullet_factory.create_bullet(
            self.tank.position,
            self.tank.direction,
            self.settings.bullet_speed,
            self.settings.bullet_damage
        )
        self.bullets.append(bullet)

    def switch_bullet_type(self, bullet_type):
        if bullet_type == 'standard':
            self.bullet_factory = StandardBulletFactory()
        elif bullet_type == 'fast':
            self.bullet_factory = FastBulletFactory()
        elif bullet_type == 'heavy':
            self.bullet_factory = HeavyBulletFactory()
        elif bullet_type == 'explosive':
            self.bullet_factory = ExplosiveBulletFactory()

    def _toggle_storage_format(self):
        from json_settings_storage import JsonSettingsStorage
        from xml_settings_storage import XmlSettingsStorage

        if isinstance(self.settings._storage, JsonSettingsStorage):
            self.settings.set_storage(XmlSettingsStorage(), "settings.xml")
            self.settings.save_to_file()
        else:
            self.settings.set_storage(JsonSettingsStorage(), "settings.json")
            self.settings.save_to_file()

    def clone_obstacle(self, obstacle_type, new_x, new_y):
        if obstacle_type in self.obstacle_prototypes:
            prototype = self.obstacle_prototypes[obstacle_type]
            cloned = prototype.clone(new_x, new_y)
            self.obstacles.append(cloned)
            self.obstacle_groups.add(cloned)
            return cloned
        return None

    def _clone_random_obstacle(self):
        if self.obstacle_prototypes:
            obstacle_type = list(self.obstacle_prototypes.keys())[0]
            new_x = random.randint(100, self.settings.window_width - 150)
            new_y = random.randint(100, self.settings.window_height - 200)
            self.clone_obstacle(obstacle_type, new_x, new_y)

    def _show_groups_info(self):
        print("\n=== Структура групп препятствий (Composite) ===")
        print(f"Корневая группа: {self.obstacle_groups.name}")
        for group in self.obstacle_groups:
            if isinstance(group, CompositeGameObject):
                print(f"  ├── Группа '{group.name}': {len(group)} объектов")
                for child in group:
                    decorator_info = ""
                    if isinstance(child, ArmoredObstacleDecorator):
                        decorator_info = " [Бронирован]"
                    elif isinstance(child, ValuableObstacleDecorator):
                        decorator_info = " [Ценный]"
                    elif isinstance(child, RegeneratingObstacleDecorator):
                        decorator_info = " [Регенерирующий]"
                    print(f"  │   └── {child.type} ({child.x}, {child.y})"
                          f" HP:{child.health}/{child.max_health} "
                          f"Points:{child.points}{decorator_info}")
            else:
                decorator_info = ""
                if isinstance(group, ArmoredObstacleDecorator):
                    decorator_info = " [Бронирован]"
                elif isinstance(group, ValuableObstacleDecorator):
                    decorator_info = " [Ценный]"
                elif isinstance(group, RegeneratingObstacleDecorator):
                    decorator_info = " [Регенерирующий]"
                print(f"  └── {group.type} ({group.x}, {group.y})"
                      f" HP:{group.health}/{group.max_health} "
                      f"Points:{group.points}{decorator_info}")
        print("=" * 50)

    def reset_game(self):
        self.load_level(self.settings.default_level)
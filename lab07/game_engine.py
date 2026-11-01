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
from level_loader_proxy import LevelLoaderProxy
from settings import Settings
from bullet_factory import (
    StandardBulletFactory,
    FastBulletFactory,
    HeavyBulletFactory,
    ExplosiveBulletFactory
)
from pygame_renderer import PygameRenderer
from obstacle_flyweight import ObstacleFlyweightFactory
from command_invoker import CommandInvoker
from commands import (
    MoveCommand,
    ShootCommand,
    SwitchBulletTypeCommand,
    CloneObstacleCommand,
    ResetGameCommand,
    ToggleStorageFormatCommand,
    MacroCommand
)
from iterators import (
    ObstacleIterator,
    ObstacleByTypeIterator,
    DamagedObstacleIterator,
    DecoratedObstacleIterator,
    CompositeIterator,
    HighValueObstacleIterator
)


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

        self.level_loader = LevelLoaderProxy()
        self.invoker = CommandInvoker(history_limit=30)

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
        self._process_movement()
        self.update_bullets()
        self.update_obstacles()
        self.update_explosions()
        self.check_collisions()

    def _process_movement(self):
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
            cmd = MoveCommand(
                self.tank, dx, dy,
                self.settings.window_width,
                self.settings.window_height
            )
            self.invoker.execute(cmd)
        else:
            self.tank.update_position(
                self.settings.window_width,
                self.settings.window_height
            )

    def update_bullets(self):
        bullet_iter = ObstacleIterator(self.bullets)
        to_remove = []
        while bullet_iter.has_next():
            bullet = bullet_iter.next()
            bullet.update()
            if bullet.is_out_of_bounds(self.settings.window_width,
                                       self.settings.window_height):
                to_remove.append(bullet)
        for bullet in to_remove:
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
            obstacle_iter = ObstacleIterator(self.obstacles)
            while obstacle_iter.has_next():
                obstacle = obstacle_iter.next()
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
        flyweight_count = ObstacleFlyweightFactory.get_count()
        proxy_cache_size = self.level_loader.get_cache_size()
        history_size = self.invoker.get_history_size()
        self.renderer.draw_text(
            f"Групп: {total_groups} | Препятствий: {total_obstacles} | "
            f"Flyweight: {flyweight_count} | Proxy: {proxy_cache_size} | Cmd: {history_size}",
            10, 120, (200, 255, 200), size=24
        )

        hints = [
            "Стрелки - движение | Пробел - выстрел | Z - отмена | Y - повтор",
            "1 - стандартные | 2 - быстрые | 3 - тяжёлые | 4 - разрывные",
            "X - формат настроек | C - клонировать | G - группы | F - Flyweight",
            "I - итераторы | H - история команд | P - Proxy stats",
            "R - сброс | F1 - настройки | Esc - выход"
        ]

        y_offset = self.settings.window_height - 130
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
            cmd = ShootCommand(self)
            self.invoker.execute(cmd)

        elif key == pygame.K_1:
            cmd = SwitchBulletTypeCommand(self, 'standard')
            self.invoker.execute(cmd)
        elif key == pygame.K_2:
            cmd = SwitchBulletTypeCommand(self, 'fast')
            self.invoker.execute(cmd)
        elif key == pygame.K_3:
            cmd = SwitchBulletTypeCommand(self, 'heavy')
            self.invoker.execute(cmd)
        elif key == pygame.K_4:
            cmd = SwitchBulletTypeCommand(self, 'explosive')
            self.invoker.execute(cmd)

        elif key == pygame.K_x:
            cmd = ToggleStorageFormatCommand(self.settings)
            self.invoker.execute(cmd)

        elif key == pygame.K_c:
            if self.obstacle_prototypes:
                obstacle_type = list(self.obstacle_prototypes.keys())[0]
                new_x = random.randint(100, self.settings.window_width - 150)
                new_y = random.randint(100, self.settings.window_height - 200)
                cmd = CloneObstacleCommand(self, obstacle_type, new_x, new_y)
                self.invoker.execute(cmd)

        elif key == pygame.K_z:
            self.invoker.undo()

        elif key == pygame.K_y:
            self.invoker.redo()

        elif key == pygame.K_r:
            cmd = ResetGameCommand(self)
            self.invoker.execute(cmd)

        elif key == pygame.K_g:
            self._show_groups_info()

        elif key == pygame.K_f:
            self._show_flyweight_info()

        elif key == pygame.K_p:
            self._show_proxy_stats()

        elif key == pygame.K_i:
            self._show_iterators_demo()

        elif key == pygame.K_h:
            self._show_command_history()

    def handle_key_up(self, key):
        self.pressed_keys.discard(key)

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

    def _show_flyweight_info(self):
        print("\n=== Информация о приспособленцах (Flyweight) ===")
        print(f"Всего создано приспособленцев: {ObstacleFlyweightFactory.get_count()}")
        print("Разделяемое состояние по типам:")
        for obstacle_type in ObstacleFlyweightFactory.get_all_types():
            flyweight = ObstacleFlyweightFactory.get_flyweight(obstacle_type)
            print(f"  - {obstacle_type}: цвет={flyweight.get_color()}, "
                  f"базовое HP={flyweight.get_base_health()}, "
                  f"базовые очки={flyweight.get_base_points()}")
        print(f"Всего препятствий на поле: {len(self.obstacles)}")
        print("=" * 50)

    def _show_proxy_stats(self):
        print("\n=== Статистика прокси загрузчика уровней (Proxy) ===")
        stats = self.level_loader.get_stats()
        print(f"Всего загрузок уровня: {stats['load_count']}")
        print(f"Попаданий в кэш: {stats['cache_hits']}")
        print(f"Размер кэша: {stats['cache_size']} уровней")
        print(f"Общее время загрузки: {stats['total_load_time']:.6f} сек")
        print("Уровни в кэше:")
        for level_path in stats['cached_levels']:
            is_current = " [текущий]" if level_path == self.settings.default_level else ""
            print(f"  - {level_path}{is_current}")
        print("=" * 50)

    def _show_iterators_demo(self):
        print("\n=== Демонстрация работы итераторов (Iterator) ===")

        print("\n1. ObstacleIterator — обход всех препятствий:")
        it = ObstacleIterator(self.obstacles)
        count = 0
        while it.has_next():
            o = it.next()
            count += 1
        print(f"   Всего препятствий: {count}")

        print("\n2. ObstacleByTypeIterator — обход по типу:")
        for t in ['brick', 'metal', 'wood']:
            it = ObstacleByTypeIterator(self.obstacles, t)
            items = []
            while it.has_next():
                items.append(it.next())
            print(f"   Тип '{t}': {len(items)} объектов")

        print("\n3. DamagedObstacleIterator — повреждённые препятствия:")
        it = DamagedObstacleIterator(self.obstacles)
        damaged = []
        while it.has_next():
            damaged.append(it.next())
        print(f"   Повреждено: {len(damaged)}")

        print("\n4. DecoratedObstacleIterator — декорированные препятствия:")
        it = DecoratedObstacleIterator(self.obstacles)
        decorated = []
        while it.has_next():
            decorated.append(it.next())
        print(f"   Декорировано: {len(decorated)}")
        for o in decorated:
            kind = "Бронирован" if isinstance(o, ArmoredObstacleDecorator) else \
                   "Ценный" if isinstance(o, ValuableObstacleDecorator) else \
                   "Регенерирующий"
            print(f"     - {o.type} ({o.x}, {o.y}) — {kind}")

        print("\n5. CompositeIterator — обход дерева групп (в глубину):")
        it = CompositeIterator(self.obstacle_groups)
        leaves = []
        while it.has_next():
            leaves.append(it.next())
        print(f"   Всего листьев в дереве: {len(leaves)}")

        print("\n6. HighValueObstacleIterator — ценные препятствия (>=15 очков):")
        it = HighValueObstacleIterator(self.obstacles, min_points=15)
        valuable = []
        while it.has_next():
            valuable.append(it.next())
        print(f"   Ценных препятствий: {len(valuable)}")

        print("=" * 50)

    def _show_command_history(self):
        print("\n=== История команд (Command) ===")
        history = self.invoker.get_history()
        print(f"Всего команд в истории: {len(history)}")
        start = max(0, len(history) - 10)
        if start > 0:
            print(f"  (показаны последние 10 из {len(history)})")
        for i, cmd in enumerate(history[start:], start=start + 1):
            print(f"  {i}. {cmd.get_name()}")
        print("=" * 50)

    def reset_game(self):
        cmd = ResetGameCommand(self)
        self.invoker.execute(cmd)
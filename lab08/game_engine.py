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
from iterators import ObstacleIterator
from handlers import (
    ChainBuilder,
    ScoreHandler,
    ExplosionHandler,
    RemoveFromCollectionsHandler,
    LoggingHandler,
    VictoryCheckHandler,
    MovementInputHandler,
    ShootInputHandler,
    BulletTypeInputHandler,
    UndoRedoInputHandler,
    UtilityInputHandler,
    BulletMovementHandler,
    OutOfBoundsHandler,
    CollisionHandler
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

        self._destroyed_chain = ChainBuilder.build_obstacle_destroyed_chain()
        self._bullet_chain = ChainBuilder.build_bullet_chain()
        self._input_chain = ChainBuilder.build_input_chain()

        self._chain_stats = {
            'destroyed_chain_calls': 0,
            'bullet_chain_calls': 0,
            'input_chain_calls': 0,
            'handlers_passed': 0
        }

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
        self._update_bullets_via_chain()
        self.update_obstacles()
        self.update_explosions()

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
            from commands import MoveCommand
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

    def _update_bullets_via_chain(self):
        for bullet in self.bullets[:]:
            context = {
                'engine': self,
                'bullet': bullet,
                'removed': False,
                'hit_obstacle': None,
                'destroyed': False
            }
            self._chain_stats['bullet_chain_calls'] += 1
            self._bullet_chain.handle(context)

    def update_obstacles(self):
        self.obstacle_groups.update()

    def update_explosions(self):
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.is_finished():
                self.explosions.remove(explosion)

    def _handle_obstacle_destroyed(self, obstacle):
        context = {
            'engine': self,
            'obstacle': obstacle,
            'points_gained': 0,
            'victory': False
        }
        self._chain_stats['destroyed_chain_calls'] += 1
        self._destroyed_chain.handle(context)

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
        destroyed_calls = self._chain_stats['destroyed_chain_calls']
        self.renderer.draw_text(
            f"Групп: {total_groups} | Препятствий: {total_obstacles} | "
            f"Flyweight: {flyweight_count} | Proxy: {proxy_cache_size} | Cmd: {history_size}",
            10, 120, (200, 255, 200), size=24
        )
        self.renderer.draw_text(
            f"Chain: destroyed={destroyed_calls} | "
            f"bullet={self._chain_stats['bullet_chain_calls']} | "
            f"input={self._chain_stats['input_chain_calls']}",
            10, 150, (255, 200, 150), size=22
        )

        hints = [
            "Стрелки - движение | Пробел - выстрел | Z - отмена | Y - повтор",
            "1 - стандартные | 2 - быстрые | 3 - тяжёлые | 4 - разрывные",
            "X - формат настроек | C - клонировать | G - группы | F - Flyweight",
            "I - итераторы | H - история команд | P - Proxy | L - Chain stats",
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

        context = {
            'engine': self,
            'key': key,
            'handled': False
        }
        self._chain_stats['input_chain_calls'] += 1
        self._input_chain.handle(context)

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
        from iterators import ObstacleByTypeIterator
        for t in ['brick', 'metal', 'wood']:
            it = ObstacleByTypeIterator(self.obstacles, t)
            items = []
            while it.has_next():
                items.append(it.next())
            print(f"   Тип '{t}': {len(items)} объектов")

        print("\n3. DamagedObstacleIterator — повреждённые препятствия:")
        from iterators import DamagedObstacleIterator
        it = DamagedObstacleIterator(self.obstacles)
        damaged = []
        while it.has_next():
            damaged.append(it.next())
        print(f"   Повреждено: {len(damaged)}")

        print("\n4. DecoratedObstacleIterator — декорированные препятствия:")
        from iterators import DecoratedObstacleIterator
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
        from iterators import CompositeIterator
        it = CompositeIterator(self.obstacle_groups)
        leaves = []
        while it.has_next():
            leaves.append(it.next())
        print(f"   Всего листьев в дереве: {len(leaves)}")

        print("\n6. HighValueObstacleIterator — ценные препятствия (>=15 очков):")
        from iterators import HighValueObstacleIterator
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

    def _show_chain_stats(self):
        print("\n=== Статистика цепочек обязанностей (Chain of Responsibility) ===")
        print(f"Вызовов цепочки разрушения препятствий: "
              f"{self._chain_stats['destroyed_chain_calls']}")
        print(f"  Обработчики в цепочке (по порядку):")
        print(f"    1. ScoreHandler — начисление очков")
        print(f"    2. ExplosionHandler — создание взрыва")
        print(f"    3. RemoveFromCollectionsHandler — удаление из коллекций")
        print(f"    4. LoggingHandler — логирование события")
        print(f"    5. VictoryCheckHandler — проверка победы")
        print(f"\nВызовов цепочки пуль: {self._chain_stats['bullet_chain_calls']}")
        print(f"  Обработчики в цепочке (по порядку):")
        print(f"    1. BulletMovementHandler — обновление позиции пули")
        print(f"    2. OutOfBoundsHandler — проверка выхода за границы")
        print(f"    3. CollisionHandler — проверка столкновений")
        print(f"\nВызовов цепочки ввода: {self._chain_stats['input_chain_calls']}")
        print(f"  Обработчики в цепочке (по порядку):")
        print(f"    1. MovementInputHandler — клавиши стрелок")
        print(f"    2. ShootInputHandler — пробел (выстрел)")
        print(f"    3. BulletTypeInputHandler — клавиши 1-4 (тип снарядов)")
        print(f"    4. UndoRedoInputHandler — Z/Y (отмена/повтор)")
        print(f"    5. UtilityInputHandler — X/C/R/G/F/P/I/H/L (утилиты)")
        print("=" * 50)

    def reset_game(self):
        from commands import ResetGameCommand
        cmd = ResetGameCommand(self)
        self.invoker.execute(cmd)
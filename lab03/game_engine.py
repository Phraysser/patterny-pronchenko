import pygame
from tank import Tank
from bullet import Bullet
from obstacle import Obstacle
from explosion import Explosion
from level_loader import LevelLoader
from settings import Settings
from bullet_factory import (
    BulletFactory,
    StandardBulletFactory,
    FastBulletFactory,
    HeavyBulletFactory,
    ExplosiveBulletFactory
)
from renderer import Renderer
from pygame_renderer import PygameRenderer


class GameEngine:
    
    def __init__(self, screen):
        # === Singleton: получаем единственный экземпляр настроек ===
        self.settings = Settings.get_instance()
        self.settings.load_from_file()
        
        self.screen = screen
        
        # === Bridge (Мост): создаём реализацию рендерера ===
        # GameEngine работает с абстракцией Renderer,
        # а конкретная реализация (PygameRenderer) создаётся здесь.
        self.renderer = PygameRenderer(screen)
        
        self.tank = None
        self.bullets = []
        self.obstacles = []
        self.explosions = []
        self.score = 0
        self.pressed_keys = set()
        
        # Фабрика снарядов (по умолчанию — стандартные)
        self.bullet_factory = StandardBulletFactory()
        
        # Прототипы для клонирования
        self.bullet_prototype = None
        self.obstacle_prototypes = {}
        
        # Загрузчик уровней
        self.level_loader = LevelLoader()
        self.load_level(self.settings.default_level)
    
    
    def reload_settings(self):
        self.settings = Settings.get_instance()
        self.settings.load_from_file()
        
        if self.tank:
            self.tank.speed = self.settings.tank_speed
    
    def update_screen(self, screen):
        self.screen = screen
        # === Bridge: пересоздаём реализацию рендерера ===
        self.renderer = PygameRenderer(screen)
    
    def switch_storage_format(self, storage, file_path):

        self.settings.set_storage(storage, file_path)
        self.settings.save_to_file()
    
    
    def load_level(self, level_file):
        """Загрузить уровень из файла."""
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
        
        # Сохраняем прототипы препятствий по типу
        self.obstacle_prototypes = {}
        
        for obstacle_data in level_data['obstacles']:
            obstacle = Obstacle(obstacle_data)
            self.obstacles.append(obstacle)
            
            if obstacle.type not in self.obstacle_prototypes:
                self.obstacle_prototypes[obstacle.type] = obstacle
        
        # Прототип снаряда
        self.bullet_prototype = Bullet(
            (0, 0),
            'up',
            self.settings.bullet_speed,
            self.settings.bullet_damage
        )
    
    
    def update(self):
        self.update_tank()
        self.update_bullets()
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
        
        self.tank.update(self.settings.window_width, self.settings.window_height)
    
    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_out_of_bounds(self.settings.window_width,
                                       self.settings.window_height):
                self.bullets.remove(bullet)
    
    def update_explosions(self):
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.is_finished():
                self.explosions.remove(explosion)
    
    def check_collisions(self):
        for bullet in self.bullets[:]:
            for obstacle in self.obstacles[:]:
                if bullet.bounds.colliderect(obstacle.bounds):
                    obstacle.take_damage(bullet.damage)
                    
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    
                    if obstacle.is_destroyed:
                        self.explosions.append(
                            Explosion(obstacle.center, obstacle.size)
                        )
                        self.score += obstacle.points
                        self.obstacles.remove(obstacle)
                    break

    
    def render(self):
        # Очистка экрана через абстракцию
        self.renderer.clear((0, 0, 0))
        
        # Препятствия
        for obstacle in self.obstacles:
            obstacle.render(self.renderer)
        
        # Пули
        for bullet in self.bullets:
            bullet.render(self.renderer)
        
        # Взрывы
        for explosion in self.explosions:
            explosion.render(self.renderer)
        
        # Танк
        self.tank.render(self.renderer)
        
        # HUD (интерфейс)
        self.render_hud()
    
    def render_hud(self):
        # Счёт очков
        self.renderer.draw_text(
            f"Очки: {self.score}", 10, 10, (255, 255, 255), size=36, bold=True
        )
        
        # Информация о текущем типе снарядов
        factory_name = self._get_factory_display_name()
        self.renderer.draw_text(
            f"Снаряды: {factory_name}", 10, 50, (200, 200, 200), size=36
        )
        
        # Информация о текущем формате хранения настроек (Адаптер)
        storage_name = self.settings._storage.__class__.__name__
        self.renderer.draw_text(
            f"Настройки: {storage_name}", 10, 90, (150, 200, 255), size=24
        )
        
        # Подсказки управления
        hints = [
            "Стрелки - движение | Пробел - выстрел",
            "1 - стандартные | 2 - быстрые | 3 - тяжёлые | 4 - разрывные",
            "X - переключить формат настроек (JSON/XML) | C - клонировать препятствие",
            "R - сброс | F1 - настройки | Esc - выход"
        ]
        
        y_offset = self.settings.window_height - 100
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
        
        # Выстрел
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
            # Переключаемся на XML
            self.settings.set_storage(XmlSettingsStorage(), "settings.xml")
            self.settings.save_to_file()
            print("Формат настроек переключён на XML")
        else:
            # Переключаемся на JSON
            self.settings.set_storage(JsonSettingsStorage(), "settings.json")
            self.settings.save_to_file()
            print("Формат настроек переключён на JSON")
    
    
    def clone_obstacle(self, obstacle_type, new_x, new_y):
        if obstacle_type in self.obstacle_prototypes:
            prototype = self.obstacle_prototypes[obstacle_type]
            cloned = prototype.clone(new_x, new_y)
            self.obstacles.append(cloned)
            return cloned
        return None
    
    def _clone_random_obstacle(self):
        if self.obstacle_prototypes:
            obstacle_type = list(self.obstacle_prototypes.keys())[0]
            import random
            new_x = random.randint(100, self.settings.window_width - 150)
            new_y = random.randint(100, self.settings.window_height - 200)
            self.clone_obstacle(obstacle_type, new_x, new_y)
    
    # ==================== СБРОС ИГРЫ ====================
    
    def reset_game(self):
        self.load_level(self.settings.default_level)
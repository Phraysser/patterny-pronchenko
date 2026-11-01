import pygame
from tank import Tank
from bullet import Bullet
from obstacle import Obstacle
from explosion import Explosion
from level_loader import LevelLoader
from settings import Settings


class GameEngine:
    """
    Игровой движок, управляющий логикой игры.
    
    Использует паттерн Singleton для получения настроек
    через Settings.get_instance().
    """
    
    def __init__(self, screen):
        # === Singleton: получаем единственный экземпляр настроек ===
        self.settings = Settings.get_instance()
        self.settings.load_from_file()
        
        self.screen = screen
        self.tank = None
        self.bullets = []
        self.obstacles = []
        self.explosions = []
        self.score = 0
        self.pressed_keys = set()
        
        self.level_loader = LevelLoader()
        self.load_level(self.settings.default_level)
    
    def reload_settings(self):
        """
        Перезагрузить настройки из Singleton.
        Применяет новые параметры к существующим игровым объектам.
        """
        # === Singleton: настройки всегда актуальны из единого источника ===
        self.settings = Settings.get_instance()
        self.settings.load_from_file()
        
        if self.tank:
            self.tank.speed = self.settings.tank_speed
    
    def update_screen(self, screen):
        """Обновить ссылку на экран (при изменении размера окна)."""
        self.screen = screen
    
    def load_level(self, level_file):
        """Загрузить уровень из файла."""
        level_data = self.level_loader.load_level(level_file)
        
        # Создаём танк напрямую через конструктор
        self.tank = Tank(
            level_data['tank_start'][0],
            level_data['tank_start'][1],
            self.settings.tank_speed
        )
        
        self.obstacles = []
        self.bullets = []
        self.explosions = []
        self.score = 0
        
        # Создаём препятствия напрямую через конструктор
        for obstacle_data in level_data['obstacles']:
            self.obstacles.append(Obstacle(obstacle_data))
    
    # ==================== ОБНОВЛЕНИЕ ====================
    
    def update(self):
        """Главный метод обновления игровой логики."""
        self.update_tank()
        self.update_bullets()
        self.update_explosions()
        self.check_collisions()
    
    def update_tank(self):
        """Обновить позицию танка на основе нажатых клавиш."""
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
        """Обновить позиции пуль и удалить вылетевшие за границы."""
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_out_of_bounds(self.settings.window_width,
                                       self.settings.window_height):
                self.bullets.remove(bullet)
    
    def update_explosions(self):
        """Обновить анимации взрывов и удалить завершённые."""
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.is_finished():
                self.explosions.remove(explosion)
    
    def check_collisions(self):
        """Проверить столкновения пуль с препятствиями."""
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
    
    # ==================== ОТРИСОВКА ====================
    
    def render(self):
        """Отрисовать все игровые объекты на экран."""
        self.screen.fill((0, 0, 0))
        
        for obstacle in self.obstacles:
            obstacle.render(self.screen)
        
        for bullet in self.bullets:
            bullet.render(self.screen)
        
        for explosion in self.explosions:
            explosion.render(self.screen)
        
        self.tank.render(self.screen)
        
        self.render_score()
    
    def render_score(self):
        """Отрисовать счёт на экране."""
        font = pygame.font.Font(None, 36)
        text = font.render(f"Очки: {self.score}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))
    
    # ==================== ОБРАБОТКА ВВОДА ====================
    
    def handle_key_down(self, key):
        """Обработка нажатия клавиши."""
        self.pressed_keys.add(key)
        
        if key == pygame.K_SPACE:
            self.shoot()
    
    def handle_key_up(self, key):
        """Обработка отпускания клавиши."""
        self.pressed_keys.discard(key)
    
    def shoot(self):
        """Выстрел из танка."""
        bullet = Bullet(
            self.tank.position,
            self.tank.direction,
            self.settings.bullet_speed,
            self.settings.bullet_damage
        )
        self.bullets.append(bullet)
    
    # ==================== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ====================
    
    def reset_game(self):
        """Сбросить игру — перезагрузить текущий уровень."""
        self.load_level(self.settings.default_level)
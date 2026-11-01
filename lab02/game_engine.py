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


class GameEngine:
    """
    Игровой движок, управляющий логикой игры «Танки».
    
    Использует три порождающих паттерна проектирования:
    - Singleton: для получения единственного экземпляра настроек (Settings)
    - Prototype: для клонирования пуль и препятствий (методы clone)
    - Factory Method: для создания разных типов снарядов через фабрики
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
        
        # === Factory Method: фабрика для создания снарядов ===
        # По умолчанию используется фабрика стандартных снарядов
        self.bullet_factory = StandardBulletFactory()
        
        # === Prototype: прототипы для клонирования ===
        self.bullet_prototype = None
        self.obstacle_prototypes = {}
        
        # Загрузчик уровней из файла
        self.level_loader = LevelLoader()
        
        # Загружаем стартовый уровень
        self.load_level(self.settings.default_level)
    
    # ==================== УПРАВЛЕНИЕ НАСТРОЙКАМИ ====================
    
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
    
    # ==================== ЗАГРУЗКА УРОВНЯ ====================
    
    def load_level(self, level_file):
        """
        Загрузить уровень из файла и построить игровые объекты.
        Также сохраняет прототипы препятствий для дальнейшего клонирования.
        """
        level_data = self.level_loader.load_level(level_file)
        
        # Создаём танк напрямую через конструктор
        self.tank = Tank(
            level_data['tank_start'][0],
            level_data['tank_start'][1],
            self.settings.tank_speed
        )
        
        # Очищаем коллекции игровых объектов
        self.obstacles = []
        self.bullets = []
        self.explosions = []
        self.score = 0
        
        # === Prototype: сохраняем прототипы препятствий по типу ===
        # Это позволит клонировать препятствия нужного типа в дальнейшем
        self.obstacle_prototypes = {}
        
        for obstacle_data in level_data['obstacles']:
            obstacle = Obstacle(obstacle_data)
            self.obstacles.append(obstacle)
            
            # Сохраняем первый экземпляр каждого типа как прототип
            if obstacle.type not in self.obstacle_prototypes:
                self.obstacle_prototypes[obstacle.type] = obstacle
        
        # === Prototype: создаём прототип снаряда для клонирования ===
        self.bullet_prototype = Bullet(
            (0, 0),
            'up',
            self.settings.bullet_speed,
            self.settings.bullet_damage
        )
    
    # ==================== ОБНОВЛЕНИЕ ИГРОВОЙ ЛОГИКИ ====================
    
    def update(self):
        """Главный метод обновления игровой логики (вызывается каждый кадр)."""
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
        """Обновить позиции пуль и удалить вылетевшие за границы экрана."""
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
                    # Препятствие получает урон
                    obstacle.take_damage(bullet.damage)
                    
                    # Удаляем снаряд после попадания
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    
                    # Если препятствие разрушено — создаём взрыв и начисляем очки
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
        
        # Отрисовка препятствий
        for obstacle in self.obstacles:
            obstacle.render(self.screen)
        
        # Отрисовка пуль
        for bullet in self.bullets:
            bullet.render(self.screen)
        
        # Отрисовка взрывов
        for explosion in self.explosions:
            explosion.render(self.screen)
        
        # Отрисовка танка
        self.tank.render(self.screen)
        
        # Отрисовка HUD (счёт, информация о типе снарядов, подсказки)
        self.render_hud()
    
    def render_hud(self):
        """
        Отрисовать интерфейс — счёт, текущий тип снарядов и подсказки управления.
        Демонстрирует использование паттерна Factory Method (показ текущей фабрики).
        """
        font = pygame.font.Font(None, 36)
        
        # Счёт очков
        score_text = font.render(f"Очки: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Информация о текущем типе снарядов (Factory Method)
        factory_name = self._get_factory_display_name()
        type_text = font.render(f"Снаряды: {factory_name}", True, (200, 200, 200))
        self.screen.blit(type_text, (10, 50))
        
        # Подсказки управления
        hint_font = pygame.font.Font(None, 24)
        hints = [
            "Стрелки - движение | Пробел - выстрел",
            "1 - стандартные | 2 - быстрые | 3 - тяжёлые | 4 - разрывные (Factory Method)",
            "C - клонировать препятствие (Prototype) | R - сброс | F1 - настройки | Esc - выход"
        ]
        
        y_offset = self.settings.window_height - 80
        for hint in hints:
            hint_text = hint_font.render(hint, True, (150, 150, 150))
            self.screen.blit(hint_text, (10, y_offset))
            y_offset += 25
    
    def _get_factory_display_name(self):
        """Получить отображаемое имя текущей фабрики снарядов."""
        if isinstance(self.bullet_factory, StandardBulletFactory):
            return "Стандартные"
        elif isinstance(self.bullet_factory, FastBulletFactory):
            return "Быстрые"
        elif isinstance(self.bullet_factory, HeavyBulletFactory):
            return "Тяжёлые"
        elif isinstance(self.bullet_factory, ExplosiveBulletFactory):
            return "Разрывные"
        return "Неизвестные"
    
    # ==================== ОБРАБОТКА ВВОДА ====================
    
    def handle_key_down(self, key):
        """Обработка нажатия клавиши."""
        self.pressed_keys.add(key)
        
        # Выстрел
        if key == pygame.K_SPACE:
            self.shoot()
        
        # === Factory Method: переключение типов снарядов клавишами 1-4 ===
        elif key == pygame.K_1:
            self.switch_bullet_type('standard')
        elif key == pygame.K_2:
            self.switch_bullet_type('fast')
        elif key == pygame.K_3:
            self.switch_bullet_type('heavy')
        elif key == pygame.K_4:
            self.switch_bullet_type('explosive')
        
        # === Prototype: клонирование препятствия клавишей C ===
        elif key == pygame.K_c:
            self._clone_random_obstacle()
    
    def handle_key_up(self, key):
        """Обработка отпускания клавиши."""
        self.pressed_keys.discard(key)
    
    # ==================== СТРЕЛЬБА (Factory Method) ====================
    
    def shoot(self):
        """
        Выстрел из танка.
        Использует паттерн Factory Method: снаряд создаётся через текущую фабрику.
        """
        bullet = self.bullet_factory.create_bullet(
            self.tank.position,
            self.tank.direction,
            self.settings.bullet_speed,
            self.settings.bullet_damage
        )
        self.bullets.append(bullet)
    
    def switch_bullet_type(self, bullet_type):
        """
        Переключить тип снарядов.
        Демонстрация паттерна Factory Method — замена фабрики на лету.
        """
        if bullet_type == 'standard':
            self.bullet_factory = StandardBulletFactory()
        elif bullet_type == 'fast':
            self.bullet_factory = FastBulletFactory()
        elif bullet_type == 'heavy':
            self.bullet_factory = HeavyBulletFactory()
        elif bullet_type == 'explosive':
            self.bullet_factory = ExplosiveBulletFactory()
    
    # ==================== КЛОНИРОВАНИЕ (Prototype) ====================
    
    def clone_obstacle(self, obstacle_type, new_x, new_y):
        """
        Клонировать препятствие определённого типа.
        Демонстрация паттерна Prototype — создание копии через метод clone().
        """
        if obstacle_type in self.obstacle_prototypes:
            prototype = self.obstacle_prototypes[obstacle_type]
            cloned = prototype.clone(new_x, new_y)
            self.obstacles.append(cloned)
            return cloned
        return None
    
    def clone_bullet(self):
        """
        Клонировать снаряд-прототип.
        Демонстрация паттерна Prototype для класса Bullet.
        """
        if self.bullet_prototype is not None:
            cloned = self.bullet_prototype.clone()
            return cloned
        return None
    
    def _clone_random_obstacle(self):
        """
        Внутренний метод: клонировать случайное препятствие из имеющихся прототипов.
        Вызывается при нажатии клавиши C.
        """
        if self.obstacle_prototypes:
            # Берём первый доступный тип прототипа
            obstacle_type = list(self.obstacle_prototypes.keys())[0]
            # Позиция для клона — случайная в пределах поля
            import random
            new_x = random.randint(100, self.settings.window_width - 150)
            new_y = random.randint(100, self.settings.window_height - 150)
            self.clone_obstacle(obstacle_type, new_x, new_y)
    
    # ==================== СБРОС ИГРЫ ====================
    
    def reset_game(self):
        """Сбросить игру — перезагрузить текущий уровень."""
        self.load_level(self.settings.default_level)
    
    # ==================== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ====================
    
    def get_score(self):
        """Получить текущий счёт."""
        return self.score
    
    def get_current_bullet_type(self):
        """Получить текущий тип снарядов."""
        return self._get_factory_display_name()
    
    def get_obstacle_types(self):
        """Получить список доступных типов препятствий (прототипов)."""
        return list(self.obstacle_prototypes.keys())
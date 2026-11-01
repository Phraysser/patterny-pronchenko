from bullet import Bullet


class BulletFactory:
    """
    Базовый класс фабрики снарядов.
    Реализует паттерн Фабричный метод.
    """
    
    def create_bullet(self, start_position, direction, speed, damage):
        """
        Фабричный метод: создаёт снаряд.
        Подклассы могут переопределить этот метод для создания разных типов снарядов.
        """
        return Bullet(start_position, direction, speed, damage)


class StandardBulletFactory(BulletFactory):
    """
    Фабрика стандартных снарядов.
    Создаёт обычные жёлтые снаряды.
    """
    
    def create_bullet(self, start_position, direction, speed, damage):
        """Создаёт стандартный снаряд."""
        return Bullet(start_position, direction, speed, damage)


class FastBulletFactory(BulletFactory):
    """
    Фабрика быстрых снарядов.
    Создаёт снаряды с увеличенной скоростью.
    """
    
    def create_bullet(self, start_position, direction, speed, damage):
        """Создаёт быстрый снаряд (скорость увеличена в 1.5 раза)."""
        fast_speed = speed * 1.5
        return Bullet(start_position, direction, fast_speed, damage)


class HeavyBulletFactory(BulletFactory):
    """
    Фабрика тяжёлых снарядов.
    Создаёт снаряды с увеличенным уроном.
    """
    
    def create_bullet(self, start_position, direction, speed, damage):
        """Создаёт тяжёлый снаряд (урон увеличен в 2 раза)."""
        heavy_damage = damage * 2
        return Bullet(start_position, direction, speed, heavy_damage)


class ExplosiveBulletFactory(BulletFactory):
    """
    Фабрика разрывных снарядов.
    Создаёт снаряды с увеличенным размером и уроном.
    """
    
    def create_bullet(self, start_position, direction, speed, damage):
        """Создаёт разрывной снаряд (больше размер и урон)."""
        bullet = Bullet(start_position, direction, speed, damage * 3)
        bullet.width = 10
        bullet.height = 10
        return bullet
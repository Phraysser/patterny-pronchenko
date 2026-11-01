from bullet import Bullet


class BulletFactory:

    
    def create_bullet(self, start_position, direction, speed, damage):

        return Bullet(start_position, direction, speed, damage)


class StandardBulletFactory(BulletFactory):

    
    def create_bullet(self, start_position, direction, speed, damage):
        return Bullet(start_position, direction, speed, damage)


class FastBulletFactory(BulletFactory):
    
    def create_bullet(self, start_position, direction, speed, damage):
        fast_speed = speed * 1.5
        return Bullet(start_position, direction, fast_speed, damage)


class HeavyBulletFactory(BulletFactory):
    
    def create_bullet(self, start_position, direction, speed, damage):
        """Создаёт тяжёлый снаряд (урон увеличен в 2 раза)."""
        heavy_damage = damage * 2
        return Bullet(start_position, direction, speed, heavy_damage)


class ExplosiveBulletFactory(BulletFactory):
    
    def create_bullet(self, start_position, direction, speed, damage):
        """Создаёт разрывной снаряд (больше размер и урон)."""
        bullet = Bullet(start_position, direction, speed, damage * 3)
        bullet.width = 10
        bullet.height = 10
        return bullet
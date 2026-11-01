from abc import ABC, abstractmethod
from obstacle_decorator import (
    ArmoredObstacleDecorator,
    ValuableObstacleDecorator,
    RegeneratingObstacleDecorator
)


class Handler(ABC):
    def __init__(self):
        self._next_handler = None

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, context):
        pass

    def pass_to_next(self, context):
        if self._next_handler is not None:
            return self._next_handler.handle(context)
        return None


class ObstacleDestroyedHandler(Handler):
    pass


class ScoreHandler(ObstacleDestroyedHandler):
    def handle(self, context):
        engine = context['engine']
        obstacle = context['obstacle']
        engine.score += obstacle.points
        context['points_gained'] = obstacle.points
        return self.pass_to_next(context)


class ExplosionHandler(ObstacleDestroyedHandler):
    def handle(self, context):
        from explosion import Explosion
        engine = context['engine']
        obstacle = context['obstacle']
        explosion = Explosion(obstacle.center, obstacle.size)
        engine.explosions.append(explosion)
        return self.pass_to_next(context)


class RemoveFromCollectionsHandler(ObstacleDestroyedHandler):
    def handle(self, context):
        engine = context['engine']
        obstacle = context['obstacle']
        if obstacle in engine.obstacles:
            engine.obstacles.remove(obstacle)
        engine._remove_from_groups(obstacle)
        return self.pass_to_next(context)


class LoggingHandler(ObstacleDestroyedHandler):
    def handle(self, context):
        obstacle = context['obstacle']
        points = context.get('points_gained', obstacle.points)
        decorator_info = ""
        if isinstance(obstacle, ArmoredObstacleDecorator):
            decorator_info = " [Бронирован]"
        elif isinstance(obstacle, ValuableObstacleDecorator):
            decorator_info = " [Ценный]"
        elif isinstance(obstacle, RegeneratingObstacleDecorator):
            decorator_info = " [Регенерирующий]"
        print(f"[LOG] Разрушено препятствие: {obstacle.type} "
              f"({obstacle.x}, {obstacle.y}){decorator_info} "
              f"— получено {points} очков")
        return self.pass_to_next(context)


class VictoryCheckHandler(ObstacleDestroyedHandler):
    def handle(self, context):
        engine = context['engine']
        remaining = len(engine.obstacles)
        if remaining == 0:
            print(f"[ПОБЕДА] Все препятствия разрушены! "
                  f"Итоговый счёт: {engine.score}")
            context['victory'] = True
        return self.pass_to_next(context)


class BulletHandler(Handler):
    pass


class OutOfBoundsHandler(BulletHandler):
    def handle(self, context):
        engine = context['engine']
        bullet = context['bullet']
        if bullet.is_out_of_bounds(engine.settings.window_width,
                                    engine.settings.window_height):
            if bullet in engine.bullets:
                engine.bullets.remove(bullet)
            context['removed'] = True
            return None
        return self.pass_to_next(context)


class BulletMovementHandler(BulletHandler):
    def handle(self, context):
        bullet = context['bullet']
        bullet.update()
        return self.pass_to_next(context)


class CollisionHandler(BulletHandler):
    def handle(self, context):
        from iterators import ObstacleIterator
        engine = context['engine']
        bullet = context['bullet']
        obstacle_iter = ObstacleIterator(engine.obstacles)
        while obstacle_iter.has_next():
            obstacle = obstacle_iter.next()
            if bullet.get_bounds().colliderect(obstacle.get_bounds()):
                obstacle.take_damage(bullet.damage)
                if bullet in engine.bullets:
                    engine.bullets.remove(bullet)
                context['hit_obstacle'] = obstacle
                if obstacle.is_destroyed:
                    context['destroyed'] = True
                    engine._handle_obstacle_destroyed(obstacle)
                return None
        return self.pass_to_next(context)


class InputHandler(Handler):
    pass


class MovementInputHandler(InputHandler):
    def handle(self, context):
        import pygame
        engine = context['engine']
        key = context['key']
        dx, dy = 0, 0
        if key == pygame.K_UP:
            dy = -engine.tank.speed
        elif key == pygame.K_DOWN:
            dy = engine.tank.speed
        elif key == pygame.K_LEFT:
            dx = -engine.tank.speed
        elif key == pygame.K_RIGHT:
            dx = engine.tank.speed
        if dx != 0 or dy != 0:
            from commands import MoveCommand
            cmd = MoveCommand(
                engine.tank, dx, dy,
                engine.settings.window_width,
                engine.settings.window_height
            )
            engine.invoker.execute(cmd)
            context['handled'] = True
            return None
        return self.pass_to_next(context)


class ShootInputHandler(InputHandler):
    def handle(self, context):
        import pygame
        engine = context['engine']
        key = context['key']
        if key == pygame.K_SPACE:
            from commands import ShootCommand
            cmd = ShootCommand(engine)
            engine.invoker.execute(cmd)
            context['handled'] = True
            return None
        return self.pass_to_next(context)


class BulletTypeInputHandler(InputHandler):
    def handle(self, context):
        import pygame
        engine = context['engine']
        key = context['key']
        mapping = {
            pygame.K_1: 'standard',
            pygame.K_2: 'fast',
            pygame.K_3: 'heavy',
            pygame.K_4: 'explosive',
        }
        if key in mapping:
            from commands import SwitchBulletTypeCommand
            cmd = SwitchBulletTypeCommand(engine, mapping[key])
            engine.invoker.execute(cmd)
            context['handled'] = True
            return None
        return self.pass_to_next(context)


class UndoRedoInputHandler(InputHandler):
    def handle(self, context):
        import pygame
        engine = context['engine']
        key = context['key']
        if key == pygame.K_z:
            engine.invoker.undo()
            context['handled'] = True
            return None
        if key == pygame.K_y:
            engine.invoker.redo()
            context['handled'] = True
            return None
        return self.pass_to_next(context)


class UtilityInputHandler(InputHandler):
    def handle(self, context):
        import pygame
        engine = context['engine']
        key = context['key']

        if key == pygame.K_x:
            from commands import ToggleStorageFormatCommand
            cmd = ToggleStorageFormatCommand(engine.settings)
            engine.invoker.execute(cmd)
            context['handled'] = True
            return None

        if key == pygame.K_c:
            import random
            if engine.obstacle_prototypes:
                obstacle_type = list(engine.obstacle_prototypes.keys())[0]
                new_x = random.randint(100, engine.settings.window_width - 150)
                new_y = random.randint(100, engine.settings.window_height - 200)
                from commands import CloneObstacleCommand
                cmd = CloneObstacleCommand(engine, obstacle_type, new_x, new_y)
                engine.invoker.execute(cmd)
            context['handled'] = True
            return None

        if key == pygame.K_r:
            from commands import ResetGameCommand
            cmd = ResetGameCommand(engine)
            engine.invoker.execute(cmd)
            context['handled'] = True
            return None

        if key == pygame.K_g:
            engine._show_groups_info()
            context['handled'] = True
            return None

        if key == pygame.K_f:
            engine._show_flyweight_info()
            context['handled'] = True
            return None

        if key == pygame.K_p:
            engine._show_proxy_stats()
            context['handled'] = True
            return None

        if key == pygame.K_i:
            engine._show_iterators_demo()
            context['handled'] = True
            return None

        if key == pygame.K_h:
            engine._show_command_history()
            context['handled'] = True
            return None

        if key == pygame.K_l:
            engine._show_chain_stats()
            context['handled'] = True
            return None

        return self.pass_to_next(context)


class ChainBuilder:
    @staticmethod
    def build_obstacle_destroyed_chain():
        head = ScoreHandler()
        head.set_next(ExplosionHandler()) \
            .set_next(RemoveFromCollectionsHandler()) \
            .set_next(LoggingHandler()) \
            .set_next(VictoryCheckHandler())
        return head

    @staticmethod
    def build_bullet_chain():
        head = BulletMovementHandler()
        head.set_next(OutOfBoundsHandler()) \
            .set_next(CollisionHandler())
        return head

    @staticmethod
    def build_input_chain():
        head = MovementInputHandler()
        head.set_next(ShootInputHandler()) \
            .set_next(BulletTypeInputHandler()) \
            .set_next(UndoRedoInputHandler()) \
            .set_next(UtilityInputHandler())
        return head
import pygame
import sys
from game_engine import GameEngine
from settings import Settings
from settings_dialog import SettingsDialog


def main():
    pygame.init()
    
    # === Singleton: получаем единственный экземпляр настроек ===
    settings = Settings.get_instance()
    settings.load_from_file()
    
    screen = pygame.display.set_mode(
        (settings.window_width, settings.window_height)
    )
    pygame.display.set_caption(settings.game_title)
    
    clock = pygame.time.Clock()
    game = GameEngine(screen)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F1:
                    dialog = SettingsDialog(settings)
                    if dialog.show():
                        settings.save_to_file()
                        game.reload_settings()
                        screen = pygame.display.set_mode(
                            (settings.window_width, settings.window_height)
                        )
                        pygame.display.set_caption(settings.game_title)
                        game.update_screen(screen)
                elif event.key == pygame.K_r:
                    game.reset_game()
                else:
                    game.handle_key_down(event.key)
            elif event.type == pygame.KEYUP:
                game.handle_key_up(event.key)
        
        game.update()
        game.render()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
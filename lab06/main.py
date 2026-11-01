import pygame
import sys
from settings import Settings
from game_facade import GameFacade


def main():
    pygame.init()

    settings = Settings.get_instance()
    settings.load_from_file()

    screen = pygame.display.set_mode(
        (settings.window_width, settings.window_height)
    )
    pygame.display.set_caption(settings.game_title)

    facade = GameFacade(screen)
    facade.start()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
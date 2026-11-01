import pygame
from settings import Settings
from game_engine import GameEngine
from pygame_renderer import PygameRenderer
from json_settings_storage import JsonSettingsStorage
from xml_settings_storage import XmlSettingsStorage


class GameFacade:
    def __init__(self, screen):
        self._screen = screen
        self._settings = Settings.get_instance()
        self._settings.load_from_file()
        self._engine = GameEngine(screen)
        self._running = False
        self._clock = pygame.time.Clock()

    def start(self):
        self._running = True
        while self._running:
            if not self._handle_events():
                break
            self._engine.update()
            self._engine.render()
            pygame.display.flip()
            self._clock.tick(60)
        self._cleanup()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_F1:
                    self._open_settings()
                else:
                    self._engine.handle_key_down(event.key)
            elif event.type == pygame.KEYUP:
                self._engine.handle_key_up(event.key)
        return True

    def _open_settings(self):
        from settings_dialog import SettingsDialog
        dialog = SettingsDialog(self._settings)
        if dialog.show():
            self._settings.save_to_file()
            self._engine.reload_settings()
            self._screen = pygame.display.set_mode(
                (self._settings.window_width, self._settings.window_height)
            )
            pygame.display.set_caption(self._settings.game_title)
            self._engine.update_screen(self._screen)

    def _cleanup(self):
        self._running = False

    def stop(self):
        self._running = False

    def reset(self):
        self._engine.reset_game()

    def get_score(self):
        return self._engine.score

    def get_settings(self):
        return self._settings

    def get_engine(self):
        return self._engine

    def switch_storage_to_json(self):
        self._settings.set_storage(JsonSettingsStorage(), "settings.json")
        self._settings.save_to_file()

    def switch_storage_to_xml(self):
        self._settings.set_storage(XmlSettingsStorage(), "settings.xml")
        self._settings.save_to_file()
import pygame
import settings

class Booster:
    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y
        self.width: int = settings.BOOSTER_WIDTH
        self.height: int = settings.BOOSTER_HEIGHT
        self.activate = True

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def update(self, dt: float) -> None:
        self.x += -settings.MAIN_SCROLL_SPEED * dt

    def is_out_of_game(self) -> bool:
        return self.x < -self.width

    def render(self, surface: pygame.Surface) -> None:
        if self.activate:
            surface.blit(settings.TEXTURES["booster"], self.get_rect())
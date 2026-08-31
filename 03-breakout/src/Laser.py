import pygame

class Laser:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.width = 3
        self.height = 8
        self.vy = -300
        self.active = True

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, dt: float) -> None:
        self.y += self.vy * dt

        if self.y + self.height < 0:
            self.active = False

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (255, 0, 0), self.get_collision_rect())
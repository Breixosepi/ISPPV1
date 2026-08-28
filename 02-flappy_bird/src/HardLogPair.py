
import random 
import pygame 
import settings
from src.LogPair import LogPair

class HardLogPair(LogPair):
    def __init__(self, x: float, y: float, initial_gap : float =90.0) -> None:
        super().__init__(x, y)
        self.gap = initial_gap
        self.is_dynamic = random.random() < 0.7
        if self.is_dynamic:
            self.vy: float = random.choice([-50, 50])  
            self.gap_vy: float = random.choice([-50, 50])
        else:
            self.vy: float = 0.0
            self.gap_vy: float = 0.0
        

    def update(self,dt:float) ->None:
        super().update(dt)

        if not self.is_dynamic:
            return
            
        self.y += self.vy * dt
        min_y = -settings.LOG_HEIGHT + 20
        max_y = (settings.VIRTUAL_HEIGHT - settings.GROUND_HEIGHT - self.gap - settings.LOG_HEIGHT - 20)

        if self.y < min_y:
            self.y = min_y
            self.vy *= -1
        elif self.y > max_y:
            self.y = max_y
            self.vy *= -1


        self.gap += self.gap_vy * dt
        min_gap = 0.0
        max_gap = settings.BIRD_HEIGHT * 4

        if self.gap <= min_gap:
            self.gap = min_gap
            self.gap_vy *= -1
            settings.SOUNDS["log_bump"].play()

        elif self.gap > max_gap:
            self.gap = max_gap
            self.gap_vy *= -1

import random
from typing import Any, Dict, List
from src.Paddle import Paddle
from src.Ball import Ball
import settings

class CatchController:
    def __init__(self, paddle: Paddle):
        self.paddle = paddle
        self.active = False
        self.timer = 0.0
        self.caught_balls: List[Dict[str, Any]] = []

    def activate(self, duration: float = 5.0) -> None:
        self.active = True
        self.timer = duration

    def has_caught_balls(self) -> bool:
        return len(self.caught_balls) > 0

    def try_catch(self, ball: Ball)-> bool:
        if not self.active:
            return False

        offset_x = ball.x - self.paddle.x
        offset_x = max(0, min(self.paddle.width - ball.width, offset_x))
        self.caught_balls.append({"ball": ball, "offset_x": offset_x})
        ball.vx, ball.vy = 0, 0

        return True

    def update(self, dt: float) -> None:
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = False
                if self.has_caught_balls():
                    self.release_balls()

            for entry in self.caught_balls:
                ball = entry["ball"]
                ball.x = self.paddle.x + entry["offset_x"]
                ball.y = self.paddle.y - ball.height

    def release_balls(self) -> None:
        for entry in self.caught_balls:
            ball = entry["ball"]
            ball.vx = random.randint(-100, 100)
            ball.vy = random.randint(-150, -100)

        settings.SOUNDS["paddle_hit"].stop()
        settings.SOUNDS["paddle_hit"].play()
        self.caught_balls.clear()
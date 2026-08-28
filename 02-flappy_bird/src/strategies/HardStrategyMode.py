

from src.HardLogPair import HardLogPair
import settings
from src.strategies.StrategyMode import StrategyMode
import random


class HardStrategyMode(StrategyMode):
    def __init__(self):
        self.spawn_timer = float = 0.0
        self.min_spawn_time = float = 1.2
        self.max_spawn_time = float = 2.4
        self.next_spawn_time = float = random.uniform(self.min_spawn_time, self.max_spawn_time)

    def on_input(self,bird, input_id: str, input_data) -> None:
        if input_id == "jump" and input_data.pressed:
            bird.jump()

        elif input_id == "left":
            if input_data.pressed:
                bird.vx = -150
            elif input_data.released:
                bird.vx = 0

        elif input_id == "right":
            if input_data.pressed:
                bird.vx = 150
            elif input_data.released:
                bird.vx = 0

    def update_world(self, world, dt: float) -> None:
        world.generate_logs = False
        self.spawn_timer += dt
        if self.spawn_timer >= self.next_spawn_time:
            self.spawn_timer = 0.0
            self._generate_log_pair(world)

        world.update(dt)

    def _generate_log_pair(self, world) -> None:
            lerp = lambda a,b,t: a + (b - a) * t
            t = (self.next_spawn_time - self.min_spawn_time) / (self.max_spawn_time - self.min_spawn_time)
            max_delta_y = lerp(35.0, 110.0, t)
            delta_y = random.uniform(-max_delta_y, max_delta_y)
            new_y = world.last_log_y + delta_y

            initial_gap = random.uniform(80.0 , 120.0)
            min_y_limit = -settings.LOG_HEIGHT + 20
            max_y_limit = (
                settings.VIRTUAL_HEIGHT
                - settings.GROUND_HEIGHT
                - initial_gap
                - settings.LOG_HEIGHT
                - 20
            )
            new_y = max(min_y_limit, min(new_y, max_y_limit))
            world.last_log_y = new_y
            world.logs.append(HardLogPair(settings.VIRTUAL_WIDTH, new_y, initial_gap))
            self.next_spawn_time = random.uniform(self.min_spawn_time, self.max_spawn_time)
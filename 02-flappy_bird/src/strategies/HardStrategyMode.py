


from src.strategies.StrategyMode import StrategyMode


class HardStrategyMode(StrategyMode):
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
        world.update(dt)
import pygame
from src.entity.Bird import Bird

class BirdManager:
    def __init__(self, world, start_x, start_y):
        self.world = world
        self.start_x = start_x
        self.start_y = start_y
        self.birds = []
        self.has_split = False
        self._spawn_initial_bird()

    def _spawn_initial_bird(self):
        self.birds = [Bird(self.world, self.start_x, self.start_y)]
        self.has_split = False
        self.can_split = True

    @property
    def primary_bird(self):
        return self.birds[0]

    def reset(self):
        for bird in self.birds[1:]:
            self.world.destroy_body(bird.body)
        
        self.birds = [self.primary_bird]
        self.primary_bird.reset()
        self.has_split = False
        self.can_split = True

    def split(self):
        if self.has_split or not self.can_split:
            return
            
        self.has_split = True
        
        original_bird = self.primary_bird
        vel = original_bird.body.velocity
        pos = original_bird.body.position
        
        v_original = pygame.Vector2(vel.x, vel.y)
        
        v_up = v_original.rotate(-20)
        v_down = v_original.rotate(20)
        
        clone_up = Bird(self.world, pos.x, pos.y)
        clone_up.body.velocity = (v_up.x, v_up.y)
        
        clone_down = Bird(self.world, pos.x, pos.y)
        clone_down.body.velocity = (v_down.x, v_down.y)
        
        self.birds.append(clone_up)
        self.birds.append(clone_down)

    def are_all_idle(self, linear_threshold, angular_threshold) -> bool:
        for bird in self.birds:
            v = bird.body.velocity
            speed = pygame.Vector2(v.x, v.y).length()
            angular_speed = abs(bird.body.angular_velocity)
            
            if speed >= linear_threshold or angular_speed >= angular_threshold:
                return False
                
        return True

    def handle_collision(self, data_a, data_b) -> None:
        if data_a in self.birds or data_b in self.birds:
            self.can_split = False

    def render(self, surface, camera):
        for bird in self.birds:
            bird.render(surface, camera)
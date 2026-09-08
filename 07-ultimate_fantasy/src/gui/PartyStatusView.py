from typing import Any

import pygame

import settings
from src.entity.Party import Party
from src.gui.Panel import Panel


class PartyStatusView:
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        party: Party,
    ) -> None:
        self.panel = Panel(x, y, width, height)
        self.party = party
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.selected_index = 0
        self.active = False  
        self.characters = list(party.characters.values())
        
        self.font = settings.FONTS["small"]
        self.cursor_texture = settings.TEXTURES["cursor-right"]

    def update(self, dt: float) -> None:
        pass

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not self.active or not input_data.pressed:
            return

        if input_id == "move_up":
            self.selected_index = (self.selected_index - 1) % len(self.characters)
            settings.SOUNDS["blip"].stop()
            settings.SOUNDS["blip"].play()
        elif input_id == "move_down":
            self.selected_index = (self.selected_index + 1) % len(self.characters)
            settings.SOUNDS["blip"].stop()
            settings.SOUNDS["blip"].play()

    def get_selected_character(self) -> Any:
        return self.characters[self.selected_index]

    def render(self, surface: pygame.Surface) -> None:
        self.panel.render(surface)

        start_x = self.x + 8
        start_y = self.y + 4
        row_height = 14

        for i, character in enumerate(self.characters):
            row_y = start_y + i * row_height
            
            if self.active and i == self.selected_index:
                surface.blit(self.cursor_texture, (start_x - 6, row_y + 1))
            
            # Name
            name_text = self.font.render(character.name, True, (255, 255, 255))
            if character.dead:
                name_text.set_alpha(100)
            surface.blit(name_text, (start_x + 4, row_y))

            # HP Text
            hp_text = self.font.render(f"HP {character.current_hp}/{character.hp}", True, (255, 255, 255))
            if character.dead:
                hp_text.set_alpha(100)
            surface.blit(hp_text, (start_x + 60, row_y))
            
            # HP Bar (Mini)
            bar_w = 30
            bar_h = 3
            bar_x = start_x + 120
            bar_y = row_y + 3
            pygame.draw.rect(surface, (50, 0, 0), (bar_x, bar_y, bar_w, bar_h))
            if character.current_hp > 0:
                hp_ratio = character.current_hp / character.hp
                pygame.draw.rect(surface, (189, 32, 32), (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))

        # We use a vertical divider
        divider_x = self.x + 165
        pygame.draw.line(surface, (255, 255, 255), (divider_x, self.y + 4), (divider_x, self.y + self.height - 4))

        selected = self.get_selected_character()
        detail_x = divider_x + 8
        detail_y = self.y + 6

        # Render selected character sprite
        alpha = 100 if selected.dead else 255
        try:
            frame = selected.animations["idle-down"].frames[0]
            sprite_surface = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
            sprite_surface.blit(settings.TEXTURES[selected.texture], (0, 0), frame)
            if alpha < 255:
                sprite_surface.set_alpha(alpha)
            scaled_sprite = pygame.transform.scale(sprite_surface, (frame.width * 2, frame.height * 2))
            surface.blit(scaled_sprite, (detail_x, detail_y + 4))
        except Exception:
            pass 

        info_x = detail_x + 40
        
        # Row 1: Name and Level
        title_text = self.font.render(f"{selected.name} (Lv {selected.level})", True, (255, 255, 255))
        title_text.set_alpha(alpha)
        surface.blit(title_text, (info_x, detail_y))

        # Row 2: EXP
        exp_text = self.font.render(f"EXP: {selected.current_exp}/{selected.exp_to_level}", True, (255, 255, 255))
        exp_text.set_alpha(alpha)
        surface.blit(exp_text, (info_x, detail_y + 12))

        # Row 3: Atk / Def / Mag
        atk_def_text = self.font.render(f"Atk: {selected.attack}  Def: {selected.defense}", True, (255, 255, 255))
        atk_def_text.set_alpha(alpha)
        surface.blit(atk_def_text, (info_x, detail_y + 24))

        # Row 4: Mag (Nueva fila abajo)
        mag_text = self.font.render(f"Mag: {selected.magic}", True, (255, 255, 255))
        mag_text.set_alpha(alpha)
        surface.blit(mag_text, (info_x, detail_y + 36)) # <-- Bajamos 12 píxeles más

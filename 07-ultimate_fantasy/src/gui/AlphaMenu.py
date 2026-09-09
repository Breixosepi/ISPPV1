from typing import Any, List, Optional, Sequence, Tuple

import pygame

from gale.ui.cursor import Cursor
from gale.ui.list_view import ListView
from gale.ui.theme import Theme

import settings
from src.gui.Menu import Menu, _MENU_THEME

Item = Tuple[str, "callable"]


class AlphaListView(ListView):

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        items: Sequence[Item],
        alphas: Sequence[int],
        font: Optional[pygame.font.Font] = None,
        cursor: Optional[Cursor] = None,
        theme: Optional[Theme] = None,
    ) -> None:
        super().__init__(x, y, width, height, items, font=font, cursor=cursor, theme=theme)
        self.alphas = alphas

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible or not self.items:
            return

        font = self._font if self._font is not None else self.theme.font

        for index, (label, _) in enumerate(self.items):
            row_rect = self.row_rect(index)

            if index == self.selected_index:
                fill_color = self.theme.focus_color if self.focused else self.theme.hover_color
                pygame.draw.rect(surface, fill_color, row_rect)

            from gale.text import Text
            alpha = self.alphas[index] if index < len(self.alphas) else 255
            text_obj = Text(
                label,
                font,
                row_rect.centerx,
                row_rect.centery,
                self.theme.text_color,
                center=True,
            )
            if alpha < 255:
                text_obj.text.set_alpha(alpha)
            text_obj.render(surface)

            if index == self.selected_index and self.cursor is not None:
                self.cursor.render(surface, (row_rect.x - 4, row_rect.centery))


class AlphaMenu(Menu):

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        items: Sequence[Item],
        alphas: Sequence[int],
        show_cursor: bool = True,
        font: Optional[pygame.font.Font] = None,
    ) -> None:
        super().__init__(x, y, width, height, items, show_cursor, font)
        
        self.list_view = AlphaListView(
            x + 4,
            y + 3,
            width - 8,
            height - 6,
            items=items,
            alphas=alphas,
            font=font or settings.FONTS["medium"],
            cursor=None,
            theme=_MENU_THEME,
        )
        self.list_view.focused = True

    def render(self, surface: pygame.Surface) -> None:
        self.panel.render(surface)
        self.list_view.render(surface)

        if self.cursor is not None and self.list_view.items:
            row_rect = self.list_view.row_rect(self.list_view.selected_index)
            # Move cursor a bit more to the left to avoid overlapping the text
            cursor_x = self.panel.x - 4
            self.cursor.render(surface, (cursor_x, row_rect.centery))

    @staticmethod
    def build_action_items(
        entity: Any, 
        make_selector_func: "callable", 
        disabled_func: Optional["callable"] = None
    ) -> Tuple[List[Item], List[int]]:
        items = []
        alphas = []
        for action in entity.actions:
            if action["name"] in ("Heal", "Global Heal"):
                items.append((action["name"], make_selector_func(action)))
                alphas.append(255)
            else:
                func = disabled_func if disabled_func is not None else make_selector_func(action)
                items.append((action["name"], func))
                alphas.append(100)
        return items, alphas




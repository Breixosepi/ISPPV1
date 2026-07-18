"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Character: a playable party member. Adds
IV-based stat growth and an experience/leveling curve on top of
BattleEntity.
"""

import random
from typing import Any, Dict, Tuple

from src.entity.BattleEntity import BattleEntity


class Character(BattleEntity):
    def __init__(self, definition: Dict[str, Any]) -> None:
        super().__init__(definition)

        self.hpiv: float = definition["HPIV"]
        self.attackiv: float = definition["attackIV"]
        self.defenseiv: float = definition["defenseIV"]
        self.magiciv: float = definition["magicIV"]

        self.current_exp: float = 0
        self.exp_to_level: float = 0
        self._next_exp_to_level()

    def calculate_stats(self) -> None:
        for _ in range(self.level):
            self.stats_level_up()

    def stats_level_up(self) -> Tuple[int, int, int, int]:
        hp_increase = 0
        for _ in range(3):
            if random.randint(1, 6) <= self.hpiv:
                self.hp += 1
                hp_increase += 1
        self.current_hp = self.hp

        attack_increase = 0
        for _ in range(3):
            if random.randint(1, 6) <= self.attackiv:
                self.attack += 1
                attack_increase += 1

        defense_increase = 0
        for _ in range(3):
            if random.randint(1, 6) <= self.defenseiv:
                self.defense += 1
                defense_increase += 1

        magic_increase = 0
        for _ in range(3):
            if random.randint(1, 6) <= self.magiciv:
                self.magic += 1
                magic_increase += 1

        return hp_increase, attack_increase, defense_increase, magic_increase

    def level_up(self) -> Tuple[int, int, int, int]:
        self.level += 1
        self._next_exp_to_level()
        return self.stats_level_up()

    def _next_exp_to_level(self) -> None:
        self.exp_to_level = self.level * self.level * 10 * 1.1

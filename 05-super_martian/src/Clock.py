"""
ISPPV1 2026
Study Case: Super Martian (Platformer)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the class Clock.
"""


class Clock:
    def __init__(self, time: int) -> None:
        self.time = time

    def count_down(self) -> None:
        self.time = max(0, self.time - 1)

    def __str__(self) -> str:
        return str(self.time)

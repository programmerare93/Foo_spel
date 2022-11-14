from __future__ import annotations

from typing import TYPE_CHECKING

import random

# Falskt på 'runtime'
if TYPE_CHECKING:
    from src.engine.engine import Engine
    from src.creature.entity import Entity


class Action:
    def perform(self, engine: Engine, entity: Entity) -> None:
        """Metod som kommer att utföra en handling för en entitet,
        måste implementeras för individuella subklasser"""

        # Kommer att misslyckas om man inte modifierat metoden
        raise NotImplementedError()


class MovementAction(Action):
    def __init__(self, dx: int, dy: int):
        self.dx = dx
        self.dy = dy

    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        if not engine.game_map.in_bounds(dest_x, dest_y):
            # Koordinaten är utanför kartan
            return

        if not engine.game_map.get_tile(dest_x, dest_y).walkable:
            return

        if engine.entity_at_location(dest_x, dest_y):
            return

        entity.move(self.dx, self.dy)


class AttackingAction(Action):
    def perform(self, engine, player) -> None:
        print("Attacking")
        pass

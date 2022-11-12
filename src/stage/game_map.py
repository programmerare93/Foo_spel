import numpy as np
from tcod.console import Console

import stage.tile_types as tile_types


class GameMap:
    """Klass för att representera spel kartan"""

    def __init__(self, width: int, height: int):
        self.width, self.height = width, height
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

        self.visible = np.full((width, height), fill_value=False, order="F")
        self.explored = np.full((width, height), fill_value=False, order="F")

    def in_bounds(self, x: int, y: int) -> bool:
        """Återvänder sant ifall koordinaten är inom kartan"""
        return 0 <= x < self.width and 0 <= y < self.height

    def is_blocked(self, x, y) -> bool:
        if (not self.get_tile(x + 1, y).transparent and
            not self.get_tile(x - 1, y).transparent and
            not self.get_tile(x, y + 1).transparent and
            not self.get_tile(x + 1, y + 1).transparent and
            not self.get_tile(x - 1, y + 1).transparent and
            not self.get_tile(x, y - 1).transparent and
            not self.get_tile(x + 1, y - 1).transparent and
            not self.get_tile(x - -1, y - 1).transparent):
            return True
        else:
            return False

    def render(self, console: Console) -> None:
        """Metod för att gå igenom alla tiles och sedan rendera varje tile"""
        # TODO: Kolla över metoden igen och se om det finns något bättre sätt, det funkar iallafall
        for (x, row) in enumerate(self.tiles):
            for (y, tile) in enumerate(row):
                if self.visible[x, y] and not self.is_blocked(x, y):
                    if self.get_tile(x, y).transparent:
                        tile.visible = True
                    if tile.type == tile_types.types_of_tiles["floor"]:
                        tile.color = tile_types.floor_color
                    elif tile.type == tile_types.types_of_tiles["wall"]:
                        tile.color = tile_types.wall_color
                    tile.render(console, x, y)
                elif self.explored[x, y] and not self.is_blocked(x, y):
                    tile.seen = True
                    tile.color = tile_types.seen_color
                    tile.render(console, x, y)

    def get_tile(self, x, y):
        return self.tiles[x, y]

import numpy as np  # type: ignore
from tcod.console import Console

import tile_types


class GameMap:
    def __init__(self, width: int, height: int):
        self.width, self.height = width, height
        self.tiles = np.full((width, height), fill_value=tile_types.WALL, order='F')

        # tiles that are currently visible
        self.visible = np.full((width, height), fill_value=False, order='F')
        # tiles that were visible but are not currently visible
        self.explored = np.full((width, height), fill_value=False, order='F')

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside the bounds of this map"""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """
        Renders the map

        If a tile is visible, draw w/ light colors
        If it isn't but is explored, draw w/ dark colors
        Otherwise, draw as SHROUD
        """
        console.tiles_rgb[0:self.width, 0:self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles['light'], self.tiles['dark']],
            default=tile_types.SHROUD
        )

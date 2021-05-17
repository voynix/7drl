from __future__ import annotations

from typing import Iterable, Iterator, Optional, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
from tcod.console import Console

from entity import Actor, Item
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

# TODO: put this in setup_game and thread it through
# how close the player can get to the edge of the screen before the viewport anchor moves
VIEWPORT_MARGIN = (10, 10)


class GameMap:
    def __init__(
        self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.width, self.height = width, height
        # the top-left point of the viewport in map-space
        # adjust_viewport_anchor() will fix this up before first run
        self.viewport_anchor_x, self.viewport_anchor_y = 0, 0
        self.viewport_margin_x, self.viewport_margin_y = VIEWPORT_MARGIN
        self.entities = set(entities)
        self.tiles = np.full((width, height), fill_value=tile_types.WALL, order="F")

        # tiles that are currently visible
        self.visible = np.full((width, height), fill_value=False, order="F")
        # tiles that were visible but are not currently visible
        self.explored = np.full((width, height), fill_value=False, order="F")

        self.downstairs_location = (0, 0)

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_blocking_entity_at_location(
        self, location_x: int, location_y: int
    ) -> Optional[Entity]:
        for entity in self.entities:
            if (
                entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ):
                return entity

        return None

    def get_actor_at_location(
        self, location_x: int, location_y: int
    ) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == location_x and actor.y == location_y:
                return actor

        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside the bounds of this map"""
        return 0 <= x < self.width and 0 <= y < self.height

    def map_to_viewport_coord(self, map_c: Tuple[int, int]) -> Tuple[int, int]:
        map_x, map_y = map_c
        vp_x = map_x - self.viewport_anchor_x
        vp_y = map_y - self.viewport_anchor_y

        return vp_x, vp_y

    def viewport_to_map_coord(self, vp: Tuple[int, int]) -> Tuple[int, int]:
        vp_x, vp_y = vp
        map_x = vp_x + self.viewport_anchor_x
        map_y = vp_y + self.viewport_anchor_y

        return map_x, map_y

    def adjust_viewport_anchor(
        self, player_x: int, player_y: int, viewport_width: int, viewport_height: int
    ) -> None:
        """Move the viewport_anchor if the player is too close to the edge of the viewport"""
        player_vp_x = player_x - self.viewport_anchor_x
        if player_vp_x < self.viewport_margin_x:
            self.viewport_anchor_x = player_x - self.viewport_margin_x
        elif viewport_width - player_vp_x < self.viewport_margin_x:
            self.viewport_anchor_x = player_x + self.viewport_margin_x - viewport_width

        player_vp_y = player_y - self.viewport_anchor_y
        if player_vp_y < self.viewport_margin_y:
            self.viewport_anchor_y = player_y - self.viewport_margin_y
        elif viewport_height - player_vp_y < self.viewport_margin_y:
            self.viewport_anchor_y = player_y + self.viewport_margin_y - viewport_height

    def render(
        self, console: Console, viewport_width: int, viewport_height: int
    ) -> None:
        """
        Renders the map

        If a tile is visible, draw w/ light colors
        If it isn't but is explored, draw w/ dark colors
        Otherwise, draw as SHROUD
        """
        self.adjust_viewport_anchor(
            self.engine.player.x, self.engine.player.y, viewport_width, viewport_height
        )

        # bounds of the viewport in map-space, clamped to the map bounds
        x_start = max(self.viewport_anchor_x, 0)
        x_end = min(self.viewport_anchor_x + viewport_width, self.width)
        y_start = max(self.viewport_anchor_y, 0)
        y_end = min(self.viewport_anchor_y + viewport_height, self.height)

        # init a new viewport buffer on the assumption that everything's off the map
        new_tiles = np.full(
            (viewport_width, viewport_height), fill_value=tile_types.EXTERNAL, order="F"
        )

        # blit the map rectangle onto the new viewport buffer
        new_tiles[
            x_start - self.viewport_anchor_x : x_end - self.viewport_anchor_x,
            y_start - self.viewport_anchor_y : y_end - self.viewport_anchor_y,
        ] = np.select(
            condlist=[
                self.visible[x_start:x_end, y_start:y_end],
                self.explored[x_start:x_end, y_start:y_end],
            ],
            choicelist=[
                self.tiles[x_start:x_end, y_start:y_end]["light"],
                self.tiles[x_start:x_end, y_start:y_end]["dark"],
            ],
            default=tile_types.SHROUD,
        )

        console.tiles_rgb[0:viewport_width, 0:viewport_height] = new_tiles

        sorted_entities = sorted(self.entities, key=lambda x: x.render_order.value)

        for entity in sorted_entities:
            # only draw visible entities in the viewport
            if (
                self.visible[entity.x, entity.y]
                and x_start <= entity.x < x_end
                and y_start <= entity.y < y_end
            ):
                console.print(
                    entity.x - self.viewport_anchor_x,
                    entity.y - self.viewport_anchor_y,
                    entity.char,
                    fg=entity.color,
                )

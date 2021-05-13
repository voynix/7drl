from __future__ import annotations

from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np  # type: ignore
from tcod.console import Console

from entity import Actor, Item
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class GameMap:
    def __init__(
        self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.width, self.height = width, height
        # the top-left point of the viewport in map-space
        self.viewport_anchor_x, self.viewport_anchor_y = 0, 0
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

    def render(
        self, console: Console, viewport_width: int, viewport_height: int
    ) -> None:
        """
        Renders the map

        If a tile is visible, draw w/ light colors
        If it isn't but is explored, draw w/ dark colors
        Otherwise, draw as SHROUD
        """
        x_start = self.viewport_anchor_x
        x_end = x_start + viewport_width
        y_start = self.viewport_anchor_y
        y_end = y_start + viewport_height

        assert 0 <= x_start < len(self.visible)
        assert 0 <= y_start < len(self.visible[0])
        assert 0 < x_end <= len(self.visible)
        assert 0 < y_end <= len(self.visible[0])

        console.tiles_rgb[0:viewport_width, 0:viewport_height] = np.select(
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

        sorted_entities = sorted(self.entities, key=lambda x: x.render_order.value)

        for entity in sorted_entities:
            # only draw visible entities in the viewport
            if (
                self.visible[entity.x, entity.y]
                and x_start <= entity.x < x_end
                and y_start <= entity.y < y_end
            ):
                console.print(
                    entity.x - x_start, entity.y - y_start, entity.char, fg=entity.color
                )

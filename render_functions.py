from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

import color

if TYPE_CHECKING:
    from tcod import Console
    from engine import Engine
    from entity import Entity
    from game_map import GameMap


def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""

    names = ", ".join(
        entity.name for entity in game_map.entities if entity.x == x and entity.y == y
    )

    return names.capitalize()


def render_bar(
    console: Console, current_value: int, maximum_value: int, total_width: int
) -> None:
    bar_width = int(total_width * float(current_value) / maximum_value)

    console.draw_rect(x=0, y=45, width=total_width, height=1, ch=1, bg=color.BAR_EMPTY)

    if bar_width > 0:
        console.draw_rect(
            x=0, y=45, width=bar_width, height=1, ch=1, bg=color.BAR_FILLED
        )

    console.print(
        x=1, y=45, string=f"HP: {current_value}/{maximum_value}", fg=color.BAR_TEXT
    )


def render_dungeon_level(
    console: Console, dungeon_level: int, location: Tuple[int, int]
) -> None:
    x, y = location

    console.print(x=x, y=y, string=f"Dungeon level: {dungeon_level}")


def render_graphics_debug(
    console: Console, player: Entity, game_map: GameMap, location: Tuple[int, int]
) -> None:
    x, y = location

    console.print(x=x, y=y, string=f"Player @: {player.x}, {player.y}")
    console.print(
        x=x,
        y=y + 1,
        string=f"VP anchor: {game_map.viewport_anchor_x}, {game_map.viewport_anchor_y}",
    )


def render_names_at_mouse_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    map_x, map_y = engine.game_map.viewport_to_map_coord(engine.mouse_location)

    names_at_mouse_location = get_names_at_location(
        x=map_x, y=map_y, game_map=engine.game_map
    )

    console.print(x=x, y=y, string=names_at_mouse_location)

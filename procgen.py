from __future__ import annotations

import random
from typing import Dict, Iterator, List, Tuple, TYPE_CHECKING

import tcod

import entity_factories
from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


# these tables include only the change points
#  each unlisted floor has the value of most recently listed floor above
# (floor, max)
MAX_ITEMS_BY_FLOOR = [(1, 1), (4, 2)]

# (floor, max)
MAX_MONSTERS_BY_FLOOR = [(1, 2), (4, 3), (6, 5)]

# these tables are cumulative;
#  each floor has the combined weights of all the floors above
# floor: [(item, weight), …]
ITEM_CHANCES_BY_FLOOR: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.HEALTH_POTION, 35)],
    2: [(entity_factories.CONFUSION_SCROLL, 10)],
    4: [(entity_factories.LIGHTNING_SCROLL, 25), (entity_factories.SWORD, 5)],
    6: [(entity_factories.FIREBALL_SCROLL, 25), (entity_factories.CHAIN_MAIL, 15)],
}

# floor: [(enemy, weight), …]
ENEMY_CHANCES_BY_FLOOR: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.ORC, 80)],
    2: [(entity_factories.TROLL, 15)],
    4: [(entity_factories.TROLL, 30)],
    6: [(entity_factories.TROLL, 60)],
}


def get_max_value_for_floor(
    weighted_chance_by_floor: List[Tuple[int, int]], floor: int
) -> int:
    current = 0

    for floor_minimum, value in weighted_chance_by_floor:
        if floor_minimum > floor:
            break
        current = value

    return current


def get_entities_at_random(
    weighted_chance_by_floor: Dict[int, List[Tuple[Entity, int]]],
    number_of_entities: int,
    floor: int,
) -> List[Entity]:
    weighted_entity_chances = {}

    for k, v in weighted_chance_by_floor.items():
        if k > floor:
            break
        for entity, weight in v:
            weighted_entity_chances[entity] = weight

    chosen_entities = random.choices(
        list(weighted_entity_chances.keys()),
        weights=list(weighted_entity_chances.values()),
        k=number_of_entities,
    )

    return chosen_entities


class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2

        return center_x, center_y

    @property
    def inner(self) -> Tuple[int, int]:
        """Return the inner area of this room as a 2D array index"""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


def place_entities(room: RectangularRoom, dungeon: GameMap, floor_number: int) -> None:
    number_of_monsters = random.randint(
        0, get_max_value_for_floor(MAX_MONSTERS_BY_FLOOR, floor_number)
    )
    number_of_items = random.randint(
        0, get_max_value_for_floor(MAX_ITEMS_BY_FLOOR, floor_number)
    )

    monsters: List[Entity] = get_entities_at_random(
        ENEMY_CHANCES_BY_FLOOR, number_of_monsters, floor_number
    )

    items: List[Entity] = get_entities_at_random(
        ITEM_CHANCES_BY_FLOOR, number_of_items, floor_number
    )

    for entity in monsters + items:
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            entity.spawn(dungeon, x, y)


def tunnel_between(
    start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between two points"""
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5:
        # move horizontally, then vertically
        corner_x, corner_y = x2, y1
    else:
        # move vertically, then horizontally
        corner_x, corner_y = x1, y2

    # generate the coordinates for the tunnel
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)):
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)):
        yield x, y


def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    engine: Engine,
) -> GameMap:
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[RectangularRoom] = []

    center_of_last_room = (0, 0)

    for r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        new_room = RectangularRoom(x, y, room_width, room_height)

        if any(new_room.intersects(other_room) for other_room in rooms):
            continue  # this room intersects an existing room; try again

        # this room is valid, so dig it out
        dungeon.tiles[new_room.inner] = tile_types.FLOOR

        if len(rooms) == 0:
            player.place(*new_room.center, dungeon)
        else:
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.FLOOR

            center_of_last_room = new_room.center

        place_entities(new_room, dungeon, engine.game_world.current_floor)

        rooms.append(new_room)

    dungeon.tiles[center_of_last_room] = tile_types.STAIRS_DOWN
    dungeon.downstairs_location = center_of_last_room

    return dungeon

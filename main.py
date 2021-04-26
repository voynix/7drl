import copy
import traceback

import tcod

import color
from engine import Engine
import entity_factories
from procgen import generate_dungeon


TITLE = 'KOBOLD-LIKE'
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 80
MAP_HEIGHT = 43

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
MAX_MONSTERS_PER_ROOM = 2
MAX_ITEMS_PER_ROOM = 2


def main() -> None:
    tileset = tcod.tileset.load_tilesheet(
        'dejavu10x10_gs_tc.png', 32, 8, 
        tcod.tileset.CHARMAP_TCOD
    )

    # can't use spawn() b/c the game_map doesn't exist yet
    player = copy.deepcopy(entity_factories.PLAYER)

    engine = Engine(player=player)

    engine.game_map = generate_dungeon(
        max_rooms=MAX_ROOMS,
        room_min_size=ROOM_MIN_SIZE,
        room_max_size=ROOM_MAX_SIZE,
        map_width=MAP_WIDTH,
        map_height=MAP_HEIGHT,
        max_monsters_per_room=MAX_MONSTERS_PER_ROOM,
        max_items_per_room=MAX_ITEMS_PER_ROOM,
        engine=engine
    )

    engine.update_fov()

    engine.message_log.add_message('Welcome, kobold adverturer!', color.WELCOME_TEXT)

    with tcod.context.new_terminal(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        tileset=tileset,
        title=TITLE,
        vsync=True
    ) as context:
        root_console = tcod.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order="F")
        while True:
            root_console.clear()
            engine.event_handler.on_render(console=root_console)
            context.present(root_console)

            try:
                for event in tcod.event.wait():
                    context.convert_event(event)
                    engine.event_handler.handle_events(event)
            except Exception:
                traceback.print_exc()  # print stacktrace to stderr
                engine.message_log.add_message(traceback.format_exc(), color.ERROR)


if __name__ == '__main__':
    main()

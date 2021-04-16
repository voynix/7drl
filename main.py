import tcod

from engine import Engine
from entity import Entity
from game_map import GameMap
from input_handlers import EventHandler


TITLE = 'KOBOLD-LIKE'
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 80
MAP_HEIGHT = 45


def main() -> None:
    tileset = tcod.tileset.load_tilesheet(
        'dejavu10x10_gs_tc.png', 32, 8, 
        tcod.tileset.CHARMAP_TCOD
    )

    event_handler = EventHandler()

    player = Entity(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, '@', (255, 255, 255))
    npc = Entity(SCREEN_WIDTH // 2 - 5, SCREEN_HEIGHT // 2, '@', (255, 255, 0))
    entities = {npc, player}

    game_map = GameMap(MAP_WIDTH, MAP_HEIGHT)

    engine = Engine(entities=entities, event_handler=event_handler, game_map=game_map, player=player)

    with tcod.context.new_terminal(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        tileset=tileset,
        title=TITLE,
        vsync=True
    ) as context:
        root_console = tcod.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order="F")
        while True:
            engine.render(console=root_console, context=context)

            events = tcod.event.wait()

            engine.handle_events(events)


if __name__ == '__main__':
    main()

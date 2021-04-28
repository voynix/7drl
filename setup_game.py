from __future__ import annotations

import copy
import lzma
import pickle
import traceback
from typing import Optional

import tcod

import color
from engine import Engine
import entity_factories
import input_handlers
from procgen import generate_dungeon


# load the bg and remove the alpha channel
BACKGROUND_IMAGE = tcod.image.load('menu_background.png')[:, :, :3]

MAP_WIDTH = 80
MAP_HEIGHT = 43

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
MAX_MONSTERS_PER_ROOM = 2
MAX_ITEMS_PER_ROOM = 2

TITLE = 'KOBOLD-LIKE'
SAVE_FILE = 'savegame.sav'


def new_game() -> Engine:
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

    return engine


def load_game(filename: str) -> Engine:
    with open(filename, 'rb') as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine


class MainMenu(input_handlers.BaseEventHandler):
    def on_render(self, console: tcod.Console) -> None:
        # this doesn't seem to work for some reason…
        # OpenGL on Mac issues, possibly…
        console.draw_semigraphics(BACKGROUND_IMAGE, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            TITLE,
            fg=color.MENU_TITLE,
            alignment=tcod.CENTER
        )
        console.print(
            console.width // 2,
            console.height // 2 - 4,
            'By Pangolin Games',
            fg=color.MENU_TITLE,
            alignment=tcod.CENTER
        )

        menu_width = 24
        for i, text in enumerate(
            ['[N] Play a new game', '[C] Continue last game', '[Q] Quit']
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=color.MENU_TEXT,
                bg=color.BLACK,
                alignment=tcod.CENTER,
                bg_blend=tcod.BKGND_ALPHA(64)
            )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in {tcod.event.K_q, tcod.event.K_ESCAPE}:
            raise SystemExit()
        elif event.sym == tcod.event.K_c:
            try:
                return input_handlers.MainGameEventHandler(load_game(SAVE_FILE))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, 'No saved game to load')
            except Exception as e:
                traceback.print_exc()
                return input_handlers.PopupMessage(self, f'Failed to load save:\n{e}')
        elif event.sym == tcod.event.K_n:
            return input_handlers.MainGameEventHandler(new_game())

        return None
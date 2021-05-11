import traceback

import tcod

import color
import exceptions
import input_handlers
import setup_game


SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50


def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game saved")


def main() -> None:
    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    handler: input_handlers.BaseEventHandler = setup_game.MainMenu()

    with tcod.context.new(
        columns=SCREEN_WIDTH,
        rows=SCREEN_HEIGHT,
        tileset=tileset,
        title=setup_game.TITLE,
        vsync=True,
    ) as context:
        root_console = tcod.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order="F")
        try:
            while True:
                root_console.clear()
                handler.on_render(console=root_console)
                context.present(root_console)

                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:
                    traceback.print_exc()  # print stacktrace to stderr
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.ERROR
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:  # save and quit
            save_game(handler, setup_game.SAVE_FILE)
        except BaseException:  # save on unexpected exceptions
            save_game(handler, setup_game.SAVE_FILE)


if __name__ == "__main__":
    main()

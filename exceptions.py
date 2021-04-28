class Impossible(Exception):
    """
    Exception raised when an action is impossible to perform

    The exception's message should be set to the reason the action is impossible
    """
    pass


class QuitWithoutSaving(SystemExit):
    """Raised to exit the game without autosaving"""
    pass

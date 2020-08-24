import inspect


def get_logger_name():
    return (
        f"{inspect.getmodulename(inspect.stack()[1].filename)}"
        f".{inspect.stack()[1].function}"
    )


def on_production(_):
    return os.getenv("PRODUCTION") is not None

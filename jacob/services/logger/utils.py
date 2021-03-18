import os


def on_production(_):
    return os.getenv("PRODUCTION") is not None

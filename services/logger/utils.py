import os


def on_production():
    return os.getenv("PRODUCTION") is not None

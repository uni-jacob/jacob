import os
from logging import LogRecord


def on_production(_: LogRecord) -> bool:
    return os.getenv("PRODUCTION") is not None

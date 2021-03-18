import os
import sys

from jacob.services.logger.handlers import TelegramHandler
from jacob.services.logger.utils import on_production

fmt = "{time:YYYY-MM-DD@HH:mm:ss zz} | {module}.{function} | {level} | {message}"
tg_conf = {"token": os.getenv("TG_TOKEN"), "chat": os.getenv("TG_CHAT")}

config = {
    "handlers": [
        {
            "sink": TelegramHandler(defaults=tg_conf),
            "format": fmt,
            "level": "ERROR",
            "filter": on_production,
        },
        {
            "sink": sys.stdout,
            "format": fmt,
        },
    ],
}

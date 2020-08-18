import os

from notifiers.logging import NotificationHandler

fmt = "YY-MM-D@HH:mm:sszz | {module}.{function} | {level} | {message}"
tg_conf = {"chat_id": os.getenv("TG_CHAT"), "token": os.getenv("TG_TOKEN")}

config = {
    "handlers": [
        {
            "sink": NotificationHandler("telegram", defaults=tg_conf),
            "format": fmt,
            "enqueue": True,
            "level": "ERROR",
        },
        {
            "sink": "jacob_{time}.log",
            "format": fmt,
            "rotation": "00:00",
            "enqueue": True,
        },
    ]
}

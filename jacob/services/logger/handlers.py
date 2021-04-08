import copy
import logging
import os
from types import FrameType
from typing import Optional

import requests
from loguru import logger
from requests import Response


class TelegramHandler(logging.Handler):
    def __init__(self, defaults: dict = None, **kwargs):

        self.defaults: dict = defaults or {}
        super().__init__(**kwargs)

    def emit(self, record):
        data: dict = copy.deepcopy(self.defaults)
        data["message"], data["tbs"] = self.format(record)
        query: Response = requests.post(
            "https://dpaste.com/api/v2/",
            data={"content": data["tbs"], "syntax": {"pytb": "Python Traceback"}},
        )
        link: str = query.text.strip("\n")
        message: str = f"`{data['message']}`\n{link}"
        requests.post(
            f"https://api.telegram.org/bot"
            f"{data['token']}/sendMessage?chat_id={os.getenv('TG_CHATS')}&text"
            f"={message}&parse_mode=Markdown",
        )

    def format(self, record: logging.LogRecord):
        record.message = record.getMessage()
        msg = [msg.strip() for msg in record.message.split("\n") if msg]
        return "\n".join(msg[-2:]), "\n".join(msg[1:])


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame: Optional[FrameType] = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )

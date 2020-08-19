import copy
import logging
import os

import requests


class TelegramHandler(logging.Handler):
    def __init__(self, defaults: dict = None, **kwargs):

        self.defaults = defaults or {}
        super().__init__(**kwargs)

    def emit(self, record):
        data = copy.deepcopy(self.defaults)
        data["message"], data["tbs"] = self.format(record)
        query = requests.post(
            "https://dpaste.com/api/v2/",
            data={"content": data["tbs"], "syntax": {"pytb": "Python Traceback"}},
        )
        link = query.text.strip("\n")
        message = f"`{data['message']}`\n{link}"
        requests.post(
            f"https://api.telegram.org/bot"
            f"{data['token']}/sendMessage?chat_id={os.getenv('TG_CHATS')}&text"
            f"={message}&parse_mode=Markdown"
        )

    def format(self, record):
        record.message = record.getMessage()
        msg = record.message.split("\n")
        return msg[0], "\n".join(msg[1:])

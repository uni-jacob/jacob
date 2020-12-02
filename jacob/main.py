"""Подключает все роутеры и запускает бота."""

import logging
import os

from vkwave import bots

import blueprints
from services.logger.handlers import InterceptHandler

logging.basicConfig(level=logging.DEBUG, handlers=[InterceptHandler()])

bot = bots.SimpleLongPollBot(
    tokens=os.getenv("VK_TOKEN"),
    group_id=os.getenv("GROUP_ID"),
)
bot.dispatcher.add_router(blueprints.main.main.main_router)
bot.dispatcher.add_router(blueprints.call.call_router)
bot.dispatcher.add_router(blueprints.preferences.preferences_router)
bot.dispatcher.add_router(blueprints.chats.chats_router)
bot.dispatcher.add_router(blueprints.finances.finances_router)
bot.dispatcher.add_router(blueprints.schedule.schedule_router)
bot.dispatcher.add_router(blueprints.web.web_router)
bot.dispatcher.add_router(blueprints.report.report_router)
bot.dispatcher.add_router(blueprints.contacts.contacts_router)


bot.run_forever()

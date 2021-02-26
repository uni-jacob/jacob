"""Подключает все роутеры и запускает бота."""

import logging
import os

from vkwave import bots

from jacob.blueprints.main import main
from jacob.blueprints.mention import menu as call_menu
from jacob.blueprints.mention import start as call_start
from jacob.blueprints import chats, preferences, finances, report, contacts
from jacob.services.logger.handlers import InterceptHandler

logging.basicConfig(level=logging.DEBUG, handlers=[InterceptHandler()])

bot = bots.SimpleLongPollBot(
    tokens=os.getenv("VK_TOKEN"),
    group_id=os.getenv("GROUP_ID"),
)
bot.dispatcher.add_router(main.main_router)
bot.dispatcher.add_router(call_menu.call_menu_router)
bot.dispatcher.add_router(call_start.call_start_router)
bot.dispatcher.add_router(preferences.preferences_router)
bot.dispatcher.add_router(chats.chats_router)
bot.dispatcher.add_router(finances.finances_router)
bot.dispatcher.add_router(report.report_router)
bot.dispatcher.add_router(contacts.contacts_router)


bot.run_forever()

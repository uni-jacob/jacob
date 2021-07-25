import os

from vkbottle import Bot, load_blueprints_from_package

bot = Bot(os.getenv("VK_TOKEN"))
for bp in load_blueprints_from_package("blueprints"):
    bp.load(bot)

bot.run_forever()

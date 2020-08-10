import logging
import os

from vkwave.bots import SimpleBotEvent
from vkwave.bots import SimpleLongPollBot
from vkwave.bots import TextFilter

from services import keyboard as kbs
from database import utils as db
from services import filters

logging.basicConfig(level=logging.DEBUG)
bot = SimpleLongPollBot(tokens=os.getenv("VK_TOKEN"), group_id=os.getenv("GROUP_ID"))


@bot.message_handler(TextFilter(["старт", "начать", "start", "привет", "hi", "hello"]))
async def start(ans: SimpleBotEvent):
    await ans.answer(
        "Привет!", keyboard=kbs.main_menu(ans.object.object.message.peer_id)
    )


@bot.message_handler(filters.ButtonFilter("call"))
async def start_call(ans: SimpleBotEvent):
    db.update_admin_storage(
        db.get_system_id_of_student(ans.object.object.message.peer_id),
        state_id=db.get_id_of_state("wait_call_text"),
    )
    await ans.answer("Отправьте текст призыва", keyboard=kbs.skip_call_message())


@bot.message_handler(
    filters.StateFilter("wait_call_text") & filters.ButtonFilter("skip_call_message")
)
async def skip_register_call_message(ans: SimpleBotEvent):
    db.clear_admin_storage(
        db.get_system_id_of_student(ans.object.object.message.peer_id)
    )
    await ans.answer(
        "Сохранение сообщения призыва пропущено. Выберите призываемых студентов",
        keyboard=kbs.call_interface(ans.object.object.message.peer_id),
    )


@bot.message_handler(filters.StateFilter("wait_call_text"))
async def register_call_message(ans: SimpleBotEvent):
    db.update_admin_storage(
        db.get_system_id_of_student(ans.object.object.message.peer_id),
        state_id=db.get_id_of_state("main"),
        text=ans.object.object.message.text,
    )
    await ans.answer(
        "Сообщение сохранено. Выберите призываемых студентов",
        keyboard=kbs.call_interface(ans.object.object.message.peer_id),
    )


bot.run_forever()

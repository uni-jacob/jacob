"""Модуль приглашений."""

from loguru import logger
from pony import orm
from vkwave import bots

from jacob.database import models, redis
from jacob.database.utils import admin, students
from jacob.services import keyboard as kbs
from jacob.services.filters import PLFilter
from jacob.services.logger.config import config

invite_router = bots.DefaultRouter()
logger.configure(**config)


@bots.simple_bot_message_handler(
    invite_router,
    PLFilter({"button": "invite_user"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _invite_user(ans: bots.SimpleBotEvent):
    user_id = ans.payload.get("user")
    user = await ans.api_ctx.users.get(user_ids=user_id)
    admin_id = students.get_system_id_of_student(ans.from_id)
    group_id = await redis.hget(
        str(user_id),
        "requested_group",
    )
    with orm.db_session:
        student = models.Student(
            vk_id=user_id,
            first_name=user.response[0].first_name,
            last_name=user.response[0].last_name,
            group=group_id,
            academic_status=1,
        )
    await redis.delete(str(user_id))
    await ans.answer(
        "Пользователь @id{0} добавлен в вашу группу".format(user_id),
        keyboard=kbs.main.main_menu(admin_id),
    )
    await ans.api_ctx.messages.send(
        message="Администратор пригласил вас в группу",
        peer_id=user_id,
        random_id=0,
        keyboard=kbs.main.main_menu(student.id),
    )
    with orm.db_session:
        admins = admin.get_admins_of_group(group_id)
        for adm in admins:
            if adm.vk_id != ans.from_id:
                await ans.api_ctx.messages.send(
                    message="Другой администратор пригласил пользователя",
                    peer_id=adm.vk_id,
                    random_id=0,
                    keyboard=kbs.main.main_menu(adm.student.id),
                )


@bots.simple_bot_message_handler(
    invite_router,
    PLFilter({"button": "decline_user"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _decline_user(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    user_id = ans.payload.get("user")
    group_id = await redis.hget(
        str(user_id),
        "requested_group",
    )
    await redis.delete(str(user_id))
    await ans.answer(
        "Вы отклонили запрос на добавление студента",
        keyboard=kbs.main.main_menu(admin_id),
    )
    await ans.api_ctx.messages.send(
        message="Администратор отклонил ваш запрос на добавление в группу",
        peer_id=user_id,
        random_id=0,
    )
    with orm.db_session:
        admins = admin.get_admins_of_group(group_id)
        for adm in admins:
            if adm.vk_id != ans.from_id:
                await ans.api_ctx.messages.send(
                    message="Другой администратор отклонил запрос пользователя",
                    peer_id=adm.vk_id,
                    random_id=0,
                    keyboard=kbs.main.main_menu(adm.student.id),
                )

"""Главное меню бота."""

from loguru import logger
from pony import orm
from vkwave import bots

from jacob.database import models, redis
from jacob.database.utils import admin, students
from jacob.database.utils.storages import managers
from jacob.services import keyboard as kbs
from jacob.services.exceptions import StudentNotFound
from jacob.services.filters import PLFilter, RedisStateFilter
from jacob.services.logger.config import config

main_router = bots.DefaultRouter()
logger.configure(**config)


@bots.simple_bot_message_handler(
    main_router,
    bots.TextFilter(["старт", "начать", "start", "привет", "hi", "hello"])
    | PLFilter({"button": "main_menu"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _greeting(ans: bots.SimpleBotEvent):
    try:
        student_id = students.get_system_id_of_student(
            ans.from_id,
        )
    except StudentNotFound:
        await ans.answer(
            "Вы не являетесь зарегистрированным студентом.\n"
            + "Желаете попасть в существующую группу или создать свою?",
            keyboard=kbs.main.choose_register_way(),
        )
    else:
        state_store = managers.StateStorageManager(student_id)
        state_store.update(state=state_store.get_id_of_state("main"))
        await ans.answer(
            "Привет!",
            keyboard=kbs.main.main_menu(
                student_id,
            ),
        )


@bots.simple_bot_message_handler(
    main_router,
    PLFilter({"button": "create_new_group"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _show_universities(ans: bots.SimpleBotEvent):
    await redis.hmset(
        str(ans.from_id),
        state="create_group_select_university",
    )
    await ans.answer(
        "Выбери университет",
        keyboard=kbs.main.universities_with_create(),
    )


@bots.simple_bot_message_handler(
    main_router,
    PLFilter({"button": "choose_existing_group"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _show_universities_choose(ans: bots.SimpleBotEvent):
    await redis.hmset(
        str(ans.from_id),
        state="select_group_select_university",
    )
    await ans.answer(
        "Выбери университет",
        keyboard=kbs.main.universities_without_create(),
    )


@bots.simple_bot_message_handler(
    main_router,
    PLFilter({"button": "university"}),
    RedisStateFilter("select_group_select_university"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _select_group(ans: bots.SimpleBotEvent):
    await redis.hmset(
        str(ans.from_id),
        state="select_group_select_group",
    )
    await ans.answer(
        "Выберите группу",
        keyboard=kbs.main.public_groups(ans.payload.get("university")),
    )


@bots.simple_bot_message_handler(
    main_router,
    PLFilter({"button": "group"}),
    RedisStateFilter("select_group_select_group"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _send_add_request(ans: bots.SimpleBotEvent):

    group_id = ans.payload.get("group")
    await redis.hmset(str(ans.from_id), requested_group=group_id)

    with orm.db_session:
        admins = admin.get_admins_of_group(group_id)
        group = models.Group[group_id]

        await ans.api_ctx.messages.send(
            message="Пользователь @id{0} хочет присоединиться к вашей группе {1}".format(
                ans.from_id,
                group.group_num,
            ),
            peer_ids=[adm.vk_id for adm in admins],
            random_id=0,
            keyboard=kbs.invite.add_request_confirm(ans.from_id),
        )

    await ans.answer(
        "Запрос на добавление отправлен",
        keyboard=kbs.common.empty(),
    )


@bots.simple_bot_message_handler(
    main_router,
    PLFilter({"button": "create_university"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _create_university(ans: bots.SimpleBotEvent):
    await redis.hmset(
        str(ans.from_id),
        state="create_group_enter_university_name",
    )
    await ans.answer(
        "Введите название университета",
        keyboard=kbs.common.cancel().get_keyboard(),
    )


@bots.simple_bot_message_handler(
    main_router,
    PLFilter({"button": "university"}),
    RedisStateFilter("create_group_select_university"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _enter_group_number(ans: bots.SimpleBotEvent):
    await redis.hmset(
        str(ans.from_id),
        state="create_group_enter_number",
        university=ans.payload.get("university"),
    )
    await ans.answer(
        "Введите номер группы",
        keyboard=kbs.common.cancel().get_keyboard(),
    )


@bots.simple_bot_message_handler(
    main_router,
    PLFilter({"button": "cancel"}),
    RedisStateFilter("create_group_*"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _cancel_create_group(ans: bots.SimpleBotEvent):
    await redis.hmset(
        str(ans.from_id),
        state="main",
    )
    await ans.answer("Создание группы отменено")
    await _greeting(ans)


@bots.simple_bot_message_handler(
    main_router,
    PLFilter({"button": "cancel"}),
    RedisStateFilter("select_group_*"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _cancel_join_group(ans: bots.SimpleBotEvent):
    await redis.hmset(
        str(ans.from_id),
        state="main",
    )
    await ans.answer("Присоединение к группе отменено")
    await _greeting(ans)


@bots.simple_bot_message_handler(
    main_router,
    RedisStateFilter("create_group_enter_university_name"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _save_university(ans: bots.SimpleBotEvent):
    with orm.db_session:
        uni = models.AlmaMater(name=ans.text)
    await redis.hmset(
        str(ans.from_id),
        state="create_group_enter_number",
        university=uni.id,
    )
    await ans.answer(
        "Университет создан. Введите номер группы",
        keyboard=kbs.common.cancel().get_keyboard(),
    )


@bots.simple_bot_message_handler(
    main_router,
    RedisStateFilter("create_group_enter_number"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _enter_group_specialty(ans: bots.SimpleBotEvent):
    await redis.hmset(
        str(ans.from_id),
        state="create_group_enter_specialty",
        group_number=ans.text,
    )
    await ans.answer("Введите название специальности")


@bots.simple_bot_message_handler(
    main_router,
    RedisStateFilter("create_group_enter_specialty"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _select_publicity(ans: bots.SimpleBotEvent):
    await redis.hmset(
        str(ans.from_id),
        state="create_group_select_privacy",
        specialty=ans.text,
    )
    await ans.answer(
        "Выберите публичность/приватность группы",
        keyboard=kbs.main.group_privacy(),
    )


@bots.simple_bot_message_handler(
    main_router,
    PLFilter({"button": "group_privacy"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _save_group(ans: bots.SimpleBotEvent):
    group_number = await redis.hget(
        str(ans.from_id),
        "group_number",
    )
    specialty = await redis.hget(
        str(ans.from_id),
        "specialty",
    )
    university = await redis.hget(
        str(ans.from_id),
        "university",
    )
    privacy = ans.payload.get("value")

    user = await ans.api_ctx.users.get(user_ids=ans.from_id)

    with orm.db_session:
        group = models.Group(
            group_num=group_number,
            specialty=specialty,
            alma_mater=university,
            private=privacy,
        )

    with orm.db_session:
        student = models.Student(
            vk_id=ans.from_id,
            first_name=user.response[0].first_name,
            last_name=user.response[0].last_name,
            group=group.id,
            email="",
            phone_number="",
            academic_status=1,
        )
    with orm.db_session:
        models.Admin(student=student.id, group=group.id)

    await redis.hmset(
        str(ans.from_id),
        state="main",
    )

    await ans.answer("Группа сохранена")
    await _greeting(ans)

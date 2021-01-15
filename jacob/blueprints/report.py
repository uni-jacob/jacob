import os

from github import Github
from loguru import logger
from vkwave.api import API
from vkwave.bots import DefaultRouter
from vkwave.bots import MessageFromConversationTypeFilter
from vkwave.bots import SimpleBotEvent
from vkwave.bots import simple_bot_message_handler
from vkwave.client import AIOHTTPClient

from jacob.database import utils as db
from jacob.services import filters
from jacob.services import keyboard as kbs
from jacob.services.logger.config import config

report_router = DefaultRouter()
api_session = API(tokens=os.getenv("VK_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()
logger.configure(**config)


@simple_bot_message_handler(
    report_router,
    filters.PLFilter({"button": "report_error"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def start_reporting(ans: SimpleBotEvent):
    db.shortcuts.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
        state_id=db.bot.get_id_of_state("wait_issue_title"),
    )
    await ans.answer(
        "Отправьте заголовок проблемы, кратко описывающий произошедшее",
        keyboard=kbs.common.empty(),
    )


@simple_bot_message_handler(
    report_router,
    filters.StateFilter("wait_issue_title"),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def ask_for_issue_text(ans: SimpleBotEvent):
    issue = db.report.get_or_create_last_issue_of_user(
        ans.object.object.message.from_id,
    )
    db.report.update_issue(
        issue.id,
        title=ans.object.object.message.text,
    )
    db.shortcuts.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
        state_id=db.bot.get_id_of_state("wait_issue_text"),
    )

    await ans.answer("Отправьте текст проблемы с подробным описанием бага")


@simple_bot_message_handler(
    report_router,
    filters.StateFilter("wait_issue_text"),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def create_issue(ans: SimpleBotEvent):

    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo("dadyarri/jacob")

    issue = db.report.get_or_create_last_issue_of_user(
        ans.object.object.message.from_id,
    )
    db.report.update_issue(
        issue.id,
        text=ans.object.object.message.text,
    )

    new_issue = repo.create_issue(
        title=issue.title,
        body=db.report.generate_issue_text(
            ans.object.object.message.from_id,
        ),
    )

    db.shortcuts.clear_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
    )

    await ans.answer(
        f"Ишью создан: https://github.com/dadyarri/jacob/issues/{new_issue.number}",
        keyboard=kbs.main.main_menu(
            db.students.get_system_id_of_student(
                ans.object.object.message.from_id,
            ),
        ),
    )

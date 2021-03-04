import re
import typing as t

import requests
from pony import orm
from vkwave.types.objects import MessagesConversationMember

from jacob.database.models import Student


def prepare_set_from_vk(data: t.List[MessagesConversationMember]) -> t.Set[int]:
    """
    Формирует список идентификаторов студентов из беседы ВК.

    Args:
        data: Список судентов

    Returns:
        set: идентификаторы ВК студентов
    """
    return {student.member_id for student in data if student.member_id > 0}


@orm.db_session
def prepare_set_from_db(data: t.List[Student]) -> t.Set[int]:
    """
    Формирует список идентификаторов студентов из базы данных.

    Args:
        data: Список судентов

    Returns:
        set: идентификаторы ВК студентов
    """
    return {student.vk_id for student in data}


def get_confirm_message() -> str:
    """
    Генерирует подтверждающее сообщение для регистрации чатов.

    Returns:
        str: подтверждающее сообщение
    """
    text = ""
    query = requests.get("https://fish-text.ru/get", params={"type": "title"})
    if query.status_code == 200:
        text = query.json()["text"]
        text = re.sub(r'[!@"#№$;%^:&?*()\-_=+{}\[\]|/,<.>]', "", text)
        text = text.split(" ")[:3]
    return "-".join(text).lower()

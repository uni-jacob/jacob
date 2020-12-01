import typing as t

from pony.orm import select
from pony.orm import db_session

from database.models import Chat
from database.utils import shortcuts


def get_list_of_chats_by_group(group_id: int) -> t.List[Chat]:
    """
    Возвращает список чатов активной группы.

    Args:
        group_id: Идентификатор группы

    Returns:
        list[Chat]: Список объектов чатов
    """
    return select(c for c in Chat if c.group == group_id)[:]


@db_session
def delete_chat(chat_id: int):
    """
    Удаляет чат из зарегистрированных.

    Args:
        chat_id: идентфикатор чата

    """
    Chat[chat_id].delete()


@db_session
def register_chat(chat_id: int, group_id: int) -> Chat:
    """
    Зарегистрировать чат.

    Args:
        chat_id: идентификатор чата
        group_id: идентификатор группы

    Returns:
        Chat: объект чата
    """
    return Chat(chat_id=chat_id, group_id=group_id)


def is_chat_registered(chat_id: int, group_id: int) -> bool:
    """
    Проверяет, был ли зарегистрирован чат для группы.

    Args:
        chat_id: Идентификатор чата
        group_id: Идентификатор группы

    Returns:
        bool: Флаг регистрации чата
    """
    chat = Chat.get(chat_id=chat_id, group_id=group_id)
    if chat is not None:
        return True
    return False

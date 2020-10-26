import typing as t

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
    query = Chat.select().where(Chat.group_id == group_id)
    return shortcuts.generate_list(query)


def delete_chat(chat_id: int) -> int:
    """
    Удаляет чат из зарегистрированных.

    Args:
        chat_id: идентфикатор чата

    Returns:
        int: количество удаленных записей
    """
    return Chat.delete().where(Chat.id == chat_id).execute()


def register_chat(chat_id: int, group: int) -> Chat:
    """
    Зарегистрировать чат.

    Args:
        chat_id: идентификатор чата
        group: идентификатор группы

    Returns:
        Chat: объект чата
    """
    return Chat.create(chat_id=chat_id, group_id=group)


def is_chat_registered(chat_id: int, group_id: int) -> bool:
    """
    Проверяет, был ли зарегистрирован чат для группы.

    Args:
        chat_id: Идентификатор чата
        group_id: Идентификатор группы

    Returns:
        bool: Флаг регистрации чата
    """
    chat = Chat.get_or_none(chat_id=chat_id, group_id=group_id)
    if chat is not None:
        return True
    return False

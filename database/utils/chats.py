import typing as t

from database.models import Chat
from database.utils import admin
from database.utils import shortcuts


def get_list_of_chats_by_group(admin_id: int) -> t.List[Chat]:
    """
    Возвращает список чатов группы, в активной группе.

    Args:
        admin_id: идентификатор пользователя

    Returns:
        list[Chat]: список объектов чатов
    """
    active_group = admin.get_active_group(admin_id)
    query = Chat.select().where(Chat.group_id == active_group)
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

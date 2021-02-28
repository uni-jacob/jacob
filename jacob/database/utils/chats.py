"""Функции для работы с регистрацией чатов."""

from pony import orm

from jacob.database.models import Chat


@orm.db_session()
def get_list_of_chats_by_group(group_id: int) -> orm.core.Query:
    """
    Возвращает список чатов активной группы.

    Args:
        group_id: Идентификатор группы

    Returns:
        orm.core.Query[Chat]: Список объектов чатов
    """
    return orm.select(chat for chat in Chat if chat.group == group_id)


@orm.db_session
def delete_chat(chat_id: int):
    """
    Удаляет чат из зарегистрированных.

    Args:
        chat_id: идентфикатор чата

    """
    Chat[chat_id].delete()


@orm.db_session
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


@orm.db_session
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
    return chat is not None

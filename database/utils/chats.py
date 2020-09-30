import typing as t

from database.models import Chat
from database.utils import admin
from database.utils import shortcuts
from database.utils import students


def get_list_of_chats_by_group(vk_id: int) -> t.List[Chat]:
    """
    Возвращает список чатов группы, в которой vk_id администратор

    Args:
        vk_id: идентификатор пользователя

    Returns:
        list[Chat]: список объектов чатов
    """
    admin_group = admin.get_admin_feud(students.get_system_id_of_student(vk_id))
    query = Chat.select().where(Chat.group_id == admin_group)
    return shortcuts.generate_list(query)


def delete_chat(chat_id: int) -> int:
    """
    удаляет чат из зарегистрированных

    Args:
        chat_id: идентфикатор чата
    Returns:
        int: количество удаленных записей
    """
    return Chat.delete().where(Chat.id == chat_id).execute()


def register_chat(chat_id: int, group: int) -> Chat:
    """
    Зарегистрировать чат
    Args:
        chat_id: идентификатор чата
        group: идентификатор группы

    Returns:
        Chat: объект чата
    """
    return Chat.create(chat_id=chat_id, group_id=group)

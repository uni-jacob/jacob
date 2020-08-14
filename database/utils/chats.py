import typing as t

from database.models import CachedChat
from database.models import Chat
from database.models import ChatType
from database.utils import admin
from database.utils import shortcuts
from database.utils import students


def get_or_create_cached_chat(chat_id: int) -> CachedChat:
    """
    Возвращает кешированный чат (уже существовавщий или свжесозданный)
    Args:
        chat_id: идентификатор чата ВК

    Returns:
        CachedChat: объект кешированного чата
    """
    return CachedChat.get_or_create(chat_id=chat_id)[0]


def get_list_of_chats_by_group(vk_id: int) -> t.List[Chat]:
    """
    Возвращает список чатов группы, в которой vk_id администратор
    Args:
        vk_id: идентификатор пользователя

    Returns:
        list[Chat]: список объектов чатов
    """
    admin_group = admin.get_admin_feud(students.get_system_id_of_student(vk_id))
    query = Chat.select().where(group=admin_group)
    return shortcuts.generate_list(query)


def get_cached_chats() -> t.List[CachedChat]:
    """
    Возвращает список кешированных чатов

    Returns:
        list[CachedChat]: список всех чатов, находящихся в кеше
    """
    query = CachedChat.select()
    return shortcuts.generate_list(query)


def is_chat_registered(vk_id: int, chat_type: int) -> bool:
    """
    Проверяет, был ли зарегистрирован чат типа chat_type в группе, в которой
    пользователь с vk_id администратор
    Args:
        vk_id: идентификатор пользователя
        chat_type: тип чата

    Returns:
        bool: флаг, указывающий на регистрацию чата
    """
    admin_group = admin.get_admin_feud(students.get_system_id_of_student(vk_id))
    query = Chat.select().where(
        (Chat.group_id == admin_group) & (Chat.chat_type == chat_type)
    )
    if shortcuts.generate_list(query):
        return True
    return False


def find_chat(**kwargs) -> t.Optional[Chat]:
    """
    ищет зарегистрированный чат
    Args:
        **kwargs: параметры поиска

    Returns:
        Optional[Chat]: объект чата
    """
    return Chat.get_or_none(**kwargs)


def find_chat_type(**kwargs) -> t.Optional[ChatType]:
    """
    ищет тип чата
    Args:
        **kwargs: параметры поиска

    Returns:
        Optional[ChatType]: объект типа чата
    """
    return ChatType.get_or_none(**kwargs)

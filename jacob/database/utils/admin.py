import typing as t

from loguru import logger

from database.models import Administrator
from database.models import Group
from database.models import Storage
from services.logger.config import config

logger.configure(**config)


def is_user_admin(admin_id: int) -> bool:
    """
    Проверяет, является ли студент администратором.

    Args:
        admin_id: идентификатор студента в системе

    Returns:
        bool: статус администрирования студента
    """
    admin = Administrator.get_or_none(student_id=admin_id)
    if admin is not None:
        return True
    return False


def get_admin_feud(admin_id: int) -> t.List[Group]:
    """
    Возвращает объекты групп в которых пользователь является администратором.

    Args:
        admin_id: идентификатор администратора

    Returns:
        list[Group]: список объектов групп
    """
    if is_user_admin(admin_id):
        admin_entries = Administrator.select().where(
            Administrator.student_id == admin_id,
        )
        groups = [admin.group_id for admin in admin_entries]
        logger.debug(f"Администрируемое: {groups}")
        return groups
    return []


def get_admin_storage(admin_id: int) -> Storage:
    """
    Ищет хранилище администратора и возвращет объект класса Storage.

    Если хранилище не было найдено, оно создается

    Args:
        admin_id: идентификатор администратора

    Returns:
        Storage: объект хранилища пользователя
    """
    if is_user_admin(admin_id):
        return Storage.get_or_create(id=admin_id)[0]


def get_active_group(admin_id: int) -> t.Optional[Group]:
    """
    Возвращает объект активной группы администратора.

    Если администратор управляет одной группой, возвращается идентификатор группы,
    которой он принадлежит

    Args:
        admin_id: идентификатор администратора

    Returns:
        Optional[Group]: объект активной группы
    """
    if is_user_admin(admin_id):
        if len(get_admin_feud(admin_id)) > 1:
            return Storage.get_by_id(admin_id).active_group
        return Administrator.get(student_id=admin_id).group_id

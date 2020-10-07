import typing as t

from loguru import logger

from database.models import Administrator
from database.models import Group
from database.models import Storage
from database.models import Student
from services.logger.config import config

logger.configure(**config)


def is_user_admin(admin_id: int) -> bool:
    """
    Проверяет, является ли студент администратором

    Args:
        admin_id: идентификатор студента в системе

    Returns:
        bool: статус администрирования студента

    Raises:
        UserIsNotAnAdministrator: когда пользователь не является администратором
    """
    admin = Administrator.get_or_none(id=admin_id)
    if admin is not None:
        return True
    return False


def get_admin_feud(admin_id: int) -> t.Optional[t.List[Group]]:
    """
    Возвращает идентификатор группы в которой пользователь является администратором

    Args:
        admin_id: идентификатор администратора

    Returns:
        list[Group] or None: объект группы
    """
    if is_user_admin(admin_id):
        admin_entries = Administrator.select().where(Administrator.id == admin_id)
        groups = [admin.group_id for admin in admin_entries]
        logger.debug(f"Администрируемое: {groups}")
        return groups


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


def get_active_group(admin_id: int) -> Group:
    """
    Возвращает объект активной группы администратора
    Если администратор управляет одной группой, возвращается идентификатор группы,
    которой он принадлежит

    Args:
        admin_id: идентификатор администратора

    Returns:
        Group: объект активной группы
    """

    if len(get_admin_feud(admin_id)) > 1:
        return Storage.get_by_id(admin_id).active_group
    return Student.get_by_id(admin_id).group_id

import typing as t

from loguru import logger
from pony.orm import select

from jacob.database.models import Administrator
from jacob.database.models import AdminConfig
from jacob.database.models import Group
from jacob.database.models import Storage
from jacob.services.logger.config import config
from jacob.services.exceptions import UserIsNotAnAdmin

logger.configure(**config)


def is_user_admin(admin_id: int) -> bool:
    """
    Проверяет, является ли студент администратором.

    Args:
        admin_id: идентификатор студента в системе

    Returns:
        bool: статус администрирования студента
    """
    return Administrator.exists(student=admin_id)


def get_admin_feud(admin_id: int) -> t.List[Group]:
    """
    Возвращает объекты групп в которых пользователь является администратором.

    Args:
        admin_id: идентификатор администратора

    Returns:
        list[Group]: список объектов групп
    """
    if is_user_admin(admin_id):
        groups = select(
            admin.groups for admin in Administrator if admin.student == admin_id
        )
        logger.debug(f"Администрируемое: {groups}")
        return groups
    raise UserIsNotAnAdmin(f"Пользователь {admin_id} не является админом")


def get_or_create_admin_config(admin_id: int) -> AdminConfig:
    """Ищет хранилище администратора и возвращает объект класса AdminConfig.

    Если хранилище не было найдено, оно создается

    Args:
        admin_id: идентификатор администратора

    Returns:
        AdminConfig: объект хранилища настроек администратора
    """
    if is_user_admin(admin_id):
        if AdminConfig.exists(administrator=admin_id):
            return AdminConfig.get(administrator=admin_id)
        return AdminConfig(administrator=admin_id)
    raise UserIsNotAnAdmin(f"Пользователь {admin_id} не является админом")


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
            return AdminConfig[admin_id].active_group
        return Administrator.get(student_id=admin_id).group
    raise UserIsNotAnAdmin(f"Пользователь {admin_id} не является админом")

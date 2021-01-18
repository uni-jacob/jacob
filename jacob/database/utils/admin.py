"""Бэкенд админской части."""

import warnings

from loguru import logger
from pony import orm

from jacob.database import models
from jacob.services import exceptions
from jacob.services.logger import config as logger_config

logger.configure(**logger_config.config)


def is_user_admin(admin_id: int) -> bool:
    """
    Проверяет, является ли студент администратором.

    Args:
        admin_id: идентификатор студента в системе

    Raises:
        UserIsNotAnAdmin: если пользователь не является администратором

    Returns:
        bool: статус администрирования студента
    """
    warnings.warn(
        "Функция устарела, используйте models.Student.is_admin.", DeprecationWarning
    )
    if models.Admin.exists(student=admin_id):
        return True
    raise exceptions.UserIsNotAnAdmin(
        "Пользователь {0} не является администратором".format(admin_id),
    )


def get_admin_feud(admin_id: int) -> orm.core.Query:
    """
    Возвращает объекты групп в которых пользователь является администратором.

    Args:
        admin_id: идентификатор администратора

    Returns:
        Iterable[models.Group]: список объектов групп
    """
    if models.Student.get(student_id=admin_id).is_admin():
        groups = orm.select(
            admin.groups for admin in models.Admin if admin.student == admin_id
        )
        logger.debug("Администрируемое: {0}".format(groups))
        return groups


def get_active_group(admin_id: int) -> models.Group:
    return models.AdminConfig[admin_id].active_group

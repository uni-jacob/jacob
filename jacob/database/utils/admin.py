"""Функции для работы с администратраторской частью базы данных."""

import typing

from loguru import logger
from pony.orm import select

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
    if models.Administrator.exists(student=admin_id):
        return True
    raise exceptions.UserIsNotAnAdmin(
        "Пользователь {0} не является администратором".format(admin_id),
    )


def get_admin_feud(admin_id: int) -> typing.Iterable[models.Group]:
    """
    Возвращает объекты групп в которых пользователь является администратором.

    Args:
        admin_id: идентификатор администратора

    Returns:
        Iterable[models.Group]: список объектов групп
    """
    if is_user_admin(admin_id):
        groups = select(
            admin.groups for admin in models.Administrator if admin.student == admin_id
        )
        logger.debug("Администрируемое: {0}".format(groups))
        return groups


def get_or_create_admin_config(admin_id: int) -> models.AdminConfig:
    """Ищет хранилище администратора и возвращает объект класса models.AdminConfig.

    Если хранилище не было найдено, оно создается

    Args:
        admin_id: идентификатор администратора

    Returns:
        models.AdminConfig: объект хранилища настроек администратора
    """
    if is_user_admin(admin_id):
        if models.AdminConfig.exists(admin=admin_id):
            return models.AdminConfig.get(admin=admin_id)
        return models.AdminConfig(admin=admin_id)


def get_active_group(admin_id: int) -> typing.Optional[models.Group]:
    """
    Возвращает объект активной группы администратора.

    Если администратор управляет одной группой, возвращается идентификатор группы,
    которой он принадлежит

    Args:
        admin_id: идентификатор администратора

    Returns:
        Optional[models.Group]: объект активной группы
    """
    if is_user_admin(admin_id):
        if len(get_admin_feud(admin_id)) > 1:
            return models.AdminConfig[admin_id].active_group
        return models.Administrator.get(student_id=admin_id).group

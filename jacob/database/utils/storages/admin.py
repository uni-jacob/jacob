"""Управление хранилищами администратора."""
import typing

from loguru import logger

from jacob.database import models
from jacob.database import utils as db
from jacob.services.logger import config as logger_config

logger.configure(**logger_config.config)


def update_admin_config(admin_id: int, **kwargs) -> models.AdminConfig:
    """Обновляет и возвращает объект хранилища настроек администратора.

    Args:
        admin_id: идентификатор администратора
        **kwargs: поля для обновления

    Returns:
        models.AdminConfig: объект хранилища
    """
    store = models.AdminConfig[admin_id]
    store.set(**kwargs)
    logger.debug("Хранилище id{0} обновлено с {1}".format(admin_id, kwargs))
    return store


def get_or_create_admin_config(admin_id: int) -> models.AdminConfig:
    """Ищет хранилище администратора и возвращает объект класса models.AdminConfig.

    Если хранилище не было найдено, оно создается

    Args:
        admin_id: идентификатор администратора

    Returns:
        models.AdminConfig: объект хранилища настроек администратора
    """
    if db.admin.is_user_admin(admin_id):
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
    if db.admin.is_user_admin(admin_id):
        if len(db.admin.get_admin_feud(admin_id)) > 1:
            return models.AdminConfig[admin_id].active_group
        return models.Admin.get(student_id=admin_id).group


def get_active_chat(admin_id: int) -> models.Chat:
    """Получает объект активного чата конкретного администратора.

    Args:
        admin_id: идентификатор администратора

    Returns:
        Chat: объект активного чата
    """
    # TODO: Что делать, если активный чат не выбран?
    store = db.admin.get_or_create_admin_config(admin_id)
    return models.Chat.get_by_id(store.active_chat)

"""Шорткаты для работы с хранилищем администратора."""

from loguru import logger

from jacob.database import models
from jacob.database.utils import storages
from jacob.services.logger import config as logger_config

logger.configure(**logger_config.config)


def invert_names_usage(admin_id: int) -> models.AdminConfig:
    """Изменяет использование имен у администратора.

    Args:
        admin_id: идентификатор администратора

    Returns:
        Storage: объект хранилища
    """
    store = storages.admin.get_or_create_admin_config(admin_id)
    state = not store.names_usage
    return storages.admin.update_admin_config(admin_id, names_usage=state)

"""Бэкенд меню Призыва."""
from loguru import logger

from jacob.database import models
from jacob.services.logger import config as logger_config

logger.configure(**logger_config.config)


def get_mention_storage(admin_id: int) -> models.MentionStorage:
    """Получает хранилище Призыва админа.

    Args:
        admin_id: идентификатор администратора

    Returns:
        models.MentionStorage: Хранилище Призыва
    """
    return models.MentionStorage.get(admin=admin_id)


def update_mention_storage(admin_id: int, **kwargs) -> models.MentionStorage:
    """Обновляет хранилище Призыва админа.

    Args:
        admin_id: Идентификатор администратора
        **kwargs: Поля для обновления

    Returns:
        models.MentionStorage: Объект хранилища
    """
    store = models.MentionStorage[admin_id]
    store.set(**kwargs)
    logger.debug("Хранилище Призыва id{0} обновлено с {1}".format(admin_id, kwargs))
    return store

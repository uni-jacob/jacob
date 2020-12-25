"""Бэкенд меню Призыва."""

from jacob.database import models


def get_mention_storage(admin_id: int) -> models.MentionStorage:
    """Получает хранилище Призыва админа.

    Args:
        admin_id: идентификатор администратора

    Returns:
        models.MentionStorage: Хранилище Призыва
    """
    return models.MentionStorage.get(admin=admin_id)

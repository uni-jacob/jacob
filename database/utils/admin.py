from loguru import logger
from playhouse import shortcuts

from database.models import Administrator
from database.models import Group
from database.models import Storage
from services.exceptions import UserIsNotAnAdministrator
from services.logger.config import config

logger.configure(**config)


def is_user_admin(admin_id: int) -> bool:
    """
    Проверяет, является ли студент администратором
    Args:
        admin_id: идентификатор студента в системе

    Returns:
        bool: статус администрирования студента
    """
    admin = Administrator.get_or_none(id=admin_id)
    if admin is not None:
        return True
    raise UserIsNotAnAdministrator(f"Студент с {admin_id=} не является администратором")


def get_admin_feud(admin_id: int) -> Group:
    """
    Возвращает идентификатор группы в которой пользователь является администратором
    Args:
        admin_id: идентификатор администратора

    Returns:
        Group: объект группы
    """
    if is_user_admin(admin_id):
        admin = Administrator.get_or_none(id=admin_id)
        logger.debug(f"{admin.group_id}")
        return admin.group_id


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


def update_admin_storage(admin_id: int, **kwargs) -> Storage:
    """
    Обновляет хранилище администратора и возвращает объект хранилища
    Args:
        admin_id: идентификатор администратора
        **kwargs: поля для обновления

    Returns:
        Storage: объект хранилища
    """
    a_id = shortcuts.update_model_from_dict(get_admin_storage(admin_id), kwargs).save()
    return get_admin_storage(a_id)


def clear_admin_storage(admin_id: int) -> Storage:
    """
    Очищает хранилище администратора
    Args:
        admin_id: идентификатор администратора

    Returns:
        Storage: объект хранилища
    """
    return update_admin_storage(
        admin_id,
        state_id=1,
        mailing_id=None,
        selected_students="",
        text="",
        attaches="",
    )

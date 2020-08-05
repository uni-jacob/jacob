import os
import urllib.parse as urlparse

from database.models import Storage


def get_admin_storage(admin_id: int) -> Storage:
    """
    Ищет хранилище администратора и возвращет объект класса Storage.
    Если хранилище не было найдено, оно создается
    Args:
        admin_id: идентификатор администратора
    Returns:
        Storage: объект хранилища пользователя
    """
    return Storage.get_or_create(id=admin_id)


def update_admin_storage(admin_id: int, **kwargs) -> Storage:
    """
    Обновляет хранилище администратора и возвращает объект хранилища
    Args:
        admin_id: идентификатор администратора
        **kwargs: поля для обновления

    Returns:
        Storage: объект хранилища
    """
    return get_admin_storage(admin_id).update(**kwargs)


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


def get_db_credentials() -> dict:
    """
    Создает словарь с учетными данными базы данных из переменной окружения DATABASE_URL
    Returns:
        dict: Учетные данные
    """
    url = urlparse.urlparse(os.getenv("DATABASE_URL"))
    db_creds = {
        "user": url.username,
        "password": url.password,
        "host": url.hostname,
        "port": url.port,
        "database": url.path[1:],
    }

    return db_creds

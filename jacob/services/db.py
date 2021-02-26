"""Мелкие утилиты для работы с базой данных."""


import typing
from urllib import parse as urlparse

StrInt = typing.TypeVar("StrInt", str, int)


def get_db_credentials(source: str) -> typing.Dict[str, StrInt]:
    """
    Создает словарь с учетными данными базы данных из ссылки.

    Args:
        source: URL базы данных

    Returns:
        dict: Учетные данные
    """
    url = urlparse.urlparse(source)

    return {
        "user": url.username,
        "password": url.password,
        "host": url.hostname,
        "port": url.port,
        "database": url.path[1:],
    }

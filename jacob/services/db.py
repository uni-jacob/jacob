import os
import typing as t
from urllib import parse as urlparse


StrInt = t.TypeVar("StrInt", str, int)


def get_db_credentials(source: str) -> t.Dict[str, StrInt]:
    """
    Создает словарь с учетными данными базы данных из переменной окружения DATABASE_URL.

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

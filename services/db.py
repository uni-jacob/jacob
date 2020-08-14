import os
import typing as t
import urllib.parse as urlparse


StrInt = t.TypeVar("StrInt", str, int)


def get_db_credentials() -> t.Dict[str, StrInt]:
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

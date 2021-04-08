"""Мелкие утилиты для работы с базой данных."""
from typing import Dict, Optional, Union
from urllib import parse as urlparse


def get_db_credentials(source: str) -> Dict[str, Optional[Union[str, int]]]:
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

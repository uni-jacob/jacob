import os
import urllib.parse as urlparse


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

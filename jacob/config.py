import logging
import os

from jacob.services.exceptions import UnknownEnvironmentType


def get_token() -> str:
    """
    Получает токен от нужного сообщества в зависимости от выбранного окружения.

    Raises:
        UnknownEnvironmentType: Если указан некорректный тип окружения

    Returns:
        str: Токен VK Bot API
    """
    environment = os.getenv("ENV").upper()
    var_name = f"{environment}_VK_TOKEN"
    token = os.getenv(var_name)
    if token is None:
        raise UnknownEnvironmentType(f"{environment} не определён")

    logging.info(f"Выбран токен {var_name}")
    return token


def get_database_url() -> str:
    """
    Получает URL базы данных в зависимости от того, запущен ли проект с помощью pytest.

    Returns:
        str: URL базы данных
    """
    if "PYTEST_CURRENT_TEST" in os.environ:
        logging.debug("Выбрана тестовая БД")
        return os.getenv("TEST_DATABASE_URL")

    logging.debug("Выбрана основная БД")
    return os.getenv("DATABASE_URL")

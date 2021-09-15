import logging
import os

from jacob.services.exceptions import UnknownEnvironmentType


def generate_abbreviation(phrase: str) -> str:
    """
    Создаёт аббревиатуру из фразы.

    Args:
        phrase: Фраза

    Returns:
        str: Аббревиатура
    """
    abbr = "".join([word[0].upper() for word in phrase.split(" ")])
    logging.info(f"Аббревиатура {phrase} - {abbr}")
    return abbr


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

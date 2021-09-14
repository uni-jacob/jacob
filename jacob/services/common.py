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
    return "".join([word[0].upper() for word in phrase.split(" ")])


def get_token():
    environment = os.getenv("ENV").upper()
    if environment in ("PRODUCTION", "DEV"):
        return os.getenv(f"{environment}_VK_TOKEN")

    raise UnknownEnvironmentType(f"{environment} не определён")

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
    if os.getenv("ENV") == "production":
        return os.getenv("STABLE_VK_TOKEN")
    elif os.getenv("ENV") == "dev":
        return os.getenv("CANARY_VK_TOKEN")
    else:
        raise UnknownEnvironmentType(f"{os.getenv('ENV')} не определён")

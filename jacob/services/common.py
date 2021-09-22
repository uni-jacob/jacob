import logging
import os

from vkbottle import VKAPIError
from vkbottle.dispatch.rules.bot import VBMLRule

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


def vbml_rule(bot):
    return VBMLRule.with_config(
        bot.labeler.rule_config,
    )  # FIXME: temporary fix, bug in vkbottle


async def handle_captcha(e: VKAPIError):
    logging.debug(f"Rate limit error: {e.raw_error['captcha_img']}")

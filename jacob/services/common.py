import logging

from vkbottle.dispatch.rules.bot import VBMLRule


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


def vbml_rule(bot):
    return VBMLRule.with_config(
        bot.labeler.rule_config,
    )  # FIXME: temporary fix, bug in vkbottle

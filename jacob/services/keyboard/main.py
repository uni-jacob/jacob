import typing

from loguru import logger
from pony import orm
from vkwave.bots import Keyboard

from jacob.database.utils import admin, uni
from jacob.services import media

JSONStr = str


def main_menu(admin_id: int) -> JSONStr:
    """
    Генерирует клавиатуру главного меню.

    Args:
        admin_id: Идентификатор пользователя

    Returns:
        JSONStr: Строка с клавиатурой

    """
    is_admin = admin.is_user_admin(admin_id)
    logger.debug(f"{is_admin=}")
    kb = Keyboard()
    if is_admin:
        kb.add_text_button(text="📢 Призыв", payload={"button": "call"})
        kb.add_text_button(text="💰 Финансы", payload={"button": "finances"})
        kb.add_row()
    if is_admin:
        kb.add_text_button(text="📕 Менеджмент группы", payload={"button": "group_mgmt"})
        kb.add_row()
        kb.add_text_button(text="⚙ Настройки", payload={"button": "settings"})
        kb.add_row()
    kb.add_text_button(
        text="⚠ Сообщить об ошибке",
        payload={"button": "report_error"},
    )
    return kb.get_keyboard()


def choose_register_way() -> JSONStr:
    kb = Keyboard()

    kb.add_text_button(
        text="Новая группа",
        payload={"button": "create_new_group"},
    )
    kb.add_text_button(
        text="Существующая группа",
        payload={"button": "choose_existing_group"},
    )

    return kb.get_keyboard()


@orm.db_session
def universities() -> Keyboard:
    kb = Keyboard()

    unies = uni.get_all()

    for university in unies:
        if len(kb.buttons[-1]) == 2:
            kb.add_row()

        kb.add_text_button(
            media.get_university_abbreviation(university.name),
            payload={
                "button": "university",
                "university": university.id,
            },
        )

    if kb.buttons[-1]:
        kb.add_row()

    return kb


def universities_with_create() -> JSONStr:

    kb = universities()

    kb.add_text_button("➕ Создать университет", payload={"button": "create_university"})

    kb.add_row()

    kb.add_text_button("◀️ Назад", payload={"button": "main_menu"})

    return kb.get_keyboard()


def universities_without_create() -> JSONStr:
    kb = universities()

    kb.add_text_button("◀️ Назад", payload={"button": "main_menu"})

    return kb.get_keyboard()


def group_privacy():
    kb = Keyboard()

    kb.add_text_button("Публичная", payload={"button": "group_privacy", "value": False})
    kb.add_text_button("Приватная", payload={"button": "group_privacy", "value": True})

    kb.add_row()

    kb.add_text_button("🚫 Отмена", payload={"button": "cancel"})

    return kb.get_keyboard()


def public_groups(university: typing.Optional[int]):
    kb = Keyboard()

    if university is None:
        raise TypeError("Значение university не может быть пустым")

    with orm.db_session:
        groups = uni.get_public_groups(university)

        for group in groups:
            if len(kb.buttons[-1]) == 2:
                kb.add_row()

            kb.add_text_button(
                group.group_num, payload={"button": "group", "group": group.id}
            )

    if kb.buttons[-1]:
        kb.add_row()

    kb.add_text_button("🚫 Отмена", payload={"button": "cancel"})

    return kb.get_keyboard()

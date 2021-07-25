from .. import models


def is_user(vk_id: int) -> bool:
    """Проверяет регистрацию анонимного пользователя.

    Args:
        vk_id: ИД ВК проверяемого пользователя

    Returns:
        bool: Зарегистрирован ли пользователь.
    """
    return bool(models.User.get_or_none(vk_id=vk_id))

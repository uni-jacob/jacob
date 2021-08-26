from tortoise.transactions import in_transaction

from jacob.database import models
from jacob.database.utils.states import get_state_id_by_name


async def is_user(vk_id: int) -> bool:
    """Проверяет регистрацию анонимного пользователя.

    Args:
        vk_id: ИД ВК проверяемого пользователя

    Returns:
        bool: Зарегистрирован ли пользователь.
    """
    async with in_transaction():
        return bool(await models.User.get_or_none(vk_id=vk_id))


async def create_user(vk_id: int) -> models.User:
    """
    Создаёт нового пользователя и хранилище стейтов для него.

    Args:
        vk_id: ИД ВК нового пользователя

    Returns:
        models.User: Объект нового пользователя
    """
    state_id = await get_state_id_by_name("main")
    async with in_transaction():
        user = await models.User.create(vk_id=vk_id)
        await user.save()
        await models.StateStorage.create(
            user_id=user.id,
            state_id=state_id,
        )
        return user

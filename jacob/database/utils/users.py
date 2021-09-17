import logging
from typing import Optional

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
        b = bool(await models.User.get_or_none(vk_id=vk_id))
        logging.info(f"Пользователь {vk_id} {'' if b else 'не'} зарегистрирован")
        return b


async def get_user_id(vk_id: int) -> Optional[int]:
    """
    Получает ИД пользователя в системе.

    Args:
        vk_id: ИД ВК пользователя

    Returns:
        Optional[int]: ИД пользователя
    """
    async with in_transaction():
        logging.info(f"Поиск пользователя @id{vk_id}...")
        query = await models.User.get_or_none(vk_id=vk_id)

        try:
            logging.info(f"ИД пользователя @id{vk_id} = {query.id}")
            return query.id
        except AttributeError:
            logging.error(f"Пользователь №{vk_id} не найден")
            return None


async def create_user(vk_id: int) -> models.User:
    """
    Создаёт нового пользователя и хранилище стейтов для него.

    Args:
        vk_id: ИД ВК нового пользователя

    Returns:
        models.User: Объект нового пользователя
    """
    async with in_transaction():
        logging.info(f"Создание пользователя с параметрами {locals()}...")
        user = await models.User.get_or_create(**locals())
        logging.info(f"Создание хранилища пользователя {user[0].id}...")
        await models.StateStorage.get_or_create(
            user_id=user[0].id,
        )
        return user[0]


async def get_state_of_user(vk_id: int) -> Optional[int]:
    """
    Получает стейт пользователя.

    Args:
        vk_id: ИД ВК пользователя

    Returns:
        Optional[int]: ИД стейта
    """
    user_id = await get_user_id(vk_id)
    async with in_transaction():
        query = await models.StateStorage.get_or_none(user_id=user_id)

        try:
            state = await query.state
        except AttributeError:
            return None
        try:
            return state.id
        except AttributeError:
            return None


async def set_state(vk_id: int, state_name: str) -> str:
    """
    Изменяет стейт у пользователя.

    Args:
        vk_id: ИД ВК пользователя
        state_name: Название стейта

    Returns:
        str: Установленное имя стейта.
    """
    user_id = await get_user_id(vk_id)
    state_id = await get_state_id_by_name(state_name)
    async with in_transaction():
        await models.StateStorage.filter(user_id=user_id).update(state_id=state_id)
        logging.info(f"Пользователю @id{vk_id} установлен стейт {state_name}")
    return state_name

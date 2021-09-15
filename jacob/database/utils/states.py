import logging
from typing import Optional

from tortoise.transactions import in_transaction

from jacob.database import models
from jacob.services.exceptions import StateNotFound


async def get_state_id_by_name(state_name: str) -> Optional[int]:
    """
    Получает ИД стейта по его имени.
    Args:
        state_name: имя стейта

    Returns:
        Optional[int]: ИД стейта
    """
    async with in_transaction():
        logging.info(f"Поиск стейта {state_name}...")
        query = await models.State.get_or_none(description=state_name)

        try:
            logging.info(f"ИД стейта {state_name} = {query.id}")
            return query.id
        except AttributeError:
            raise StateNotFound(f"Стейт {state_name} не найден!")


async def get_state_name_by_id(state_id: int) -> Optional[str]:
    """
    Получает имя стейта по его ИД.
    Args:
        state_id: ИД стейта

    Returns:
        Optional[str]: имя стейта
    """
    async with in_transaction():
        logging.info(f"Поиск стейта №{state_id}...")
        query = await models.State.get_or_none(id=state_id)

        try:
            logging.info(f"ИД стейта {state_id} = {query.description}")
            return query.description
        except AttributeError:
            raise StateNotFound(f"Стейт №{state_id} не найден!")

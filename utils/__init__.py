from database.models import Administrator
from database.models import Storage


async def get_storage(user_id: int) -> Storage:
    """
    Возвращает объект хранилища администратора
    Args:
        user_id: Идентфикатор администратора

    Returns:
        Storage: хранилище администратора
    """
    admin = await Administrator.get_or_none(vk_id=user_id)
    if admin is not None:
        user = await Storage.get_or_create(id=admin.id)
        return user[0]
    else:
        return None

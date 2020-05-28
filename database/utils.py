from .models import Administrator
from .models import Storage
from .models import Student


async def is_admin(user_id: int) -> bool:
    """
    Проверяет наличие прав администратора (любого заведения/группы) у выбранного
    пользователя

    Args:
        user_id: Идентификатор пользователя

    Returns:
        bool: Статус администратора
    """
    student = await Student.get_or_none(vk_id=user_id)
    if student:
        admin = await Administrator.get_or_none(id=student.id)
        if admin:
            return True
        return False
    return False


async def get_storage(user_id: int) -> Storage:
    """
    Возвращает объект хранилища администратора
    Args:
        user_id: Идентфикатор администратора

    Returns:
        Storage: хранилище администратора
    """
    student = await Student.get_or_none(vk_id=user_id)
    if student:
        admin = await Administrator.get_or_none(id=student.id)
        if admin is not None:
            user = await Storage.get_or_create(id=admin.id)
            return user[0]
        else:
            return None
    return None


async def clear_storage(user_id: int):
    """
    Очищает пользовательское хранилище

    Args:
        user_id: Идентификатор пользователя
    Returns:
        bool: True в случае успеха, False, если администратор не был найден
    """
    student = await Student.get_or_none(vk_id=user_id)
    if student:
        admin = await Administrator.get_or_none(id=student.id)
        if admin is not None:
            user = await Storage.get(id=admin.id)
            user.selected_students = None
            user.text = None
            user.attaches = None
            user.mailing_id = None
            await user.save()
            return True
        return False
    return False

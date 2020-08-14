from database.models import Group


def find_group(**kwargs) -> Group:
    """
    Ищет группу по указанным параметрам
    Args:
        **kwargs: Параметры поиска

    Returns:
        Group: объект группы
    """
    return Group.get(**kwargs)

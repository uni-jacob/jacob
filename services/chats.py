import typing as t

from vkwave.types.objects import MessagesConversationMember

from database.models import Student


def prepare_set_from_vk(data: t.List[MessagesConversationMember]) -> t.Set[int]:
    """
    Формирует список идентификаторов студентов из беседы ВК
    Args:
        data: Список судентов

    Returns:
        set: идентификаторы ВК студентов
    """
    return {student.member_id for student in data if student.member_id > 0}


def prepare_set_from_db(data: t.List[Student]) -> t.Set[int]:
    """
        Формирует список идентификаторов студентов из базы данных
        Args:
            data: Список судентов

        Returns:
            set: идентификаторы ВК студентов
        """
    return {student.vk_id for student in data}

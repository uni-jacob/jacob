import typing as t

from database import utils as db
from database.models import FinancialCategory


def get_list_of_fin_categories(group_id: int) -> t.List[FinancialCategory]:
    """
    Возвращает список категорий финансов группы
    Args:
        group_id: идентификатор группы

    Returns:
        List[FinancialCategory]: категории финансов
    """

    query = FinancialCategory.select().where(FinancialCategory.group_id == group_id)
    return db.shortcuts.generate_list(query)


def find_fin_category(**kwargs) -> t.Optional[FinancialCategory]:
    """
    Ищет категорию финансов
    Args:
        **kwargs: Критерии поиска

    Returns:
        FinancialCategory or None: объект категории
    """
    return FinancialCategory.get_or_none(**kwargs)

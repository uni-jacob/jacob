import typing as t

from peewee import fn

from database import utils as db
from database.models import FinancialCategory
from database.models import FinancialDonate


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


def find_donate(category_id: int, student_id: int) -> t.Optional[FinancialDonate]:
    """
    Ищет существующий доход

    Args:
        category_id: идентификатор категории
        student_id: идентификатор студента

    Returns:
        FinancialDonate or None: объект дохода
    """
    return FinancialDonate.get_or_none(
        FinancialDonate.category == category_id, FinancialDonate.student == student_id
    )


def add_or_edit_donate(category_id: int, student_id: int, summ: int):
    """
    Создает новый доход или редактирует существующий

    Args:
        category_id: Идентификатор категории
        student_id: Источник дохода (идентификатор студента)
        summ: Сумма дохода
    """
    if donate := find_donate(category_id, student_id):
        donate.update(summ=donate.summ + summ, update_date=fn.NOW()).execute()
    else:
        return FinancialDonate.create(
            category_id=category_id, student_id=student_id, summ=summ, update_date=None
        )

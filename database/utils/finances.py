import typing as t

from peewee import fn

from database import utils as db
from database.models import FinancialCategory
from database.models import FinancialDonate
from database.models import FinancialExpense
from database.utils.students import get_active_students


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


def get_debtors(category_id: int) -> t.List[int]:
    """
    Ищет должников (не сдавших деньги на категорию вообще или не всю сумму)
    Args:
        category_id: идентификатор категории

    Returns:
        List[int]: список идентификаторов
    """

    category = find_fin_category(id=category_id)
    students = get_active_students(category.group_id)
    debtors = []
    for student in students:
        donate = find_donate(category_id, student.id)
        if donate is None or donate.summ < category.summ:
            debtors.append(student.id)

    return debtors


def add_expense(category_id, summ) -> FinancialExpense:
    """
    Создает новый расход

    Args:
        category_id: идентификатор категории
        summ: сумма расхода

    Returns:
        FinancialExpense: объект расхода
    """
    return FinancialExpense.create(
        category_id=category_id,
        summ=summ,
    )


def calculate_donates_in_category(category_id: int) -> int:
    """
    Вычисляет сумму собранных в категории денег

    Args:
        category_id: идентификатор категории

    Returns:
        int: Сумма сборов
    """
    summ = 0
    donates = FinancialDonate.select(FinancialDonate.summ).where(
        FinancialDonate.category == category_id
    )
    for donate in donates:
        summ += donate.summ

    return summ


def calculate_expenses_in_category(category_id: int) -> int:
    """
    Вычисляет сумму расходов в категории
    Args:
        category_id: идентификатор категории

    Returns:
        int: сумма расходов
    """
    summ = 0
    donates = FinancialExpense.select(FinancialExpense.summ).where(
        FinancialExpense.category == category_id
    )
    for donate in donates:
        summ += donate.summ

    return summ

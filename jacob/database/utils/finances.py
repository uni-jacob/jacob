"""Функции для работы с блоком Финансы."""

from datetime import datetime

from pony import orm

from jacob.database import models
from jacob.database.utils.students import get_active_students


@orm.db_session
def get_fin_categories(group_id: int) -> list[models.FinancialCategory]:
    """
    Возвращает список категорий финансов группы.

    Args:
        group_id: идентификатор группы

    Returns:
        List[FinancialCategory]: категории финансов
    """
    return orm.select(fc for fc in models.FinancialCategory if fc.group == group_id)


@orm.db_session
def add_or_edit_donate(
    category_id: int,
    student_id: int,
    summ: int,
) -> models.FinancialIncome:
    """
    Создает новый доход или редактирует существующий.

    Args:
        category_id: Идентификатор категории
        student_id: Источник дохода (идентификатор студента)
        summ: Сумма дохода

    Returns:
        FinancialIncome: Объект дохода
    """
    donate = models.FinancialIncome.get(
        financial_category=category_id,
        student=student_id,
    )
    if donate is not None:
        donate.summ = donate.summ + summ
        donate.update_date = datetime.now()
        return donate
    return models.FinancialIncome(
        financial_category=category_id,
        student=student_id,
        summ=summ,
        update_date=None,
    )


@orm.db_session
def get_debtors(category_id: int) -> list[int]:
    """
    Ищет должников (не сдавших деньги на категорию вообще или не всю сумму).

    Args:
        category_id: идентификатор категории

    Returns:
        List[int]: список идентификаторов
    """
    category = models.FinancialCategory[category_id]
    students = get_active_students(category.group)
    debtors = []
    for student in students:
        donate = models.FinancialIncome.get(
            financial_category=category_id,
            student=student.id,
        )
        if donate is None or donate.summ < category.summ:
            debtors.append(student.id)

    return debtors


@orm.db_session
def add_expense(category_id: int, summ: int) -> models.FinancialExpense:
    """
    Создает новый расход.

    Args:
        category_id: идентификатор категории
        summ: сумма расхода

    Returns:
        FinancialExpense: объект расхода
    """
    return models.FinancialExpense(
        financial_category=category_id,
        summ=summ,
    )


@orm.db_session
def calculate_incomes_in_category(category_id: int) -> int:
    """
    Вычисляет сумму собранных в категории денег.

    Args:
        category_id: идентификатор категории

    Returns:
        int: Сумма сборов
    """
    return orm.sum(
        fi.summ for fi in models.FinancialIncome if fi.financial_category == category_id
    )


@orm.db_session
def calculate_expenses_in_category(category_id: int) -> int:
    """
    Вычисляет сумму расходов в категории.

    Args:
        category_id: идентификатор категории

    Returns:
        int: сумма расходов
    """
    return orm.sum(
        fe.summ
        for fe in models.FinancialExpense
        if fe.financial_category == category_id
    )


@orm.db_session
def get_or_create_finances_category(
    group_id: int,
    name: str,
    summ: int,
) -> models.FinancialCategory:
    """
    Создаёт новую финансовую категорию, или возвращает уже существующую.

    Args:
        group_id: Идентификатор группы
        name: Название категории
        summ: Сумма сборов

    Returns:
        FinancialCategory: объект категории
    """
    fin_cat = models.FinancialCategory.get(group=group_id, name=name, summ=summ)
    if fin_cat is not None:
        return fin_cat
    return models.FinancialCategory(group=group_id, name=name, summ=summ)

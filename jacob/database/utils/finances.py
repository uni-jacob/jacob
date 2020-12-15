"""Функции для работы с блоком Финансы."""

import typing
from datetime import datetime

from pony.orm import db_session
from pony.orm import select

from jacob.database import models
from jacob.database.utils.students import get_active_students


def get_fin_categories(group_id: int) -> typing.List[models.FinancialCategory]:
    """
    Возвращает список категорий финансов группы.

    Args:
        group_id: идентификатор группы

    Returns:
        List[FinancialCategory]: категории финансов
    """
    return select(fc for fc in models.FinancialCategory if fc.group == group_id)[:]


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
    donate = models.FinancialIncome.get(category=category_id, student=student_id)
    if donate is not None:
        with db_session:
            donate.summ = (donate.summ + summ,)
            donate.update_date = (datetime.now(),)
        return donate
    with db_session:
        return models.FinancialIncome(
            category_id=category_id,
            student_id=student_id,
            summ=summ,
            update_date=None,
        )


def get_debtors(category_id: int) -> typing.List[int]:
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
        donate = models.FinancialIncome.get(category=category_id, student=student.id)
        if donate is None or donate.summ < category.summ:
            debtors.append(student.id)

    return debtors


def add_expense(category_id: int, summ: int) -> models.FinancialExpense:
    """
    Создает новый расход.

    Args:
        category_id: идентификатор категории
        summ: сумма расхода

    Returns:
        FinancialExpense: объект расхода
    """
    with db_session:
        return models.FinancialExpense(
            category_id=category_id,
            summ=summ,
        )


def calculate_incomes_in_category(category_id: int) -> int:
    """
    Вычисляет сумму собранных в категории денег.

    Args:
        category_id: идентификатор категории

    Returns:
        int: Сумма сборов
    """
    return sum(fi.summ for fi in models.FinancialIncome if fi.category == category_id)


def calculate_expenses_in_category(category_id: int) -> int:
    """
    Вычисляет сумму расходов в категории.

    Args:
        category_id: идентификатор категории

    Returns:
        int: сумма расходов
    """
    return sum(fe.summ for fe in models.FinancialExpense if fe.category == category_id)


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
    if models.FinancialCategory.exists(group_id=group_id, name=name, summ=summ):
        return models.FinancialCategory.get(group_id=group_id, name=name, summ=summ)
    with db_session:
        return models.FinancialCategory(group_id=group_id, name=name, summ=summ)

"""Утилиты для работы с работы с БД модуля 'Финансы'."""


import typing

from pony import orm

from jacob.database import models
from jacob.database.utils import finances


def generate_debtors_call(category_id: int) -> typing.List[str]:
    """
    Генерирует сообщение призыва должников.

    Args:
        category_id: идентификатор категории сбора

    Returns:
        List[str]: сообщение(я) призыва должников
    """
    message_len_limit = 2000

    debtors = finances.get_debtors(category_id)

    with orm.db_session:
        category = models.FinancialCategory[category_id]

        messages = [
            "Вы не сдали на {0} сумму, указанную напротив вашего имени\n".format(
                category.name,
            ),
        ]
        for debtor_id in debtors:
            donate = models.FinancialIncome.get(
                financial_category=category.id,
                student=debtor_id,
            )
            if donate:
                summ = category.summ - donate.summ
            else:
                summ = category.summ
            student = models.Student[debtor_id]
            tmp = "@id{0} ({1} {2}) - {3} руб.\n".format(
                student.vk_id,
                student.first_name,
                student.last_name,
                summ,
            )
            if len(messages[-1]) < message_len_limit:
                messages[-1] += tmp
            else:
                messages.append("")

    return messages

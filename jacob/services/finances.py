"""Утилиты для работы с работы с БД модуля 'Финансы'."""


import typing

from jacob.database import models
from jacob.database import utils as db


def generate_debtors_call(admin_id: int) -> typing.List[str]:
    """
    Генерирует сообщение призыва должников.

    Args:
        admin_id: идентификатор администратора

    Returns:
        List[str]: сообщение(я) призыва должников
    """
    message_len_limit = 2000

    store = db.admin.get_admin_storage(admin_id)
    debtors = db.finances.get_debtors(store.category_id)
    category = models.FinancialCategory.get_by_id(store.category_id)
    messages = [
        "Вы не сдали на {0} сумму, указанную напротив вашего имени\n".format(
            category.name,
        ),
    ]
    for debtor_id in debtors:
        donate = models.FinancialIncome.get_or_none(
            category=category.id,
            student=debtor_id,
        )
        if donate:
            summ = category.summ - donate.summ
        else:
            summ = category.summ
        student = models.Student.get_by_id(debtor_id)
        tmp = "@id{0} ({1} {2}) - {3} руб.\n".format(
            student.vk_id,
            student.first_name,
            student.second_name,
            summ,
        )
        if len(messages[-1]) < message_len_limit:
            messages[-1] += tmp
        else:
            messages.append("")

    return messages

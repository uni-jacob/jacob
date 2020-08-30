import typing as t

from database import utils as db


def generate_debtors_call(admin_id: int) -> t.List[str]:
    """
    Генерирует сообщение призыва должников
    Args:
        admin_id: идентификатор администратора

    Returns:
        List[str]: сообщение(я) призыва должников
    """
    store = db.admin.get_admin_storage(admin_id)
    debtors = db.finances.get_debtors(store.category_id)
    category = db.finances.find_fin_category(id=store.category_id)
    messages = [""]
    for debtor_id in debtors:
        if donate := db.finances.find_donate(store.category_id, debtor_id):
            summ = category.summ - donate.summ
        else:
            summ = category.summ
        student = db.students.find_student(id=debtor_id)
        tmp = (
            f"@id{student.vk_id} ({student.first_name} {student.second_name}) - "
            f"{summ} руб.\n"
        )
        if len(messages[-1]) < 2000:
            messages[-1] += tmp
        else:
            messages.append("")

    return messages

from database import utils as db


def generate_debtors_call(admin_id: int):
    """
    Генерирует сообщение призыва должников
    Args:
        admin_id: идентификатор администратора

    Returns:
        str: сообщение призыва должников
    """
    store = db.admin.get_admin_storage(admin_id)
    debtors = db.finances.get_debtors(store.category_id)
    category = db.finances.find_fin_category(id=store.category_id)
    msg_parts = []
    for debtor_id in debtors:
        if donate := db.finances.find_donate(store.category_id, debtor_id):
            summ = category.summ - donate.summ
        else:
            summ = category.summ
        student = db.students.find_student(id=debtor_id)
        msg_parts.append(
            f"@id{student.vk_id} ({student.first_name} {student.second_name}) - {summ}"
        )

    return ";\n".join(msg_parts)

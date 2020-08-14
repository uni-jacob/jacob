def main_menu(user_id: int) -> JSONStr:
    """
    Генерирует клавиатуру главного меню
    Args:
        user_id: Идентификатор пользователя
    Returns:
        JSONStr: Строка с клавиатурой

    """
    is_admin = db.admin.is_user_admin(
        admin_id=db.students.get_system_id_of_student(user_id)
    )
    kb = Keyboard()
    if is_admin:
        kb.add_text_button(text="📢 Призыв", payload={"button": "call"})
        kb.add_text_button(text="💰 Финансы", payload={"button": "finances"})
        kb.add_row()
    kb.add_text_button(text="📅 Расписание", payload={"button": "schedule"})
    kb.add_text_button(text="📨 Рассылки", payload={"button": "mailings"})
    if is_admin:
        kb.add_row()
        kb.add_text_button(text="⚙ Настройки", payload={"button": "settings"})
        kb.add_text_button(text="🌐 Веб", payload={"button": "web"})
    return kb.get_keyboard()

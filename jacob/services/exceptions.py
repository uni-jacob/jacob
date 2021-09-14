class StateNotFound(Exception):
    """Возбуждается когда get_state_id_by_name не может найти стейт"""

    pass


class PayloadIsEmptyOrNotFound(Exception):
    """Возбуждается когда пейлоад не найден или пуст"""

    pass


class UnknownEnvironmentType(Exception):
    """Возбуждается при попытке получить токен для неопределённого типа окружения."""

    pass

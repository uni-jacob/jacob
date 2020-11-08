class UserIsNotAnAdministrator(Exception):
    """Вызывается, когда пользователь не является администратором."""

    pass


class BotStateNotFound(Exception):
    """Вызывается при попытке получить идентификатор не существующего статуса бота."""

    pass


class StudentNotFound(Exception):
    """Вызывается, когда студент с заданными параметрами поиска не был найден."""

    pass


class ChatNotFound(Exception):
    """Вызывается, когда чат с заданными параметрами поиска не был найден."""

    pass


class AttachmentLimitExceeded(Exception):
    """Вызывается если лимит вложений в сообщении был превышен."""

    pass


class EmptyCallMessage(Exception):
    """Вызывется при попытке отправить пустое сообщение призыва."""

    pass


class BotIsNotAChatAdministrator(Exception):
    """Вызывается при попытке доступа к чату, в котором бот не администратор."""

    pass

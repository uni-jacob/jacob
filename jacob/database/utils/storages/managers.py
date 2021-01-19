"""Описание менеджеров хранилищ."""
from pony import orm

from jacob.database import models
from jacob.database.utils.storages import base
from jacob.services.exceptions import BotStateNotFound


class AdminConfigManager(base.BaseStorageManager):
    """Менеджер хранилища конфигов админа."""

    def __init__(self, admin: models.Admin):
        """Создаёт объект менеджера хранилища.

        Args:
            admin: объект администратора
        """
        super().__init__(admin)
        self.model = models.AdminConfig


class MentionStorageManager(base.BaseStorageManager):
    """Менеджер хранилища призыва."""

    def __init__(self, admin: models.Admin):
        """Создаёт объект менеджера хранилища.

        Args:
            admin: объект администратора
        """
        super().__init__(admin)
        self.model = models.MentionStorage

    @orm.db_session
    def get_text(self) -> str:
        """Получает текст Призыва.

        Returns:
            str: Текст Призыва
        """
        return self.get_or_create().mention_text

    @orm.db_session
    def update_text(self, new_text: str):
        """Обновляет текст Призыва.

        Args:
            new_text: Новый текст Призыва
        """
        self.update(mention_text=new_text)

    @orm.db_session
    def append_to_mentioned_students(self, new_item: int):
        """Добавляет элемент в конец список призываемых студентов.

        Args:
            new_item: Новый элемент списка
        """
        mentioned_students = self._get_mentioned_students()
        mentioned_students.append(new_item)
        self._update_mentioned_students(mentioned_students)

    @orm.db_session
    def remove_from_mentioned(self, item_to_remove: int):
        """Удаляет элемент из списка призыва.

        Args:
            item_to_remove: Элемент для удаления
        """
        mentioned_students = self._get_mentioned_students()
        mentioned_students.remove(item_to_remove)
        self._update_mentioned_students(mentioned_students)

    @orm.db_session
    def _get_mentioned_students(self) -> list:
        """Получает список призываемых студентов.

        Returns:
            list: Список призываемых студентов
        """
        storage = self.get_or_create()
        return list(map(int, storage.mentioned_students.split(",")))

    @orm.db_session
    def _update_mentioned_students(self, new_list: list):
        """Обновляет список призываемых студентов.

        Args:
            new_list: Новый список призываемых студентов
        """
        self.update(mentioned_students=",".join(map(str, new_list)))


class StateStorageManager(base.BaseStorageManager):
    """Менеджер хранилищ состояний."""

    def __init__(self, admin: models.Student):
        """Создаёт объект менеджера хранилища.

        Args:
            admin: объект администратора
        """
        super().__init__(admin)
        self.model = models.StateStorage

    @orm.db_session
    def get_id_of_state(self, description: str) -> int:
        """
        Возвращает идентификатор состояния бота по его описанию.

        Args:
            description: описание статуса бота

        Returns:
            int: идентфикатор статуса бота

        Raises:
            BotStateNotFound: если переданный статус бота не был найден в БД
        """
        state = self.model.get(description=description)
        if state is not None:
            return state.id
        raise BotStateNotFound('Статус "{0}" не существует'.format(description))


class ChatRegistrarConfigManager(base.BaseStorageManager):
    """Менеджер хранилища конфигов регистратора чатов."""

    def __init__(self, admin: models.Admin):
        """Создаёт объект менеджера хранилища.

        Args:
            admin: объект администратора
        """
        super().__init__(admin)
        self.model = models.ChatRegistrarConfig


class FinancialConfigManager(base.BaseStorageManager):
    """Менеджер хранилища финансовых конфигов."""

    def __init__(self, admin: models.Admin):
        """Создаёт объект менеджера хранилища.

        Args:
            admin: объект администратора
        """
        super().__init__(admin)
        self.model = models.FinancialConfig

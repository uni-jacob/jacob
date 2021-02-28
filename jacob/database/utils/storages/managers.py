"""Описание менеджеров хранилищ."""
from pony import orm

from jacob.database import models
from jacob.database.utils import admin as admin_utils
from jacob.database.utils import chats
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

    @orm.db_session
    def get_active_group(self) -> models.Group:
        """Получить объект активной группы администратора.

        Returns:
            Group: объект группы
        """
        if len(admin_utils.get_admin_feud(self.owner)) > 1:
            return self.get_or_create().active_group
        return models.Admin.get(student=self.owner).group

    def get_names_usage(self) -> bool:
        """Получает флаг использования имён.

        Returns:
            bool: использование имён
        """
        return self.get_or_create().names_usage

    def invert_names_usage(self) -> models.AdminConfig:
        """Шорткат, инвертирующий использование имён в Призыве.

        Returns:
            models.AdminConfig: объект хранилища администратора
        """
        state = not self.get_names_usage()
        return self.update(names_usage=state)

    @orm.db_session
    def get_active_chat(self) -> models.Chat:
        """Получает активный чат администратора.

        Returns:
            Chat: объект чата
        """
        # TODO: Что делать, если активный чат не выбран?
        active_chat = self.get_or_create().active_chat
        if active_chat is None:
            active_group = self.get_active_group()
            active_chat = chats.get_list_of_chats_by_group(active_group).random(1)[0]
            self.update(active_chat=active_chat)

        return active_chat


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
        mentioned_students = self.get_mentioned_students()
        mentioned_students.append(new_item)
        self.update_mentioned_students(mentioned_students)

    @orm.db_session
    def remove_from_mentioned(self, item_to_remove: int):
        """Удаляет элемент из списка призыва.

        Args:
            item_to_remove: Элемент для удаления
        """
        mentioned_students = self.get_mentioned_students()
        mentioned_students.remove(item_to_remove)
        self.update_mentioned_students(mentioned_students)

    @orm.db_session
    def get_mentioned_students(self) -> list:
        """Получает список призываемых студентов.

        Returns:
            list: Список призываемых студентов
        """
        storage = self.get_or_create()
        return list(map(int, filter(bool, storage.mentioned_students.split(","))))

    @orm.db_session
    def update_mentioned_students(self, new_list: list):
        """Обновляет список призываемых студентов.

        Args:
            new_list: Новый список призываемых студентов
        """
        self.update(mentioned_students=",".join(map(str, new_list)))

    def get_attaches(self) -> str:
        """Получает список вложений.

        Returns:
            str: Список вложений
        """
        return self.get_or_create().mention_attaches

    def update_attaches(self, new_attaches: list):
        """Обновляет список вложений.

        Args:
            new_attaches: Новый список вложений

        Returns:
            orm.Database().Entity: объект хранилища MentionStorage
        """
        return self.update(mention_attaches=",".join(new_attaches))

    def clear(self):
        """Очищает хранилище Призыва.

        Returns:
            orm.Database().Entity: объект хранилища MentionStorage
        """
        self.update_mentioned_students([])
        self.update_attaches([])
        return self.update_text("")


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
        state = models.State.get(description=description)
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

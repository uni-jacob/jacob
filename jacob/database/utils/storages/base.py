"""Описание базового менеджера хранилищ."""


from pony import orm

from jacob.database import models


class BaseStorageManager(object):
    """Базовый менеджер хранилищ."""

    def __init__(self, admin: models.Admin):
        """Создаёт объект менеджера хранилищ.

        Args:
            admin: объект администратора
        """
        self.model = None
        self.admin = admin

    @orm.db_session
    def get_or_create(self) -> orm.Database().Entity:
        """Получает существующий или создаёт новый объект хранилища.

        Returns:
            orm.Database().Entity: Объект хранилища
        """
        storage = self.model.get()

        if storage is None:
            storage = self.model(admin=self.admin)

        return storage

    @orm.db_session
    def update(self, **kwargs) -> orm.Database().Entity:
        """Обновляет поля хранилища.

        Args:
            **kwargs: Поля для обновления

        Returns:
            orm.Database().Entity: Объект хранилища
        """
        storage = self.get_or_create()
        storage.set(**kwargs)

        return storage

from .base import Base


class Database(Base):
    async def get_ownership_of_admin(self, user_id: int) -> int:
        """
        Получает информацию об учебном заведении и группе, к которым имеет доступ
        администратор с указанным идентификатором ВК

        Args:
            user_id: Идентификатор пользователя

        Returns:
            int: Идентификатор группы, в которой указанный пользователь
            является администратором
        """
        query = await self.query(
            "select id from students where vk_id=$1", user_id, fetchone=True,
        )
        data = await self.query(
            "select group_id from administrators where id=$1",
            query["id"],
            fetchone=True,
        )

        return data["group_id"]

    async def get_unique_second_name_letters(self, user_id: int) -> list:
        """
        Получает список первых букв фамилий студентов

        Args:
            user_id: Идентификатор администратора

        Returns:
            list[str]: Список первых букв фамилий
        """
        data = await self.get_ownership_of_admin(user_id)
        query = await self.query(
            "SELECT DISTINCT substring(second_name from  '^.') FROM students where "
            "group_id=$1 ORDER BY substring(second_name from  '^.')",
            data,
            fetchall=True,
        )
        return [letter for (letter,) in iter(query)]

    async def get_list_of_names(self, letter: str, user_id: int) -> list:
        """
        Получает список студентов, фамилии которых начинаются на letter

        Args:
            letter: Первая буква фамилий для поиска
            user_id: Идентификатор администратора

        Returns:
            List[Record]: Информация о студентах (ид, имя, фамилия), пододящих под
            фильтр
        """
        data = await self.get_ownership_of_admin(user_id)
        names = await self.query(
            "SELECT id, first_name, second_name FROM students "
            "WHERE substring(second_name from '^.') = $1 "
            "AND academic_status > 0 AND group_id=$2 ORDER BY id",
            letter,
            data,
            fetchall=True,
        )
        return names

    async def get_active_students(self, user_id: int):
        """
        Получает список студентов группы, чей академический статус больше нуля

        Args:
            user_id: Идентификатор администратора

        Returns:
            list[Record]: Список объектов активных студентов группы
        """
        data = await self.get_ownership_of_admin(user_id)
        names = await self.query(
            "SELECT id, first_name, second_name FROM students "
            "WHERE academic_status > 0 AND group_id=$1 ORDER BY id",
            data,
            fetchall=True,
        )
        return names

    async def get_list_of_chats(self, user_id: int):
        """
        Получает список настроенных чатов для группы, администратором которой
        является user_id
        Args:
            user_id: Идентификатор пользователя

        Returns:
            list[Records]: Список с данными о чатах
        """
        data = await self.get_ownership_of_admin(user_id)
        chats = await self.query(
            "SELECT chat_id, group_id, chat_type, is_active from chats where "
            "group_id=$1",
            data,
            fetchall=True,
        )
        return chats

    async def get_cached_chats(self):
        """
        Получает список кэшированных чатов
        Returns:
            list[Record]: Список чатов
        """
        chats = await self.query("select chat_id from cached_chats", fetchall=True)
        return chats

    async def is_chat_registered(self, user_id: int, chat_type: int):
        """
        Был ли зарегистрирован чат с указанным типом
        Args:
            user_id: Идентификатор пользователя
            chat_type: Тип чата
        Returns:
            bool: Наличие зарегистрированного чата
        """
        data = await self.get_ownership_of_admin(user_id)
        query = await self.query(
            "select * from chats where group_id=$1 and chat_type=$3",
            data,
            chat_type,
            fetchone=True,
        )
        return bool(query)

    async def get_chat_types(self):
        """
        Возвращает доступные типы чатов
        Returns:
            list[Record]: Типы чатов
        """

        data = self.query("select * from chat_types", fetchall=True)

        return data

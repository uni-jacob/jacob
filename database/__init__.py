from .base import Base


class Database(Base):
    async def get_ownership_of_admin(self, user_id: int):
        """
        Получает информацию об учебном заведении и группе, к которым имеет доступ
        администратор с указанным идентификатором ВК

        Todo:
            Что если пользователь администратор не одной группы?
            (В теории это возможно...)

        Args:
            user_id: Идентификатор пользователя

        Returns:
            Record: Информация об администраторе (первая существующая запись)
        """
        data = await self.query(
            "select alma_mater_id, group_id from administrators where vk_id=$1",
            user_id,
            fetchone=True,
        )
        return data

    async def get_unique_second_name_letters(self, user_id: int):
        """
        Получает список первых букв фамилий студентов

        Args:
            user_id: Идентификатор администратора

        Returns:
            list: Список первых букв фамилий
        """
        data = await self.get_ownership_of_admin(user_id)
        query = await self.query(
            "SELECT DISTINCT substring(second_name from  '^.') FROM students where "
            "alma_mater_id=$1 and group_id=$2 ORDER BY substring(second_name from  "
            "'^.')",
            data["alma_mater_id"],
            data["group_id"],
            fetchall=True,
        )
        return [letter for (letter,) in iter(query)]

    async def get_list_of_names(self, letter: str, user_id: int):
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
            "AND academic_status > 0 AND alma_mater_id=$2 AND group_id=$3 ORDER BY "
            "id",
            letter,
            data["alma_mater_id"],
            data["group_id"],
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
            "WHERE academic_status > 0 AND alma_mater_id=$1 AND group_id=$2 ORDER BY id",
            data["alma_mater_id"],
            data["group_id"],
            fetchall=True,
        )
        return names

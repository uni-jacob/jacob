from .base import Base


class Database(Base):
    async def get_unique_second_name_letters(self, user_id: int):
        """
        Получает список первых букв фамилий студентов

        Args:
            user_id: Идентификатор администратора

        Returns:
            list: Список первых букв фамилий
        """
        data = await self.query(
            "select alma_mater_id, group_id from administrators where vk_id=$1",
            user_id,
            fetchone=True,
        )
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
            List[tuple]: Информация о студентах (ид, имя, фамилия), пододящих под фильтр
        """
        data = await self.query(
            "select alma_mater_id, group_id from administrators where vk_id=$1",
            user_id,
            fetchone=True,
        )
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

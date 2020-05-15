from .base import Base


class Database(Base):
    def get_unique_second_name_letters(self, user_id: int):
        """
        Получает список первых букв фамилий студентов

        Args:
            user_id: Идентификатор администратора

        Returns:
            list: Список первых букв фамилий
        """
        data = self.query(
            "select alma_mater_id, group_id from administrators where vk_id=%s",
            (user_id,),
            fetchone=True,
        )
        query = self.query(
            "SELECT DISTINCT substring(second_name from  '^.') FROM students where "
            "alma_mater_id = %s and group_id=%s ORDER BY substring(second_name from  "
            "'^.')",
            (data[0], data[1]),
        )
        return [letter for (letter,) in query]

    def get_list_of_names(self, letter: str, user_id: int):
        """
        Получает список студентов, фамилии которых начинаются на letter

        Args:
            letter: Первая буква фамилий для поиска
            user_id: Идентификатор администратора

        Returns:
            List[tuple]: Информация о студентах (ид, имя, фамилия), пододящих под фильтр
        """
        data = self.query(
            "select alma_mater_id, group_id from administrators where vk_id=%s",
            (user_id,),
            fetchone=True,
        )
        names = self.query(
            "SELECT id, first_name, second_name FROM students "
            "WHERE substring(second_name from '^.') = %s "
            "AND academic_status > 0 AND alma_mater_id=%s AND group_id=%s ORDER BY "
            "id",
            (letter, data[0], data[1]),
        )
        return names

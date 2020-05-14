from .base import Base


class Database(Base):
    def is_admin(self, user_id: int):
        """
        Проверяет наличие прав администратора (любого заведения/группы) у выбранного
        пользователя
        Args:
            user_id: Идентификатор пользователя

        Returns:
            bool: Статус администратора
        """

        query = self.query(
            "select * from administrators where vk_id=%s", (user_id,), fetchone=True
        )
        return bool(query)

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

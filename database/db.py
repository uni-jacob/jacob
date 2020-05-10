from . import Base


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

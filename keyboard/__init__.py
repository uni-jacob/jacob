from vkbottle.keyboard import Keyboard, Text


class Keyboards:
    @staticmethod
    def main_menu() -> str:
        """
        Генерирует клавиатуру главного меню
        Returns:
            JSON-like str: Строка с клавиатурой

        """
        kb = Keyboard()
        kb.add_row()
        kb.add_button(Text(label="Призыв", payload={"button": "call"}))
        kb.add_button(Text(label="Финансы", payload={"button": "finances"}))
        return kb.generate()

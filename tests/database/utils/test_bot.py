import pytest
from pyexpect import expect

from jacob.database.utils import bot
from jacob.services.exceptions import BotStateNotFound


class TestBot:
    def test_get_id_of_state(self):

        test_description = "mention_wait_text"

        state = bot.get_id_of_state(test_description)

        expect(state).is_equal(12)

    def test_get_id_of_non_existing_state(self):

        test_description = "qwerty"

        with pytest.raises(BotStateNotFound):
            bot.get_id_of_state(test_description)

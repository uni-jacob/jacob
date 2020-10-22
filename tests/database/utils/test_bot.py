import pytest
from pyshould import it

from database.utils import bot
from services.exceptions import BotStateNotFound


class TestBot:
    def test_get_id_of_state(self):

        test_description = "wait_call_text"

        state = bot.get_id_of_state(test_description)

        it(state).should.be_equal(5)

    def test_get_id_of_non_existing_state(self):

        test_description = "qwerty"

        with pytest.raises(BotStateNotFound):
            bot.get_id_of_state(test_description)

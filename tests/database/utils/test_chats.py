from pyshould import it

from database.utils import chats


class TestChats:

    def test_is_chat_registered(self):

        test_user_id = 549350532

        res = chats.is_chat_registered(test_user_id, 1)

        it(res).should.be_equal(True)

    def test_is_chat_registered_with_non_registered_chat(self):

        test_user_id = 465767

        res = chats.is_chat_registered(test_user_id, 1)

        it(res).should.be_equal(False)

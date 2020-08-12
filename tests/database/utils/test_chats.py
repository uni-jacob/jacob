from pyshould import it

from database.utils import chats


class TestChats:
    def test_get_cached_chats(self):
        from database.models import CachedChat

        test_cached_chat = CachedChat.get(id=1)

        cache = chats.get_cached_chats()
        it(cache).should.be_equal([test_cached_chat])

    def test_is_chat_registered(self):

        test_user_id = 549350532

        res = chats.is_chat_registered(test_user_id, 1)

        it(res).should.be_equal(True)

from pyshould import it

from services import call


class TestCall:
    def test_generate_mentions_with_sep(self):

        res = call.generate_mentions(students="2,3", names_usage=True)

        it(res).should.be_equal("@id199901833 (Сабина), @id255208457 (Алексей)")

    def test_generate_mentions_without_sep(self):
        res = call.generate_mentions(students="2,3", names_usage=False)

        it(res).should.be_equal("@id199901833 (!)@id255208457 (!)")

    def test_generate_message(self):
        test_admin_id = 1

        res = call.generate_message(test_admin_id)

        it(res).should.be_equal(
            "@id549350532 (!)@id199901833 (!)@id255208457 (!)\nTest"
        )

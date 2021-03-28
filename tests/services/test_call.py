from pyexpect import expect

from jacob.services import call


class TestCall:
    def test_generate_mentions_with_sep(self):

        res = call.generate_mentions(students=[26, 27], names_usage=True)

        expect(res).is_equal("@id199901833 (Сабина), @id255208457 (Алексей)")

    def test_generate_mentions_without_sep(self):
        res = call.generate_mentions(students=[26, 27], names_usage=False)

        expect(res).is_equal("@id199901833 (!)@id255208457 (!)")

    def test_generate_message(self):
        test_admin_id = 47

        res = call.generate_message(test_admin_id)

        expect(res).is_equal("@id549350532 (!)@id199901833 (!)@id255208457 (!)\nTest")

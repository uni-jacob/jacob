from pyshould import it

from services import call


class TestCall:
    def test_generate_mentions_with_sep(self):
        res = call.generate_mentions(students="2,3", names_usage=True)

        it(res).should.be_equal("@id446545 (fgrgrf), @id465767 (fhfgbv)")

    def test_generate_mentions_without_sep(self):
        res = call.generate_mentions(students="2,3", names_usage=False)

        it(res).should.be_equal("@id446545 (!)@id465767 (!)")

    def test_generate_message(self):
        test_admin_id = 1

        res = call.generate_message(test_admin_id)

        it(res).should.be_equal("@id549350532 (!)@id446545 (!)@id465767 (!)\nTest")

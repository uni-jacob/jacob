from pyshould import it

from jacob.services.media import translate_string


class TestMedia:
    def test_translate_string_en2ru(self):
        string = "ghbdtn"

        res = translate_string(string)

        it(res).should.be_equal("привет")

    def test_translate_string_ru2en(self):
        string = "руддщ"

        res = translate_string(string)

        it(res).should.be_equal("hello")

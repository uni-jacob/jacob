from jacob.services.common import generate_abbreviation


def test_generate_abbreviation():
    phrase = "Владимирский государственный университет"
    assert generate_abbreviation(phrase) == "ВГУ"

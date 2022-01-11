import json


def assert_cassette_empty(cass):
    assert len(cass) == 0
    assert cass.play_count == 0


def assert_cassette_has_one_response(cass):
    assert len(cass) == 1
    assert cass.play_count == 1


def assert_is_json(a_string):
    try:
        json.loads(a_string.decode("utf-8"))
    except Exception:
        assert False
    assert True

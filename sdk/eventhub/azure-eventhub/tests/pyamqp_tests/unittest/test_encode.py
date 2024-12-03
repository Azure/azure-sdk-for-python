import pytest
from azure.eventhub._pyamqp._encode import encode_filter_set


@pytest.mark.parametrize(
    "value,expected",
    [
        ({b"com.microsoft:session-filter": "ababa"}, "ababa"),
        ({b"com.microsoft:session-filter": "abab"}, "abab"),
        ({b"com.microsoft:session-filter": "aba"}, "aba"),
        ({b"com.microsoft:session-filter": "ab"}, "ab"),
        ({b"com.microsoft:session-filter": "a"}, "a"),
        ({b"com.microsoft:session-filter": 1}, 1),
    ],
)
def test_valid_filter_encode(value, expected):
    fields = encode_filter_set(value)
    assert len(fields) == 2
    assert fields["VALUE"][0][1] == expected

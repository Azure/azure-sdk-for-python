import pytest
from azure.eventhub._pyamqp._encode import encode_filter_set, encode_unknown
from decimal import Decimal

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


@pytest.mark.parametrize(
        "value, expected",
        [
            (Decimal("3.14"), b'\x940<\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01:'),
            (Decimal((1, (3, 1, 4), -2)), b'\x94\xb0<\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01:'),
            (Decimal("0.1"), b'\x940>\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'),
            (Decimal("33802.4489"), b'\x9408\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14%\xd8)'),
        ]
)
def test_decimal_encode(value, expected):
    output = bytearray()
    encode_unknown(output, value)
    assert bytes(output) == expected

import pytest
from azure.eventhub._pyamqp._decode import _decode_decimal128
from decimal import Decimal



@pytest.mark.parametrize(
    "value,expected",
    [
        (b'\x0c>\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"\xa1', Decimal("3.4")),
        (b'\x0c6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x86\xb9\xa1', Decimal(".34489")),
        (b'\x0c@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\xa1', Decimal("10")),
        (b'\x0c8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14%\xd8)\xa1', Decimal("33802.4489")),
    ]
)
def test_decimal_decode(value, expected):
    output = _decode_decimal128(memoryview(value))
    assert output[1] == expected



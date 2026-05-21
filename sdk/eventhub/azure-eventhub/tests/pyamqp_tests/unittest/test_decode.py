import pytest
from azure.eventhub._pyamqp._decode import _decode_decimal128, _decode_described, _decode_array_small, _decode_array_large
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


def test_described():
    value = b"\x80\0\0\x017\0\0\x07\xd3\xd0\0\0\0\x12\0\0\0\x02\xa1\ntest/topicP\0"
    buffer, output = _decode_described(memoryview(value))
    assert output.descriptor == 1335734831059
    assert output == [b'test/topic', 0]


def test_array_of_described():
    value = b"\0\x03\0\x80\0\0\x017\0\0\x07\xd4\xd0\0\0\0\x0c\0\0\0\x02\xa1\x02n1\xa1\x02v1\0\0\0\x0c\0\0\0\x02\xa1\x02n2\xa1\x02v2\0\0\0\n\0\0\0\x02\xa1\x02n1\xa1\0"

    buffer, output = _decode_array_small(memoryview(value))
    assert output == [[b'n1', b'v1'], [b'n2', b'v2'], [b'n1', b'']]
    assert output[0].descriptor == 1335734831060
    assert output[1].descriptor == 1335734831060
    assert output[2].descriptor == 1335734831060


def test_array_of_described_large():
    value = b"\0\0\x0e\x0f\0\0\x01\0\0\x80\0\0\x017\0\0\x07\xd4\xd0"
    for i in range(256):
        value += b"\0\0\0\n\0\0\0\x02\xa1\x01n\xa1\x01v"

    buffer, output = _decode_array_large(memoryview(value))
    assert len(output) == 256
    for i in range(256):
        assert output[i] == [b'n', b'v']
        assert output[i].descriptor == 1335734831060

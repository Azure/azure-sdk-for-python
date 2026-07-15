import pytest
from azure.eventhub._pyamqp._decode import (
    _decode_decimal128,
    _decode_described,
    _decode_array_small,
    _decode_array_large,
    decode_frame,
    _PERFORMATIVE_FIELD_COUNT,
)
from azure.eventhub._pyamqp import performatives
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


def _list8_frame(code, count, encoded_fields, payload=b""):
    # Build a described performative frame using a list8 (0xc0) body:
    # described-type ctor (0x00), ulong ctor (0x53), descriptor code, list8 (0xc0),
    # size, count, then the encoded field bytes and any trailing payload.
    header = bytes([0x00, 0x53, code, 0xC0, len(encoded_fields) + 1, count])
    return memoryview(header + encoded_fields + payload)


# A sender may omit trailing null fields (AMQP 1.0 section 1.4), so an incoming
# performative list can be shorter than the full field count. The decoder must
# pad it back to the full count so positional access and namedtuple unpacking
# stay safe and omitted fields read back as None.
def test_short_open_is_padded_to_full_field_count():
    # Open with only container_id set ("x"), 1 field on the wire out of 10.
    frame = _list8_frame(performatives.OpenFrame._code, 1, bytes([0xA1, 0x01, 0x78]))
    frame_type, fields = decode_frame(frame)
    assert frame_type == performatives.OpenFrame._code
    assert len(fields) == 10
    # Unpacking and fixed-index access must not raise on the omitted fields.
    open_frame = performatives.OpenFrame(*fields)
    assert open_frame.container_id == b"x"
    assert open_frame.properties is None
    assert fields[9] is None


def test_short_transfer_pads_fields_and_preserves_payload():
    # Transfer with only handle (0) set, plus a message payload. The payload is
    # appended after the fields and must survive the padding.
    frame = _list8_frame(performatives.TransferFrame._code, 1, bytes([0x52, 0x00]), payload=b"\xde\xad")
    frame_type, fields = decode_frame(frame)
    assert frame_type == performatives.TransferFrame._code
    # 11 wire fields padded out, then the trailing payload appended (12 total).
    assert len(fields) == 12
    transfer = performatives.TransferFrame(*fields)
    assert transfer.handle == 0
    assert transfer.batchable is None
    assert bytes(transfer.payload) == b"\xde\xad"


def _list0_frame(code):
    # Build a described performative whose body is an AMQP list0 (0x45): the most
    # compact "all fields omitted" encoding, carrying no size or count bytes.
    # described-type ctor (0x00), ulong ctor (0x53), descriptor code, list0 (0x45).
    return memoryview(bytes([0x00, 0x53, code, 0x45]))


# A performative with every field omitted may arrive as a list0 (0x45) body,
# which has no count byte. The decoder must treat it as zero fields and pad up
# to the full field count instead of indexing past the end of the buffer.
@pytest.mark.parametrize("frame_cls", [performatives.EndFrame, performatives.CloseFrame])
def test_list0_performative_pads_to_full_field_count(frame_cls):
    frame = _list0_frame(frame_cls._code)
    frame_type, fields = decode_frame(frame)
    assert frame_type == frame_cls._code
    assert len(fields) == _PERFORMATIVE_FIELD_COUNT[frame_cls._code]
    # Every omitted field reads back as None and unpacking must not raise.
    performative = frame_cls(*fields)
    assert performative.error is None


@pytest.mark.parametrize(
    "frame_cls,expected_count",
    [
        (performatives.OpenFrame, 10),
        (performatives.BeginFrame, 8),
        (performatives.AttachFrame, 14),
        (performatives.FlowFrame, 11),
        (performatives.TransferFrame, 11),
        (performatives.DispositionFrame, 6),
        (performatives.DetachFrame, 3),
        (performatives.EndFrame, 1),
        (performatives.CloseFrame, 1),
    ],
)
def test_performative_field_count_matches_spec(frame_cls, expected_count):
    # The padding target is the number of wire fields defined for each
    # performative (the trailing transfer payload slot is excluded).
    assert _PERFORMATIVE_FIELD_COUNT[frame_cls._code] == expected_count

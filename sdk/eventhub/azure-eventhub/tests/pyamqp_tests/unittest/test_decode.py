import pathlib
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


# A sender may omit trailing fields whose value is the default (AMQP 1.0 section
# 1.4), so an incoming performative list can be shorter than the full field
# count. The decoder must pad it back to the full count so positional access and
# namedtuple unpacking stay safe and omitted fields read back as their default.
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


def test_short_open_materializes_non_null_field_defaults():
    # An Open that omits max_frame_size/channel_max means their AMQP defaults,
    # not null. _connection._incoming_open reads them positionally and numerically
    # (frame[2] < 512, frame[3]); padding with None would raise TypeError there.
    frame = _list8_frame(performatives.OpenFrame._code, 1, bytes([0xA1, 0x01, 0x78]))
    _, fields = decode_frame(frame)
    assert fields[2] == 4294967295  # max_frame_size default
    assert fields[3] == 65535  # channel_max default
    # Exercise the exact comparison _incoming_open performs; must not raise.
    assert not fields[2] < 512
    open_frame = performatives.OpenFrame(*fields)
    assert open_frame.max_frame_size == 4294967295
    assert open_frame.channel_max == 65535


def test_open_with_explicit_null_field_uses_default():
    # Only trailing fields may be omitted, so an Open that sets a later field
    # (channel_max) while wanting the default max_frame_size must encode
    # max_frame_size as an explicit null. That null must still read back as the
    # 4294967295 default, or _incoming_open's frame[2] < 512 raises TypeError.
    # container_id="x", hostname=null, max_frame_size=null, channel_max=100.
    frame = _list8_frame(
        performatives.OpenFrame._code, 4, bytes([0xA1, 0x01, 0x78, 0x40, 0x40, 0x52, 0x64])
    )
    _, fields = decode_frame(frame)
    assert fields[2] == 4294967295  # explicit null normalized to the default
    assert not fields[2] < 512  # the comparison _incoming_open performs
    assert fields[3] == 100  # the explicitly set later field is preserved
    assert fields[1] is None  # a null-default field (hostname) stays None
    open_frame = performatives.OpenFrame(*fields)
    assert open_frame.max_frame_size == 4294967295
    assert open_frame.channel_max == 100


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
    # Omitted boolean/uint fields read back as their AMQP defaults, not None.
    assert transfer.message_format == 0
    assert transfer.batchable is False
    assert bytes(transfer.payload) == b"\xde\xad"


def _list0_frame(code):
    # Build a described performative whose body is an AMQP list0 (0x45): the most
    # compact "all fields omitted" encoding, carrying no size or count bytes.
    # described-type ctor (0x00), ulong ctor (0x53), descriptor code, list0 (0x45).
    return memoryview(bytes([0x00, 0x53, code, 0x45]))


def _list32_frame(code, count, encoded_fields, payload=b""):
    # Build a described performative frame using a list32 (0xd0) body, whose size
    # and count are 4-byte big-endian. decode_frame ignores the size field and
    # reads the count from data[8:12], so only the count must be accurate.
    size = (len(encoded_fields) + 4).to_bytes(4, "big")
    header = bytes([0x00, 0x53, code, 0xD0]) + size + count.to_bytes(4, "big")
    return memoryview(header + encoded_fields + payload)


# Begin/Attach/Disposition/Detach are namedtuples with no field defaults, so a
# short positional unpack raised TypeError before the decoder padded to the full
# field count. Only Open was covered above; exercise the rest of the no-default
# performatives directly.
@pytest.mark.parametrize(
    "frame_cls",
    [
        performatives.AttachFrame,
        performatives.BeginFrame,
        performatives.DispositionFrame,
        performatives.DetachFrame,
    ],
)
def test_short_no_default_performative_is_padded(frame_cls):
    # Each field's AMQP default, in wire order (the transfer payload sentinel
    # is excluded, but these performatives have none).
    defaults = [f.default for f in frame_cls._definition if f is not None]  # pylint: disable=protected-access
    # A single null field on the wire, the rest omitted.
    frame = _list8_frame(frame_cls._code, 1, bytes([0x40]))
    frame_type, fields = decode_frame(frame)
    assert frame_type == frame_cls._code
    assert len(fields) == len(defaults)
    # The one wire field decoded as an explicit null; the omitted trailing fields
    # are padded with their defaults (e.g. Disposition.batchable is False).
    assert fields[0] is None
    assert fields[1:] == defaults[1:]
    # Namedtuple construction must not raise on the omitted (now padded) fields.
    frame_cls(*fields)


# The list32 (0xd0) body path is only taken for large frames and is otherwise
# unexercised; confirm a short performative encoded as list32 pads identically to
# the list8 case.
def test_short_list32_is_padded_to_full_field_count():
    frame = _list32_frame(performatives.OpenFrame._code, 1, bytes([0xA1, 0x01, 0x78]))
    frame_type, fields = decode_frame(frame)
    assert frame_type == performatives.OpenFrame._code
    assert len(fields) == 10
    open_frame = performatives.OpenFrame(*fields)
    assert open_frame.container_id == b"x"
    assert fields[9] is None


# SASLInit/SASLOutcome have required (no-default) fields, so a short SASL frame
# crashed pre-fix. They are in the field-count map and must pad too.
@pytest.mark.parametrize("frame_cls", [performatives.SASLInit, performatives.SASLOutcome])
def test_short_sasl_frame_is_padded(frame_cls):
    full_field_count = _PERFORMATIVE_FIELD_COUNT[frame_cls._code]
    frame = _list8_frame(frame_cls._code, 1, bytes([0x40]))
    frame_type, fields = decode_frame(frame)
    assert frame_type == frame_cls._code
    assert len(fields) == full_field_count
    assert fields[-1] is None
    frame_cls(*fields)


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


# The _pyamqp engine is vendored identically into azure-eventhub and
# azure-servicebus; a fix (like the padding above) must be applied to both
# copies. Guard against the two copies silently drifting apart. The packages
# ship separately, so skip when the sibling source is not present rather than
# fail on a package-isolated checkout.
_PYAMQP_COPIES = (
    "sdk/eventhub/azure-eventhub/azure/eventhub/_pyamqp",
    "sdk/servicebus/azure-servicebus/azure/servicebus/_pyamqp",
)


def _repo_root():
    for parent in pathlib.Path(__file__).resolve().parents:
        if (parent / "sdk").is_dir():
            return parent
    return None


@pytest.mark.parametrize("filename", ["_decode.py", "_encode.py", "performatives.py"])
def test_pyamqp_copies_are_byte_identical(filename):
    root = _repo_root()
    assert root is not None, "could not locate the repo root (no ancestor contains sdk/)"
    eventhub_copy = root / _PYAMQP_COPIES[0] / filename
    servicebus_copy = root / _PYAMQP_COPIES[1] / filename
    if not (eventhub_copy.exists() and servicebus_copy.exists()):
        pytest.skip("both _pyamqp copies are not present in this checkout")
    assert (
        eventhub_copy.read_bytes() == servicebus_copy.read_bytes()
    ), f"{filename} has drifted between the eventhub and servicebus _pyamqp copies; apply to both."

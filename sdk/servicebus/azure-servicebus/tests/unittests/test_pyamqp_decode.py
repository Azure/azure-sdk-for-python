import pytest
from azure.servicebus._pyamqp._decode import decode_frame, _PERFORMATIVE_FIELD_COUNT
from azure.servicebus._pyamqp import performatives


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

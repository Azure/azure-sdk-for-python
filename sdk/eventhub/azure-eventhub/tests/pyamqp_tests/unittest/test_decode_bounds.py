import pytest

from azure.eventhub._pyamqp._decode import (
    _decode_array_large,
    _decode_list_large,
    _decode_map_large,
    _decode_map_small,
    decode_frame,
    _MAX_COMPOUND_COUNT,
    _MAX_NESTING_DEPTH,
    _DECODE_BY_CONSTRUCTOR,
)


def _header(count: int) -> bytes:
    # 4 bytes size (unused by the decoder beyond slicing) + 4 bytes big-endian count
    return b"\x00\x00\x00\x00" + count.to_bytes(4, "big")


HUGE_COUNT = 0x7FFFFFFF
JUST_OVER = _MAX_COMPOUND_COUNT + 1


@pytest.mark.parametrize("count", [HUGE_COUNT, JUST_OVER])
def test_decode_array_large_rejects_oversized_count(count):
    buffer = memoryview(_header(count))
    with pytest.raises(ValueError, match="exceeds maximum"):
        _decode_array_large(buffer)


@pytest.mark.parametrize("count", [HUGE_COUNT, JUST_OVER])
def test_decode_list_large_rejects_oversized_count(count):
    buffer = memoryview(_header(count))
    with pytest.raises(ValueError, match="exceeds maximum"):
        _decode_list_large(buffer)


@pytest.mark.parametrize("count", [HUGE_COUNT, JUST_OVER])
def test_decode_map_large_rejects_oversized_count(count):
    buffer = memoryview(_header(count))
    with pytest.raises(ValueError, match="exceeds maximum"):
        _decode_map_large(buffer)


def test_decode_array_large_accepts_boundary():
    # COUNT exactly at the cap with a null subconstructor (0x40). _decode_null
    # consumes no bytes, so the result is a list of _MAX_COMPOUND_COUNT Nones.
    buffer = memoryview(_header(_MAX_COMPOUND_COUNT) + b"\x40")
    remaining, values = _decode_array_large(buffer)
    assert len(values) == _MAX_COMPOUND_COUNT
    assert all(v is None for v in values)
    assert bytes(remaining) == b""


def test_decode_list_large_accepts_boundary():
    # Each element carries its own constructor byte; _MAX_COMPOUND_COUNT nulls.
    body = b"\x40" * _MAX_COMPOUND_COUNT
    buffer = memoryview(_header(_MAX_COMPOUND_COUNT) + body)
    remaining, values = _decode_list_large(buffer)
    assert len(values) == _MAX_COMPOUND_COUNT
    assert all(v is None for v in values)
    assert bytes(remaining) == b""


def test_decode_map_large_accepts_boundary():
    # COUNT counts entries (keys + values); pairs = count // 2.
    body = b"\x40" * _MAX_COMPOUND_COUNT
    buffer = memoryview(_header(_MAX_COMPOUND_COUNT) + body)
    remaining, values = _decode_map_large(buffer)
    # All keys collapse to None, so the dict has a single entry.
    assert values == {None: None}
    assert bytes(remaining) == b""


def _frame_list32(count: int) -> bytes:
    # decode_frame skips data[0:2] (described/ulong constructors), reads
    # frame_type at data[2], the compound marker at data[3], size at
    # data[4:8], and the COUNT under test at data[8:12].
    return b"\x00\x53\x00\xd0" + b"\x00\x00\x00\x00" + count.to_bytes(4, "big")


@pytest.mark.parametrize("count", [HUGE_COUNT, JUST_OVER])
def test_decode_frame_rejects_oversized_list32_count(count):
    buffer = memoryview(_frame_list32(count))
    with pytest.raises(ValueError, match="exceeds maximum"):
        decode_frame(buffer)


def test_decode_map_large_rejects_odd_count():
    # An odd raw COUNT would silently floor to pairs = (count - 1) // 2 and
    # leave a trailing key with no value, corrupting subsequent decoding.
    buffer = memoryview(_header(3))
    with pytest.raises(ValueError, match="must be even"):
        _decode_map_large(buffer)


def test_decode_map_small_rejects_odd_count():
    # _decode_map_small reads the COUNT from buffer[1] (1 byte, 0-255). An
    # odd value has the same trailing-key problem as the large variant.
    buffer = memoryview(b"\x00\x03")
    with pytest.raises(ValueError, match="must be even"):
        _decode_map_small(buffer)


def _nested_list(levels: int) -> bytes:
    # list32 with correct size/count so the payload is valid even if size is ever enforced.
    payload = b"\x40"
    for _ in range(levels):
        body = b"\x00\x00\x00\x01" + payload
        payload = b"\xd0" + len(body).to_bytes(4, "big") + body
    return payload


def _nested_map(levels: int) -> bytes:
    payload = b"\x40"
    for _ in range(levels):
        body = b"\x00\x00\x00\x02" + b"\x40" + payload
        payload = b"\xd1" + len(body).to_bytes(4, "big") + body
    return payload


def _nested_array(levels: int) -> bytes:
    payload = b"\xf0" + (5).to_bytes(4, "big") + b"\x00\x00\x00\x01\x40"
    for _ in range(levels - 1):
        body = b"\x00\x00\x00\x01" + b"\xf0" + payload[1:]
        payload = b"\xf0" + len(body).to_bytes(4, "big") + body
    return payload


def _nested_described(levels: int) -> bytes:
    return b"\x00\x53\x00" * levels + b"\x40"


def _nested_mixed(levels: int) -> bytes:
    # alternate list/map/described so one chain exercises multiple decoders.
    payload = b"\x40"
    wrappers = (
        lambda p: b"\xd0" + len(b"\x00\x00\x00\x01" + p).to_bytes(4, "big") + b"\x00\x00\x00\x01" + p,
        lambda p: b"\xd1" + len(b"\x00\x00\x00\x02\x40" + p).to_bytes(4, "big") + b"\x00\x00\x00\x02\x40" + p,
        lambda p: b"\x00\x53\x00" + p,
    )
    for i in range(levels):
        payload = wrappers[i % 3](payload)
    return payload


def _decode(payload: bytes):
    return _DECODE_BY_CONSTRUCTOR[payload[0]](memoryview(payload)[1:])


def _nested_list8(levels: int) -> bytes:
    # list8 (compact) wrappers; the size byte is ignored by the decoder so 0x00 is fine.
    payload = b"\x40"
    for _ in range(levels):
        payload = b"\xc0\x00\x01" + payload
    return payload


def _nested_map8(levels: int) -> bytes:
    payload = b"\x40"
    for _ in range(levels):
        payload = b"\xc1\x00\x02\x40" + payload
    return payload


def _nested_array8(levels: int) -> bytes:
    body = b"\x00\x01\x40"
    for _ in range(levels - 1):
        body = b"\x00\x01\xe0" + body
    return b"\xe0" + body


_BOMBS = [
    _nested_list,
    _nested_map,
    _nested_array,
    _nested_described,
    _nested_mixed,
    _nested_list8,
    _nested_map8,
    _nested_array8,
]


@pytest.mark.parametrize("bomb", _BOMBS)
def test_decode_rejects_excessive_nesting(bomb):
    with pytest.raises(ValueError, match="exceeds maximum depth"):
        _decode(bomb(_MAX_NESTING_DEPTH + 1))


@pytest.mark.parametrize("bomb", _BOMBS)
def test_decode_accepts_nesting_at_limit(bomb):
    _decode(bomb(_MAX_NESTING_DEPTH))


@pytest.mark.parametrize("bomb", _BOMBS)
def test_decode_resets_depth_after_rejection(bomb):
    # after a rejected bomb the depth counter must reset so a later decode still works.
    with pytest.raises(ValueError, match="exceeds maximum depth"):
        _decode(bomb(_MAX_NESTING_DEPTH + 1))
    remaining, value = _decode(b"\xc0\x05\x02\x50\x01\x50\x02")
    assert value == [1, 2]
    assert bytes(remaining) == b""


def test_decode_frame_rejects_deeply_nested_field():
    field = _nested_list(_MAX_NESTING_DEPTH + 1)
    data = b"\x00\x53\x00\xd0" + (len(field) + 4).to_bytes(4, "big") + b"\x00\x00\x00\x01" + field
    with pytest.raises(ValueError, match="exceeds maximum depth"):
        decode_frame(memoryview(data))


def test_decode_shallow_value_unchanged():
    remaining, value = _decode(_nested_list(2))
    assert value == [[None]]
    assert bytes(remaining) == b""


def _described_array_of(inner: bytes) -> bytes:
    body = (1).to_bytes(4, "big") + b"\x00" + b"\x53\x00" + inner[0:1] + inner[1:]
    return b"\xf0" + len(body).to_bytes(4, "big") + body


def _nested_described_array(levels: int) -> bytes:
    payload = b"\x40"
    for _ in range(levels):
        payload = _described_array_of(payload)
    return payload


def test_decode_rejects_described_array_depth_bypass():
    # each described-array level is an array plus a described layer, so 33 levels = 66 layers.
    with pytest.raises(ValueError, match="exceeds maximum depth"):
        _decode(_nested_described_array(_MAX_NESTING_DEPTH // 2 + 1))


def test_decode_accepts_described_array_at_limit():
    _decode(_nested_described_array(_MAX_NESTING_DEPTH // 2))


def test_decode_list_large_threads_explicit_depth():
    # depth is now a parameter rather than thread-local state: a decode already at the limit rejects.
    empty = b"\x00\x00\x00\x04\x00\x00\x00\x00"
    _decode_list_large(memoryview(empty), depth=_MAX_NESTING_DEPTH - 1)
    with pytest.raises(ValueError, match="exceeds maximum depth"):
        _decode_list_large(memoryview(empty), depth=_MAX_NESTING_DEPTH)


def _nested_list_to_empty(levels: int) -> bytes:
    # `levels` list32 wrappers around an empty list0 (0x45); total compound layers = levels + 1.
    payload = b"\x45"
    for _ in range(levels):
        body = b"\x00\x00\x00\x01" + payload
        payload = b"\xd0" + len(body).to_bytes(4, "big") + body
    return payload


def test_decode_rejects_empty_list_past_depth_limit():
    # the empty-list (list0) leaf is itself a compound layer and must count toward the limit.
    with pytest.raises(ValueError, match="exceeds maximum depth"):
        _decode(_nested_list_to_empty(_MAX_NESTING_DEPTH))


def test_decode_accepts_empty_list_at_depth_limit():
    _decode(_nested_list_to_empty(_MAX_NESTING_DEPTH - 1))


def test_decode_decimal128_rejects_out_of_range():
    # An out-of-range decimal128 exponent must surface as a decode ValueError, not a bare
    # decimal.DecimalException, so the receive loop can reject rather than tear down.
    with pytest.raises(ValueError):
        _decode(b"\x94" + b"\x5f" + b"\xff" * 15)


# Depth is threaded through every compound decoder as an explicit argument; a
# mis-wired recursive call would corrupt decoded values, not merely miscount
# depth. These cover real content surviving list/map/described nesting.
_LIST_OF_MAP_AND_INT = b"\xc0\x00\x02\xc1\x00\x02\x50\x01\x50\x02\x50\x03"
_MAP_WITH_LIST_VALUE = (
    b"\xd1\x00\x00\x00\x13\x00\x00\x00\x02"  # map32, size (ignored), count=2
    b"\x50\x09"  # key: ubyte 9
    b"\xd0\x00\x00\x00\x08\x00\x00\x00\x02\x50\x07\x50\x08"  # value: list32[7, 8]
)
_DESCRIBED_SCALAR = b"\x00\x53\x00\x50\x07"  # described(0x53) wrapping ubyte 7


@pytest.mark.parametrize(
    "payload,expected",
    [
        (_LIST_OF_MAP_AND_INT, [{1: 2}, 3]),
        (_MAP_WITH_LIST_VALUE, {9: [7, 8]}),
        (_DESCRIBED_SCALAR, 7),
    ],
)
def test_decode_preserves_nested_values(payload, expected):
    remaining, value = _decode(payload)
    assert value == expected
    assert bytes(remaining) == b""

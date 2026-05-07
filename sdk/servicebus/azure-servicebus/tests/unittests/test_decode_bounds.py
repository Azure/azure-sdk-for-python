import pytest

from azure.servicebus._pyamqp._decode import (
    _decode_array_large,
    _decode_list_large,
    _decode_map_large,
    _MAX_COMPOUND_COUNT,
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

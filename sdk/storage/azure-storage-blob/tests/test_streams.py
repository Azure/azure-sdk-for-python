# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import math
import os
import random
from io import BytesIO, UnsupportedOperation, SEEK_CUR, SEEK_END, SEEK_SET
from typing import List, Optional, Tuple, Union

import pytest
from azure.storage.blob._shared.streams import (
    StructuredMessageConstants,
    StructuredMessageDecodeStream,
    StructuredMessageEncodeStream,
    StructuredMessageProperties,
)
from azure.storage.extensions import crc64

from test_helpers import NonSeekableStream


def _write_segment(
    number: int,
    data: bytes,
    data_crc: Optional[int],
    stream: BytesIO,
) -> None:
    stream.write(number.to_bytes(2, 'little'))  # Segment number
    stream.write(len(data).to_bytes(8, 'little'))  # Segment length
    stream.write(data)  # Segment content
    if data_crc is not None:
        stream.write(data_crc.to_bytes(StructuredMessageConstants.CRC64_LENGTH, 'little'))


def _build_structured_message(
    data: bytes,
    segment_size: Union[int, List[int]],
    flags: StructuredMessageProperties,
    invalidate_crc_segment: Optional[int] = None,
) -> Tuple[BytesIO, int]:
    if isinstance(segment_size, list):
        segment_count = len(segment_size)
    else:
        segment_count = math.ceil(len(data) / segment_size) or 1
    segment_footer_length = StructuredMessageConstants.CRC64_LENGTH if StructuredMessageProperties.CRC64 in flags else 0

    message_length = (
        StructuredMessageConstants.V1_HEADER_LENGTH +
        ((StructuredMessageConstants.V1_SEGMENT_HEADER_LENGTH + segment_footer_length) * segment_count) +
        len(data) +
        (StructuredMessageConstants.CRC64_LENGTH if StructuredMessageProperties.CRC64 in flags else 0))

    message = BytesIO()
    message_crc = 0

    # Message Header
    message.write(b'\x01')  # Version
    message.write(message_length.to_bytes(8, 'little'))  # Message length
    message.write(int(flags).to_bytes(2, 'little'))  # Flags
    message.write(segment_count.to_bytes(2, 'little'))  # Num segments

    # Special case for 0 length content
    if len(data) == 0:
        crc = 0 if StructuredMessageProperties.CRC64 in flags else None
        _write_segment(1, data, crc, message)
    else:
        # Segments
        segment_sizes = segment_size if isinstance(segment_size, list) else [segment_size] * segment_count
        offset = 0
        for i in range(1, segment_count + 1):
            size = segment_sizes[i - 1]
            segment_data = data[offset: offset + size]
            offset += size

            segment_crc = None
            if StructuredMessageProperties.CRC64 in flags:
                segment_crc = crc64.compute(segment_data, 0)
                if i == invalidate_crc_segment:
                    segment_crc += 5
            _write_segment(i, segment_data, segment_crc, message)

            message_crc = crc64.compute(segment_data, message_crc)

    # Message footer
    if StructuredMessageProperties.CRC64 in flags:
        if invalidate_crc_segment == -1:
            message_crc += 5
        message.write(message_crc.to_bytes(StructuredMessageConstants.CRC64_LENGTH, 'little'))

    message.seek(0, 0)
    return message, message_length


class TestStructuredMessageEncodeStream:
    def test_close(self):
        inner = BytesIO()
        stream = StructuredMessageEncodeStream(inner, 0, StructuredMessageProperties.NONE)
        assert not stream.closed
        assert not inner.closed

        stream.close()
        assert stream.closed
        assert inner.closed

        with pytest.raises(ValueError):
            stream.read(0)

    def test_read_past_end(self):
        data = os.urandom(10)
        inner_stream = BytesIO(data)

        stream = StructuredMessageEncodeStream(inner_stream, len(data), StructuredMessageProperties.CRC64)
        expected = _build_structured_message(data, len(data), StructuredMessageProperties.CRC64)[0].getvalue()

        result = stream.read(100)
        assert result == expected

        result = stream.read(100)
        assert result == b''

    @pytest.mark.parametrize("size, segment_size, flags", [
        (0, 1, StructuredMessageProperties.NONE),
        (0, 1, StructuredMessageProperties.CRC64),
        (10, 1, StructuredMessageProperties.NONE),
        (10, 1, StructuredMessageProperties.CRC64),
        (1024, 1024, StructuredMessageProperties.NONE),
        (1024, 1024, StructuredMessageProperties.CRC64),
        (1024, 512, StructuredMessageProperties.NONE),
        (1024, 512, StructuredMessageProperties.CRC64),
        (1024, 200, StructuredMessageProperties.NONE),
        (1024, 200, StructuredMessageProperties.CRC64),
        (123456, 1234, StructuredMessageProperties.NONE),
        (123456, 1234, StructuredMessageProperties.CRC64),
        (10 * 1024 * 1024, 4 * 1024 * 1024, StructuredMessageProperties.NONE),
        (10 * 1024 * 1024, 4 * 1024 * 1024, StructuredMessageProperties.CRC64),
    ])
    def test_read_all(self, size, segment_size, flags):
        data = os.urandom(size)
        inner_stream = BytesIO(data)

        stream = StructuredMessageEncodeStream(inner_stream, len(data), flags, segment_size=segment_size)
        actual = stream.read()

        expected = _build_structured_message(data, segment_size, flags)[0].getvalue()
        assert actual == expected

    @pytest.mark.parametrize("size, segment_size, chunk_size, flags", [
        (10, 10, 1, StructuredMessageProperties.NONE),
        (10, 10, 1, StructuredMessageProperties.CRC64),
        (1024, 512, 512, StructuredMessageProperties.NONE),
        (1024, 512, 512, StructuredMessageProperties.CRC64),
        (1024, 512, 123, StructuredMessageProperties.NONE),
        (1024, 512, 123, StructuredMessageProperties.CRC64),
        (1024, 200, 512, StructuredMessageProperties.NONE),
        (1024, 200, 512, StructuredMessageProperties.CRC64),
        (12345, 678, 90, StructuredMessageProperties.NONE),
        (12345, 678, 90, StructuredMessageProperties.CRC64),
        (10 * 1024 * 1024, 4 * 1024 * 1024, 1 * 1024 * 1024, StructuredMessageProperties.NONE),
        (10 * 1024 * 1024, 4 * 1024 * 1024, 1 * 1024 * 1024, StructuredMessageProperties.CRC64),
    ])
    def test_read_chunks(self, size, segment_size, chunk_size, flags):
        data = os.urandom(size)
        inner_stream = BytesIO(data)

        stream = StructuredMessageEncodeStream(inner_stream, len(data), flags, segment_size=segment_size)

        read = 0
        content = b''
        while read < len(stream):
            chunk = stream.read(chunk_size)
            assert len(chunk) == min(chunk_size, len(stream) - read)

            content += chunk
            read += chunk_size

        expected = _build_structured_message(data, segment_size, flags)[0].getvalue()
        assert content == expected

    @pytest.mark.parametrize("data_size", [100, 1024, 10 * 1024, 100 * 1024])
    def test_random_reads(self, data_size):
        data = os.urandom(data_size)
        inner_stream = BytesIO(data)

        segment_size = data_size // 3
        stream = StructuredMessageEncodeStream(
            inner_stream,
            len(data),
            StructuredMessageProperties.CRC64,
            segment_size=segment_size)

        count = 0
        content = b''
        stream_size = len(stream)
        while count < stream_size:
            read_size = random.randint(10, stream_size // 3)
            read_size = min(read_size, stream_size - count)

            content += stream.read(read_size)
            count += read_size

        expected = _build_structured_message(data, segment_size, StructuredMessageProperties.CRC64)[0].getvalue()
        assert content == expected

    def test_seekable(self):
        data = os.urandom(10)
        inner_stream = BytesIO(data)
        sm_stream = StructuredMessageEncodeStream(inner_stream, len(data), StructuredMessageProperties.CRC64)

        assert sm_stream.seekable()

    def test_not_seekable(self):
        data = os.urandom(10)
        inner_stream = NonSeekableStream(BytesIO(data))
        sm_stream = StructuredMessageEncodeStream(inner_stream, len(data), StructuredMessageProperties.CRC64)

        assert not sm_stream.seekable()
        with pytest.raises(UnsupportedOperation):
            sm_stream.seek(0)

    def test_seek_whence(self):
        data = os.urandom(10)
        inner_stream = BytesIO(data)
        sm_stream = StructuredMessageEncodeStream(inner_stream, len(data), StructuredMessageProperties.CRC64)
        # Read so we can seek backwards
        sm_stream.read(25)

        pos = sm_stream.seek(10, SEEK_SET)
        assert pos == 10
        pos = sm_stream.seek(-len(sm_stream) + 9, SEEK_END)
        assert pos == 9
        pos = sm_stream.seek(-5, SEEK_CUR)
        assert pos == 4

    def test_seek_forward(self):
        data = os.urandom(10)
        inner_stream = BytesIO(data)
        sm_stream = StructuredMessageEncodeStream(inner_stream, len(data), StructuredMessageProperties.CRC64)

        sm_stream.read(5)
        with pytest.raises(UnsupportedOperation):
            sm_stream.seek(10)

    @pytest.mark.parametrize("initial_read, segment_size, flags", [
        # Single segment
        (5000, 2048, StructuredMessageProperties.NONE),  # End -> Beginning
        (5000, 2048, StructuredMessageProperties.CRC64),  # End -> Beginning
        (5, 2048, StructuredMessageProperties.NONE),  # Message header
        (5, 2048, StructuredMessageProperties.CRC64),
        (20, 2048, StructuredMessageProperties.NONE),  # Segment header
        (20, 2048, StructuredMessageProperties.CRC64),
        (100, 2048, StructuredMessageProperties.NONE),  # First segment content
        (100, 2048, StructuredMessageProperties.CRC64),
        (1000, 2048, StructuredMessageProperties.NONE),  # Second segment content
        (1000, 2048, StructuredMessageProperties.CRC64),
        (525, 2048, StructuredMessageProperties.CRC64),  # Segment footer
        (1092, 2048, StructuredMessageProperties.CRC64),  # Message footer
        # Multiple segments
        (5000, 500, StructuredMessageProperties.NONE),  # End -> Beginning
        (5000, 500, StructuredMessageProperties.CRC64),  # End -> Beginning
        (5, 500, StructuredMessageProperties.NONE),  # Message header
        (5, 500, StructuredMessageProperties.CRC64),
        (20, 500, StructuredMessageProperties.NONE),  # Segment header
        (20, 500, StructuredMessageProperties.CRC64),
        (100, 500, StructuredMessageProperties.NONE),  # First segment content
        (100, 500, StructuredMessageProperties.CRC64),
        (1000, 500, StructuredMessageProperties.NONE),  # Second segment content
        (1000, 500, StructuredMessageProperties.CRC64),
        (525, 500, StructuredMessageProperties.CRC64),  # Segment footer
        (1092, 500, StructuredMessageProperties.CRC64),  # Message footer
    ])
    def test_seek_reverse_beginning(self, initial_read, segment_size, flags):
        data = os.urandom(1024)
        inner_stream = BytesIO(data)
        sm_stream = StructuredMessageEncodeStream(inner_stream, len(data), flags, segment_size=segment_size)
        expected = _build_structured_message(data, segment_size, flags)[0].getvalue()

        initial = sm_stream.read(initial_read)
        assert initial == expected[:initial_read]

        sm_stream.seek(0)
        result = sm_stream.read()
        assert result == expected

    @pytest.mark.parametrize("initial_read, seek_offset, segment_size, flags", [
        # Single segment
        (10, 5, 2048, StructuredMessageProperties.NONE),  # Message header -> Message header
        (10, 5, 2048, StructuredMessageProperties.CRC64),
        (20, 15, 2048, StructuredMessageProperties.NONE),  # Segment header -> Segment header
        (20, 15, 2048, StructuredMessageProperties.CRC64),
        (100, 50, 2048, StructuredMessageProperties.NONE),  # First segment content -> First segment content
        (100, 50, 2048, StructuredMessageProperties.CRC64),
        (1000, 900, 2048, StructuredMessageProperties.NONE),  # Second segment content -> Second segment content
        (1000, 900, 2048, StructuredMessageProperties.CRC64),
        (530, 525, 2048, StructuredMessageProperties.CRC64),  # Segment footer -> Segment footer
        (1060, 1050, 2048, StructuredMessageProperties.CRC64),  # Message footer -> Segment footer
        (1000, 100, 2048, StructuredMessageProperties.NONE),  # Second segment content -> First segment content
        (1000, 100, 2048, StructuredMessageProperties.CRC64),
        (1000, 20, 2048, StructuredMessageProperties.NONE),  # Second segment content -> First segment header
        (1000, 20, 2048, StructuredMessageProperties.CRC64),
        (1000, 530, 2048, StructuredMessageProperties.CRC64),  # Second segment content -> First segment footer
        (1097, 100, 2048, StructuredMessageProperties.CRC64),  # Message footer -> First segment content
        # Multiple segments
        (10, 5, 500, StructuredMessageProperties.NONE),  # Message header -> Message header
        (10, 5, 500, StructuredMessageProperties.CRC64),
        (20, 15, 500, StructuredMessageProperties.NONE),  # Segment header -> Segment header
        (20, 15, 500, StructuredMessageProperties.CRC64),
        (100, 50, 500, StructuredMessageProperties.NONE),  # First segment content -> First segment content
        (100, 50, 500, StructuredMessageProperties.CRC64),
        (1000, 900, 500, StructuredMessageProperties.NONE),  # Second segment content -> Second segment content
        (1000, 900, 500, StructuredMessageProperties.CRC64),
        (530, 525, 500, StructuredMessageProperties.CRC64),  # Segment footer -> Segment footer
        (1097, 1090, 500, StructuredMessageProperties.CRC64),  # Message footer -> Segment footer
        (1000, 100, 500, StructuredMessageProperties.NONE),  # Second segment content -> First segment content
        (1000, 100, 500, StructuredMessageProperties.CRC64),
        (1000, 20, 500, StructuredMessageProperties.NONE),  # Second segment content -> First segment header
        (1000, 20, 500, StructuredMessageProperties.CRC64),
        (1000, 530, 500, StructuredMessageProperties.CRC64),  # Second segment content -> First segment footer
        (1097, 100, 500, StructuredMessageProperties.CRC64),  # Message footer -> First segment content
    ])
    def test_seek_reverse_middle(self, initial_read, seek_offset, segment_size, flags):
        data = os.urandom(1024)
        inner_stream = BytesIO(data)
        sm_stream = StructuredMessageEncodeStream(inner_stream, len(data), flags, segment_size=segment_size)
        expected = _build_structured_message(data, segment_size, flags)[0].getvalue()

        initial = sm_stream.read(initial_read)
        assert initial == expected[:initial_read]

        sm_stream.seek(seek_offset)
        result = sm_stream.read()
        assert result == expected[seek_offset:]

    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    def test_seek_reverse_random(self, flags):
        data = os.urandom(1024)
        expected = _build_structured_message(data, 500, flags)[0].getvalue()

        for _ in range(10):
            inner_stream = BytesIO(data)
            sm_stream = StructuredMessageEncodeStream(inner_stream, len(data), flags, segment_size=500)

            initial_read = random.randint(5, len(data))
            seek_offset = random.randint(0, initial_read)

            initial = sm_stream.read(initial_read)
            assert initial == expected[:initial_read]

            sm_stream.seek(seek_offset)
            result = sm_stream.read()
            assert result == expected[seek_offset:]

    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    def test_partial_stream_read(self, flags):
        data = os.urandom(1024)
        partial_read = 100

        inner_stream = BytesIO(data)
        inner_stream.seek(partial_read)
        expected = _build_structured_message(data[partial_read:], 500, flags)[0].getvalue()

        sm_stream = StructuredMessageEncodeStream(inner_stream, len(data) - partial_read, flags, segment_size=500)
        result = sm_stream.read()
        assert result == expected

    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    def test_partial_stream_seek_beginning(self, flags):
        data = os.urandom(1024)
        partial_read = 100

        inner_stream = BytesIO(data)
        inner_stream.seek(partial_read)
        expected = _build_structured_message(data[partial_read:], 500, flags)[0].getvalue()

        sm_stream = StructuredMessageEncodeStream(inner_stream, len(data) - partial_read, flags, segment_size=500)
        initial = sm_stream.read(101)
        assert initial == expected[:101]

        sm_stream.seek(0)
        assert inner_stream.tell() == partial_read

        result = sm_stream.read()
        assert result == expected

    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    def test_partial_stream_seek_middle(self, flags):
        data = os.urandom(1024)
        partial_read = 100

        inner_stream = BytesIO(data)
        inner_stream.seek(partial_read)
        expected = _build_structured_message(data[partial_read:], 500, flags)[0].getvalue()

        sm_stream = StructuredMessageEncodeStream(inner_stream, len(data) - partial_read, flags, segment_size=500)
        initial = sm_stream.read(501)
        assert initial == expected[:501]

        sm_stream.seek(100)
        assert inner_stream.tell() == partial_read + (100 -
                                                      StructuredMessageConstants.V1_HEADER_LENGTH -
                                                      StructuredMessageConstants.V1_SEGMENT_HEADER_LENGTH)

        result = sm_stream.read()
        assert result == expected[100:]


class TestStructuredMessageDecodeStream:

    def test_empty_inner_stream(self):
        with pytest.raises(ValueError):
            StructuredMessageDecodeStream(BytesIO(), 0)

    def test_read_past_end(self):
        data = os.urandom(10)
        message_stream, length = _build_structured_message(data, len(data), StructuredMessageProperties.CRC64)

        stream = StructuredMessageDecodeStream(message_stream, length)
        result = stream.read(100)
        assert result == data

        result = stream.read(100)
        assert result == b''

    @pytest.mark.parametrize("size, segment_size, flags", [
        (0, 1, StructuredMessageProperties.NONE),
        (0, 1, StructuredMessageProperties.CRC64),
        (10, 1, StructuredMessageProperties.NONE),
        (10, 1, StructuredMessageProperties.CRC64),
        (1024, 1024, StructuredMessageProperties.NONE),
        (1024, 1024, StructuredMessageProperties.CRC64),
        (1024, 512, StructuredMessageProperties.NONE),
        (1024, 512, StructuredMessageProperties.CRC64),
        (1024, 200, StructuredMessageProperties.NONE),
        (1024, 200, StructuredMessageProperties.CRC64),
        (123456, 1234, StructuredMessageProperties.NONE),
        (123456, 1234, StructuredMessageProperties.CRC64),
        (10 * 1024 * 1024, 4 * 1024 * 1024, StructuredMessageProperties.NONE),
        (10 * 1024 * 1024, 4 * 1024 * 1024, StructuredMessageProperties.CRC64),
    ])
    def test_read_all(self, size, segment_size, flags):
        data = os.urandom(size)
        message_stream, length = _build_structured_message(data, segment_size, flags)

        stream = StructuredMessageDecodeStream(message_stream, length)
        content = stream.read()

        assert content == data

    @pytest.mark.parametrize("size, segment_size, chunk_size, flags", [
        (10, 10, 1, StructuredMessageProperties.NONE),
        (10, 10, 1, StructuredMessageProperties.CRC64),
        (1024, 512, 512, StructuredMessageProperties.NONE),
        (1024, 512, 512, StructuredMessageProperties.CRC64),
        (1024, 512, 123, StructuredMessageProperties.NONE),
        (1024, 512, 123, StructuredMessageProperties.CRC64),
        (1024, 200, 512, StructuredMessageProperties.NONE),
        (1024, 200, 512, StructuredMessageProperties.CRC64),
        (10 * 1024 * 1024, 4 * 1024 * 1024, 1 * 1024 * 1024, StructuredMessageProperties.NONE),
        (10 * 1024 * 1024, 4 * 1024 * 1024, 1 * 1024 * 1024, StructuredMessageProperties.CRC64),
    ])
    def test_read_chunks(self, size, segment_size, chunk_size, flags):
        data = os.urandom(size)
        message_stream, length = _build_structured_message(data, segment_size, flags)

        stream = StructuredMessageDecodeStream(message_stream, length)
        read = 0
        content = b''
        while read < len(data):
            chunk = stream.read(chunk_size)
            content += chunk
            read += chunk_size

        assert content == data

    @pytest.mark.parametrize("data_size", [100, 1024, 10 * 1024, 100 * 1024])
    def test_random_reads(self, data_size):
        data = os.urandom(data_size)
        message_stream, length = _build_structured_message(data, data_size // 3, StructuredMessageProperties.CRC64)

        stream = StructuredMessageDecodeStream(message_stream, length)

        count = 0
        content = b''
        while count < data_size:
            read_size = random.randint(10, data_size // 3)
            read_size = min(read_size, data_size - count)

            content += stream.read(read_size)
            count += read_size

        assert content == data

    @pytest.mark.parametrize("data_size", [100, 1024, 10 * 1024, 100 * 1024])
    def test_random_segment_sizes(self, data_size):
        segment_sizes = []
        count = 0
        while count < data_size:
            size = random.randint(10, data_size // 3)
            size = min(size, data_size - count)
            segment_sizes.append(size)
            count += size

        data = os.urandom(data_size)
        message_stream, length = _build_structured_message(data, segment_sizes, StructuredMessageProperties.CRC64)

        stream = StructuredMessageDecodeStream(message_stream, length)
        content = stream.read()

        assert content == data

    @pytest.mark.parametrize("invalid_segment", [1, 2, 3, -1])
    def test_crc64_mismatch_read_all(self, invalid_segment):
        data = os.urandom(3 * 1024)
        message_stream, length = _build_structured_message(
            data,
            1024,
            StructuredMessageProperties.CRC64,
            invalid_segment)

        stream = StructuredMessageDecodeStream(message_stream, length)
        with pytest.raises(ValueError) as e:
            stream.read()
        assert 'CRC64 mismatch' in str(e.value)

    @pytest.mark.parametrize("invalid_segment", [1, 2, 3, -1])
    def test_crc64_mismatch_read_chunks(self, invalid_segment):
        data = os.urandom(3 * 1024)
        message_stream, length = _build_structured_message(
            data,
            1024,
            StructuredMessageProperties.CRC64,
            invalid_segment)

        stream = StructuredMessageDecodeStream(message_stream, length)
        # Since we only check CRC on segment borders, some reads will succeed, but we test
        # to ensure eventually the stream reading will error out.
        with pytest.raises(ValueError) as e:
            read = 0
            while read < len(data):
                stream.read(512)

        assert 'CRC64 mismatch' in str(e.value)

    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    def test_invalid_message_version(self, flags):
        data = os.urandom(1024)
        message_stream, length = _build_structured_message(data, 512, flags)

        # Stream already set to front
        message_stream.write(b'\xFF')
        message_stream.seek(0)

        stream = StructuredMessageDecodeStream(message_stream, length)
        with pytest.raises(ValueError):
            stream.read()

    @pytest.mark.parametrize("message_length", [100, 1234567])  # Correct value: 1057
    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    def test_incorrect_message_length(self, message_length, flags):
        data = os.urandom(1024)
        message_stream, length = _build_structured_message(data, 512, flags)

        message_stream.seek(1)
        message_stream.write(int.to_bytes(message_length, 8, 'little'))
        message_stream.seek(0)

        stream = StructuredMessageDecodeStream(message_stream, length)
        with pytest.raises(ValueError):
            stream.read()

    @pytest.mark.parametrize("segment_count", [2, 123])  # Correct value: 4
    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    def test_incorrect_segment_count(self, segment_count, flags):
        data = os.urandom(1024)
        message_stream, length = _build_structured_message(data, 256, flags)

        message_stream.seek(11)
        message_stream.write(int.to_bytes(segment_count, 2, 'little'))
        message_stream.seek(0)

        stream = StructuredMessageDecodeStream(message_stream, length)
        with pytest.raises(ValueError):
            stream.read()

    @pytest.mark.parametrize("segment_number", [1, 123])  # Correct value: 2
    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    def test_incorrect_segment_number(self, segment_number, flags):
        data = os.urandom(1024)
        message_stream, length = _build_structured_message(data, 256, flags)

        # Change the second segment to be the incorrect number
        position = (StructuredMessageConstants.V1_HEADER_LENGTH +
                    StructuredMessageConstants.V1_SEGMENT_HEADER_LENGTH +
                    256 +
                    (StructuredMessageConstants.CRC64_LENGTH if StructuredMessageProperties.CRC64 in flags else 0))
        message_stream.seek(position)
        message_stream.write(int.to_bytes(segment_number, 2, 'little'))
        message_stream.seek(0)

        stream = StructuredMessageDecodeStream(message_stream, length)
        with pytest.raises(ValueError):
            stream.read()

    @pytest.mark.parametrize("segment_size", [123, 345])  # Correct value: 256
    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    def test_incorrect_segment_size(self, segment_size, flags):
        data = os.urandom(1024)
        message_stream, length = _build_structured_message(data, 256, flags)

        # Change the second segment to be the incorrect size
        position = (StructuredMessageConstants.V1_HEADER_LENGTH +
                    StructuredMessageConstants.V1_SEGMENT_HEADER_LENGTH +
                    256 +
                    (StructuredMessageConstants.CRC64_LENGTH if StructuredMessageProperties.CRC64 in flags else 0) +
                    2)
        message_stream.seek(position)
        message_stream.write(int.to_bytes(segment_size, 2, 'little'))
        message_stream.seek(0)

        stream = StructuredMessageDecodeStream(message_stream, length)
        with pytest.raises(ValueError):
            stream.read()

    @pytest.mark.parametrize("segment_size", [123, 345])  # Correct value: 256
    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    def test_incorrect_segment_size_single_segment(self, segment_size, flags):
        data = os.urandom(256)
        message_stream, length = _build_structured_message(data, 256, flags)

        message_stream.seek(15)
        message_stream.write(int.to_bytes(segment_size, 2, 'little'))
        message_stream.seek(0)

        stream = StructuredMessageDecodeStream(message_stream, length)
        with pytest.raises(ValueError):
            stream.read()

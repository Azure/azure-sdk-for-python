# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import math
import sys
from enum import auto, Enum, IntFlag
from io import BytesIO
from typing import IO

from azure.storage.extensions import crc64


DEFAULT_MESSAGE_VERSION = 1
DEFAULT_SEGMENT_SIZE = 4 * 1024 * 1024


class StructuredMessageError(Exception):
    pass


class StructuredMessageConstants:
    V1_HEADER_LENGTH = 13
    V1_SEGMENT_HEADER_LENGTH = 10
    CRC64_LENGTH = 8


class StructuredMessageProperties(IntFlag):
    NONE = 0
    CRC64 = auto()


class SMRegion(Enum):
    MESSAGE_HEADER = 1,
    SEGMENT_HEADER = 2,
    SEGMENT_CONTENT = 3,
    SEGMENT_FOOTER = 4,
    MESSAGE_FOOTER = 5,


def generate_message_header(version: int, size: int, flags: StructuredMessageProperties, num_segments: int) -> bytes:
    return (version.to_bytes(1, 'little') +
            size.to_bytes(8, 'little') +
            flags.to_bytes(2, 'little') +
            num_segments.to_bytes(2, 'little'))


def generate_segment_header(number: int, size: int) -> bytes:
    return (number.to_bytes(2, 'little') +
            size.to_bytes(8, 'little'))


class StructuredMessageEncodeStream:
    message_version: int
    content_length: int
    message_length: int
    flags: StructuredMessageProperties

    _inner_stream: IO[bytes]
    _segment_size: int
    _num_segments: int

    _content_offset: int
    _current_segment_number: int
    _current_region: SMRegion
    _current_region_length: int
    _current_region_offset: int
    _current_region_content: bytes
    _message_crc64: int
    _segment_crc64: int

    def __init__(
        self, inner_stream: IO[bytes],
        content_length: int,
        flags: StructuredMessageProperties,
        *,
        segment_size: int = DEFAULT_SEGMENT_SIZE
    ) -> None:
        if segment_size < 1:
            raise ValueError("Segment size must be greater than 0.")

        self.message_version = DEFAULT_MESSAGE_VERSION
        self.content_length = content_length
        self.flags = flags

        self._inner_stream = inner_stream
        self._segment_size = segment_size
        self._num_segments = math.ceil(self.content_length / self._segment_size) or 1

        self.message_length = self._calculate_message_length()

        self._content_offset = 0
        self._current_segment_number = 0  # Will be incremented before first segment
        self._current_region = SMRegion.MESSAGE_HEADER
        self._current_region_length = self._message_header_length
        self._current_region_offset = 0
        self._current_region_content = b''

        self._message_crc64 = 0
        self._segment_crc64 = 0

    @property
    def _message_header_length(self) -> int:
        return StructuredMessageConstants.V1_HEADER_LENGTH

    @property
    def _segment_header_length(self) -> int:
        return StructuredMessageConstants.V1_SEGMENT_HEADER_LENGTH

    @property
    def _segment_footer_length(self) -> int:
        return StructuredMessageConstants.CRC64_LENGTH if StructuredMessageProperties.CRC64 in self.flags else 0

    @property
    def _message_footer_length(self) -> int:
        return StructuredMessageConstants.CRC64_LENGTH if StructuredMessageProperties.CRC64 in self.flags else 0

    def __len__(self):
        return self.message_length

    def tell(self) -> int:
        if self._current_region == SMRegion.MESSAGE_HEADER:
            return self._current_region_offset
        elif self._current_region == SMRegion.SEGMENT_HEADER:
            return (self._message_header_length + self._content_offset +
                    (self._current_segment_number - 1) * (self._segment_header_length + self._segment_footer_length) +
                    self._current_region_offset)
        elif self._current_region == SMRegion.SEGMENT_CONTENT:
            return (self._message_header_length + self._content_offset +
                    (self._current_segment_number - 1) * (self._segment_header_length + self._segment_footer_length) +
                    self._segment_header_length)
        elif self._current_region == SMRegion.SEGMENT_FOOTER:
            return (self._message_header_length + self._content_offset +
                    (self._current_segment_number - 1) * (self._segment_header_length + self._segment_footer_length) +
                    self._segment_header_length +
                    self._current_region_offset)
        elif self._current_region == SMRegion.MESSAGE_FOOTER:
            return (self._message_header_length + self._content_offset +
                    self._current_segment_number * (self._segment_header_length + self._segment_footer_length) +
                    self._current_region_offset)
        else:
            raise StructuredMessageError(f"Invalid SMRegion {self._current_region}")

    def read(self, size: int = -1) -> bytes:
        if size == 0:
            return b''
        if size < 0:
            size = sys.maxsize

        count = 0
        output = BytesIO()

        while count < size and self.tell() < self.message_length:
            remaining = size - count
            if self._current_region in (
                    SMRegion.MESSAGE_HEADER,
                    SMRegion.SEGMENT_HEADER,
                    SMRegion.SEGMENT_FOOTER,
                    SMRegion.MESSAGE_FOOTER):
                count += self._read_metadata_region(self._current_region, remaining, output)
            elif self._current_region == SMRegion.SEGMENT_CONTENT:
                count += self._read_content(size, output)
            else:
                raise StructuredMessageError(f"Invalid SMRegion {self._current_region}")

        return output.getvalue()

    def _calculate_message_length(self) -> int:
        length = self._message_header_length
        length += (self._segment_header_length + self._segment_footer_length) * self._num_segments
        length += self.content_length
        length += self._message_footer_length
        return length

    def _buffer_metadata_region(self, region: SMRegion) -> None:
        if region == SMRegion.MESSAGE_HEADER:
            self._current_region_content = generate_message_header(
                self.message_version,
                self.message_length,
                self.flags,
                self._num_segments)

        elif region == SMRegion.SEGMENT_HEADER:
            self._current_segment_number += 1
            segment_size = min(self._segment_size, self.content_length - self._content_offset)
            self._current_region_content = generate_segment_header(self._current_segment_number, segment_size)

        elif region == SMRegion.SEGMENT_FOOTER:
            if StructuredMessageProperties.CRC64 in self.flags:
                self._current_region_content = (
                    self._segment_crc64.to_bytes(StructuredMessageConstants.CRC64_LENGTH, 'little'))
            else:
                self._current_region_content = b''

        elif region == SMRegion.MESSAGE_FOOTER:
            if StructuredMessageProperties.CRC64 in self.flags:
                self._current_region_content = (
                    self._message_crc64.to_bytes(StructuredMessageConstants.CRC64_LENGTH, 'little'))
            else:
                self._current_region_content = b''

        else:
            raise StructuredMessageError(f"Invalid metadata SMRegion {self._current_region}")

    def _advance_region(self, current: SMRegion):
        self._current_region_offset = 0
        self._current_region_content = b''

        if current == SMRegion.MESSAGE_HEADER:
            self._current_region = SMRegion.SEGMENT_HEADER
            self._current_region_length = self._segment_header_length
        elif current == SMRegion.SEGMENT_HEADER:
            self._current_region = SMRegion.SEGMENT_CONTENT
            self._current_region_length = min(self._segment_size, self.content_length - self._content_offset)
            self._segment_crc64 = 0
        elif current == SMRegion.SEGMENT_CONTENT:
            self._current_region = SMRegion.SEGMENT_FOOTER
            self._current_region_length = self._segment_footer_length
        elif current == SMRegion.SEGMENT_FOOTER:
            # If we're at the end of the content
            if self._content_offset == self.content_length:
                self._current_region = SMRegion.MESSAGE_FOOTER
                self._current_region_length = self._message_footer_length
            else:
                self._current_region = SMRegion.SEGMENT_HEADER
                self._current_region_length = self._segment_header_length
        else:
            raise StructuredMessageError(f"Invalid SMRegion {self._current_region}")

    def _read_metadata_region(self, region: SMRegion, size: int, output: BytesIO) -> int:
        # If nothing has been read, buffer the region
        if self._current_region_offset == 0:
            self._buffer_metadata_region(region)

        read_size = min(size, self._current_region_length - self._current_region_offset)
        content = self._current_region_content[self._current_region_offset: self._current_region_offset + read_size]
        output.write(content)

        self._current_region_offset += read_size
        if (self._current_region_offset == self._current_region_length and
                self._current_region != SMRegion.MESSAGE_FOOTER):
            self._advance_region(region)

        return read_size

    def _read_content(self, size: int, output: BytesIO) -> int:
        read_size = min(size, self._current_region_length - self._current_region_offset)
        content = self._inner_stream.read(read_size)
        output.write(content)

        if StructuredMessageProperties.CRC64 in self.flags:
            self._segment_crc64 = crc64.compute_crc64(content, self._segment_crc64)
            self._message_crc64 = crc64.compute_crc64(content, self._message_crc64)

        self._content_offset += read_size
        self._current_region_offset += read_size
        if self._current_region_offset == self._current_region_length:
            self._advance_region(SMRegion.SEGMENT_CONTENT)

        return read_size


class StructuredMessageDecodeStream:

    message_version: int
    """The version of the structured message."""
    message_length: int
    """The total length of the structured message."""
    flags: StructuredMessageProperties
    """The properties included in the structured message."""
    num_segments: int
    """The number of message segments."""

    _inner_stream: IO[bytes]
    _message_offset: int
    _message_crc64: int
    _segment_number: int
    _segment_crc64: int
    _segment_content_length: int
    _segment_content_offset: int

    def __init__(self, inner_stream: IO[bytes], content_length: int) -> None:
        self.message_length = content_length
        # The stream should be at least long enough to hold minimum header length
        if self.message_length < StructuredMessageConstants.V1_HEADER_LENGTH:
            raise ValueError("Content not long enough to contain a valid message header.")

        self._inner_stream = inner_stream
        self._message_offset = 0
        self._message_crc64 = 0

        self._segment_number = 0
        self._segment_crc64 = 0
        self._segment_content_length = 0
        self._segment_content_offset = 0

    @property
    def _segment_header_length(self) -> int:
        if self.message_version == 1:
            return StructuredMessageConstants.V1_SEGMENT_HEADER_LENGTH

    @property
    def _segment_footer_length(self) -> int:
        if self.message_version == 1:
            return StructuredMessageConstants.CRC64_LENGTH if StructuredMessageProperties.CRC64 in self.flags else 0

    @property
    def _message_footer_length(self) -> int:
        if self.message_version == 1:
            return StructuredMessageConstants.CRC64_LENGTH if StructuredMessageProperties.CRC64 in self.flags else 0

    @property
    def _end_of_segment_content(self) -> bool:
        return self._segment_content_offset == self._segment_content_length

    def read(self, size: int = -1) -> bytes:
        if size == 0:
            return b''
        if size < 0:
            size = sys.maxsize

        # On the first read, read message header and first segment header
        if self._message_offset == 0:
            self._read_message_header()
            self._read_segment_header()

            # Special case for 0 length content
            if self._end_of_segment_content:
                self._read_segment_footer()
                if self.num_segments > 1:
                    raise StructuredMessageError("First message segment was empty but more segments were detected.")
                self._read_message_footer()
                return b''

        count = 0
        content = BytesIO()
        while count < size and not (self._end_of_segment_content and self._message_offset == self.message_length):
            if self._end_of_segment_content:
                self._read_segment_header()

            segment_remaining = self._segment_content_length - self._segment_content_offset
            read_size = min(segment_remaining, size - count)

            segment_content = self._inner_stream.read(read_size)
            content.write(segment_content)

            # Update the running CRC64 for the segment and message
            if StructuredMessageProperties.CRC64 in self.flags:
                self._segment_crc64 = crc64.compute_crc64(segment_content, self._segment_crc64)
                self._message_crc64 = crc64.compute_crc64(segment_content, self._message_crc64)

            self._segment_content_offset += read_size
            self._message_offset += read_size
            count += read_size

            if self._end_of_segment_content:
                self._read_segment_footer()
                # If we are on the last segment, also read the message footer
                if self._segment_number == self.num_segments:
                    self._read_message_footer()

        # One final check to ensure if we think we've reached the end of the stream
        # that the current segment number matches the total.
        if self._message_offset == self.message_length and self._segment_number != self.num_segments:
            raise StructuredMessageError("Invalid structured message data detected.")

        return content.getvalue()

    def _assert_remaining_length(self, length: int):
        if self.message_length - self._message_offset < length:
            raise StructuredMessageError("Invalid structured message data detected.")

    def _read_message_header(self) -> None:
        # The first byte should always be the message version
        self.message_version = int.from_bytes(self._inner_stream.read(1), 'little')

        if self.message_version == 1:
            message_length = int.from_bytes(self._inner_stream.read(8), 'little')
            if message_length != self.message_length:
                raise StructuredMessageError(f"Structured message length {message_length} "
                                             f"did not match content length {self.message_length}")

            self.flags = StructuredMessageProperties(int.from_bytes(self._inner_stream.read(2), 'little'))
            self.num_segments = int.from_bytes(self._inner_stream.read(2), 'little')

            self._message_offset += StructuredMessageConstants.V1_HEADER_LENGTH

        else:
            raise StructuredMessageError(f"The structured message version is not supported: {self.message_version}")

    def _read_message_footer(self) -> None:
        # Sanity check: There should only be self._message_footer_length (could be 0) bytes left to consume.
        # If not, it is likely the message header contained incorrect info.
        if self.message_length - self._message_offset != self._message_footer_length:
            raise StructuredMessageError("Invalid structured message data detected.")

        if StructuredMessageProperties.CRC64 in self.flags:
            message_crc = self._inner_stream.read(StructuredMessageConstants.CRC64_LENGTH)

            if self._message_crc64 != int.from_bytes(message_crc, 'little'):
                raise StructuredMessageError("CRC64 mismatch detected in message trailer. "
                                             "All data read should be considered invalid.")

        self._message_offset += self._message_footer_length

    def _read_segment_header(self) -> None:
        self._assert_remaining_length(self._segment_header_length)

        segment_number = int.from_bytes(self._inner_stream.read(2), 'little')
        if segment_number != self._segment_number + 1:
            raise StructuredMessageError(f"Structured message segment number invalid or out of order {segment_number}")
        self._segment_number = segment_number
        self._segment_content_length = int.from_bytes(self._inner_stream.read(8), 'little')
        self._message_offset += self._segment_header_length

        self._segment_content_offset = 0
        self._segment_crc64 = 0

    def _read_segment_footer(self) -> None:
        self._assert_remaining_length(self._segment_footer_length)

        if StructuredMessageProperties.CRC64 in self.flags:
            segment_crc = self._inner_stream.read(StructuredMessageConstants.CRC64_LENGTH)

            if self._segment_crc64 != int.from_bytes(segment_crc, 'little'):
                raise StructuredMessageError(f"CRC64 mismatch detected in segment {self._segment_number}. "
                                             f"All data read should be considered invalid.")

        self._message_offset += self._segment_footer_length

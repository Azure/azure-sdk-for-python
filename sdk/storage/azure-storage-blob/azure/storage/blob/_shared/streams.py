# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import math
import sys
from enum import auto, Enum, IntFlag
from io import BytesIO, IOBase, UnsupportedOperation, SEEK_CUR, SEEK_END, SEEK_SET
from typing import IO, Optional

from .validation import calculate_crc64

DEFAULT_MESSAGE_VERSION = 1
DEFAULT_SEGMENT_SIZE = 4 * 1024 * 1024


class StructuredMessageConstants:
    V1_HEADER_LENGTH = 13
    V1_SEGMENT_HEADER_LENGTH = 10
    CRC64_LENGTH = 8


class StructuredMessageProperties(IntFlag):
    NONE = 0
    CRC64 = auto()


class SMRegion(Enum):
    MESSAGE_HEADER = 1
    SEGMENT_HEADER = 2
    SEGMENT_CONTENT = 3
    SEGMENT_FOOTER = 4
    MESSAGE_FOOTER = 5


def generate_message_header(version: int, size: int, flags: StructuredMessageProperties, num_segments: int) -> bytes:
    return (version.to_bytes(1, 'little') +
            size.to_bytes(8, 'little') +
            flags.to_bytes(2, 'little') +
            num_segments.to_bytes(2, 'little'))


def generate_segment_header(number: int, size: int) -> bytes:
    return (number.to_bytes(2, 'little') +
            size.to_bytes(8, 'little'))


class StructuredMessageEncodeStream(IOBase):  # pylint: disable=too-many-instance-attributes
    message_version: int
    content_length: int
    message_length: int
    flags: StructuredMessageProperties

    _inner_stream: IO[bytes]
    _segment_size: int
    _num_segments: int

    _initial_content_position: Optional[int]
    """Initial position of the inner stream, None if it did not implement tell()"""
    _content_offset: int
    _current_segment_number: int
    _current_region: SMRegion
    _current_region_length: int
    _current_region_offset: int

    _checksum_offset: int
    """Tracks the offset the checksum has been calculated up to for seeking purposes"""

    _message_crc64: int
    _segment_crc64s: dict[int, int]

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

        self._checksum_offset = 0
        self._message_crc64 = 0
        self._segment_crc64s = {}

        # Attempt to get starting position of inner stream. If we can't, this stream will not be seekable
        try:
            self._initial_content_position = self._inner_stream.tell()
        except (AttributeError, UnsupportedOperation, OSError):
            self._initial_content_position = None
        super().__init__()

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

    def _update_current_region_length(self) -> None:
        if self._current_region == SMRegion.MESSAGE_HEADER:
            self._current_region_length = self._message_header_length
        elif self._current_region == SMRegion.SEGMENT_HEADER:
            self._current_region_length = self._segment_header_length
        elif self._current_region == SMRegion.SEGMENT_CONTENT:
            # Last segment size is remaining content
            if self._current_segment_number == self._num_segments:
                self._current_region_length = self.content_length - \
                                              ((self._current_segment_number - 1) * self._segment_size)
            else:
                self._current_region_length = self._segment_size
        elif self._current_region == SMRegion.SEGMENT_FOOTER:
            self._current_region_length = self._segment_footer_length
        elif self._current_region == SMRegion.MESSAGE_FOOTER:
            self._current_region_length = self._message_footer_length
        else:
            raise ValueError(f"Invalid SMRegion {self._current_region}")

    def __len__(self):
        return self.message_length

    def close(self) -> None:
        self._inner_stream.close()
        super().close()

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        try:
            # Only seekable if the inner stream is and we could get its initial position
            return self._inner_stream.seekable() and self._initial_content_position is not None
        except (AttributeError, UnsupportedOperation, OSError):
            return False

    def tell(self) -> int:
        if self._current_region == SMRegion.MESSAGE_HEADER:
            return self._current_region_offset
        if self._current_region == SMRegion.SEGMENT_HEADER:
            return (self._message_header_length + self._content_offset +
                    (self._current_segment_number - 1) * (self._segment_header_length + self._segment_footer_length) +
                    self._current_region_offset)
        if self._current_region == SMRegion.SEGMENT_CONTENT:
            return (self._message_header_length + self._content_offset +
                    (self._current_segment_number - 1) * (self._segment_header_length + self._segment_footer_length) +
                    self._segment_header_length)
        if self._current_region == SMRegion.SEGMENT_FOOTER:
            return (self._message_header_length + self._content_offset +
                    (self._current_segment_number - 1) * (self._segment_header_length + self._segment_footer_length) +
                    self._segment_header_length +
                    self._current_region_offset)
        if self._current_region == SMRegion.MESSAGE_FOOTER:
            return (self._message_header_length + self._content_offset +
                    self._current_segment_number * (self._segment_header_length + self._segment_footer_length) +
                    self._current_region_offset)

        raise ValueError(f"Invalid SMRegion {self._current_region}")

    def seek(self, offset: int, whence: int = SEEK_SET) -> int:
        if not self.seekable():
            raise UnsupportedOperation("Inner stream is not seekable.")

        if whence == SEEK_SET:
            position = offset
        elif whence == SEEK_CUR:
            position = self.tell() + offset
        elif whence == SEEK_END:
            position = self.message_length + offset
        else:
            raise ValueError(f"Invalid value for whence: {whence}")

        if position < 0:
            raise ValueError(f"Cannot seek to negative position: {position}")
        if position > self.tell():
            raise UnsupportedOperation("This stream only supports seeking backwards.")

        # MESSAGE_HEADER
        if position < self._message_header_length:
            self._current_region = SMRegion.MESSAGE_HEADER
            self._current_region_offset = position
            self._content_offset = 0
            self._current_segment_number = 0
        # MESSAGE_FOOTER
        elif position >= self.message_length - self._message_footer_length:
            self._current_region = SMRegion.MESSAGE_FOOTER
            self._current_region_offset = position - (self.message_length - self._message_footer_length)
            self._content_offset = self.content_length
            self._current_segment_number = self._num_segments
        else:
            # The size of a "full" segment. Fine to use for calculating new segment number and pos
            full_segment_size = self._segment_header_length + self._segment_size + self._segment_footer_length
            new_segment_num = 1 + (position - self._message_header_length) // full_segment_size
            segment_pos = (position - self._message_header_length) % full_segment_size
            previous_segments_total_content_size = (new_segment_num - 1) * self._segment_size

            # We need the size of the segment we are seeking to for some of the calculations below
            new_segment_size = self._segment_size
            if new_segment_num == self._num_segments:
                # The last segment size is the remaining content length
                new_segment_size = self.content_length - previous_segments_total_content_size

            # SEGMENT_HEADER
            if segment_pos < self._segment_header_length:
                self._current_region = SMRegion.SEGMENT_HEADER
                self._current_region_offset = segment_pos
                self._content_offset = previous_segments_total_content_size
            # SEGMENT_CONTENT
            elif segment_pos < self._segment_header_length + new_segment_size:
                self._current_region = SMRegion.SEGMENT_CONTENT
                self._current_region_offset = segment_pos - self._segment_header_length
                self._content_offset = previous_segments_total_content_size + self._current_region_offset
            # SEGMENT_FOOTER
            else:
                self._current_region = SMRegion.SEGMENT_FOOTER
                self._current_region_offset = segment_pos - self._segment_header_length - new_segment_size
                self._content_offset = previous_segments_total_content_size + new_segment_size

            self._current_segment_number = new_segment_num

        self._update_current_region_length()
        self._inner_stream.seek((self._initial_content_position or 0) + self._content_offset)
        return position

    def read(self, size: int = -1) -> bytes:
        if self.closed:  # pylint: disable=using-constant-test
            raise ValueError("Stream is closed")

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
                count += self._read_content(remaining, output)
            else:
                raise ValueError(f"Invalid SMRegion {self._current_region}")

        return output.getvalue()

    def _calculate_message_length(self) -> int:
        length = self._message_header_length
        length += (self._segment_header_length + self._segment_footer_length) * self._num_segments
        length += self.content_length
        length += self._message_footer_length
        return length

    def _get_metadata_region(self, region: SMRegion) -> bytes:
        if region == SMRegion.MESSAGE_HEADER:
            return generate_message_header(
                self.message_version,
                self.message_length,
                self.flags,
                self._num_segments)

        if region == SMRegion.SEGMENT_HEADER:
            segment_size = min(self._segment_size, self.content_length - self._content_offset)
            return generate_segment_header(self._current_segment_number, segment_size)

        if region == SMRegion.SEGMENT_FOOTER:
            if StructuredMessageProperties.CRC64 in self.flags:
                return self._segment_crc64s[self._current_segment_number].to_bytes(
                    StructuredMessageConstants.CRC64_LENGTH, 'little')
            return b''

        if region == SMRegion.MESSAGE_FOOTER:
            if StructuredMessageProperties.CRC64 in self.flags:
                return self._message_crc64.to_bytes(StructuredMessageConstants.CRC64_LENGTH, 'little')
            return b''

        raise ValueError(f"Invalid metadata SMRegion {self._current_region}")

    def _advance_region(self, current: SMRegion):
        self._current_region_offset = 0

        if current == SMRegion.MESSAGE_HEADER:
            self._current_region = SMRegion.SEGMENT_HEADER
            self._increment_current_segment()
        elif current == SMRegion.SEGMENT_HEADER:
            self._current_region = SMRegion.SEGMENT_CONTENT
        elif current == SMRegion.SEGMENT_CONTENT:
            self._current_region = SMRegion.SEGMENT_FOOTER
        elif current == SMRegion.SEGMENT_FOOTER:
            # If we're at the end of the content
            if self._content_offset == self.content_length:
                self._current_region = SMRegion.MESSAGE_FOOTER
            else:
                self._current_region = SMRegion.SEGMENT_HEADER
                self._increment_current_segment()
        else:
            raise ValueError(f"Invalid SMRegion {self._current_region}")

        self._update_current_region_length()

    def _read_metadata_region(self, region: SMRegion, size: int, output: BytesIO) -> int:
        metadata = self._get_metadata_region(region)

        read_size = min(size, self._current_region_length - self._current_region_offset)
        content = metadata[self._current_region_offset: self._current_region_offset + read_size]
        output.write(content)

        self._current_region_offset += read_size
        if (self._current_region_offset == self._current_region_length and
                self._current_region != SMRegion.MESSAGE_FOOTER):
            self._advance_region(region)

        return read_size

    def _read_content(self, size: int, output: BytesIO) -> int:
        # Will be non-zero if there is data to read that does not need to have checksum calculated.
        # Will always be positive as stream can only seek backwards.
        checksum_offset = self._checksum_offset - self._content_offset

        read_size = min(size, self._current_region_length - self._current_region_offset)
        if checksum_offset != 0:
            # Only read up to checksum offset this iteration
            read_size = min(read_size, checksum_offset)

        content = self._inner_stream.read(read_size)
        if len(content) != read_size:
            raise ValueError("Content ended early when encoding structured message.")
        output.write(content)

        if StructuredMessageProperties.CRC64 in self.flags:
            if checksum_offset == 0:
                self._segment_crc64s[self._current_segment_number] = \
                    calculate_crc64(content, self._segment_crc64s[self._current_segment_number])
                self._message_crc64 = calculate_crc64(content, self._message_crc64)

        self._content_offset += read_size
        # Only update the checksum offset if we've read new data
        if self._content_offset > self._checksum_offset:
            self._checksum_offset += read_size
        self._current_region_offset += read_size
        if self._current_region_offset == self._current_region_length:
            self._advance_region(SMRegion.SEGMENT_CONTENT)

        return read_size

    def _increment_current_segment(self):
        self._current_segment_number += 1
        if StructuredMessageProperties.CRC64 in self.flags:
            # If seek was used, we may already have this segment's CRC (could be partial), otherwise initialize to 0
            self._segment_crc64s.setdefault(self._current_segment_number, 0)


class StructuredMessageDecodeStream(IOBase):  # pylint: disable=too-many-instance-attributes

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
        
        # Validate that inner stream is positioned at the start of the structured message
        try:
            initial_position = self._inner_stream.tell()
            if initial_position != 0:
                raise ValueError(
                    f"Inner stream must be positioned at the start of the structured message. "
                    f"Current position is {initial_position}, expected 0."
                )
        except (AttributeError, UnsupportedOperation, OSError):
            # Stream doesn't support tell(), assume it's at the correct position
            pass
        
        self._message_offset = 0
        self._message_crc64 = 0

        self._segment_number = 0
        self._segment_crc64 = 0
        self._segment_content_length = 0
        self._segment_content_offset = 0
        super().__init__()

    @property
    def _segment_header_length(self) -> int:
        return StructuredMessageConstants.V1_SEGMENT_HEADER_LENGTH

    @property
    def _segment_footer_length(self) -> int:
        return StructuredMessageConstants.CRC64_LENGTH if StructuredMessageProperties.CRC64 in self.flags else 0

    @property
    def _message_footer_length(self) -> int:
        return StructuredMessageConstants.CRC64_LENGTH if StructuredMessageProperties.CRC64 in self.flags else 0

    @property
    def _end_of_segment_content(self) -> bool:
        return self._segment_content_offset == self._segment_content_length

    def close(self) -> None:
        self._inner_stream.close()
        super().close()

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return False

    def read(self, size: int = -1) -> bytes:
        if self.closed:
            raise ValueError("Stream is closed")

        if size == 0 or self._message_offset >= self.message_length:
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
                    raise ValueError("First message segment was empty but more segments were detected.")
                self._read_message_footer()
                return b''

        count = 0
        content = BytesIO()
        while count < size and not (self._end_of_segment_content and self._message_offset == self.message_length):
            if self._end_of_segment_content:
                self._read_segment_header()

            segment_remaining = self._segment_content_length - self._segment_content_offset
            read_size = min(segment_remaining, size - count)

            segment_content = self._read_from_inner(read_size)
            content.write(segment_content)

            # Update the running CRC64 for the segment and message
            if StructuredMessageProperties.CRC64 in self.flags:
                self._segment_crc64 = calculate_crc64(segment_content, self._segment_crc64)
                self._message_crc64 = calculate_crc64(segment_content, self._message_crc64)

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
            raise ValueError("Invalid structured message data detected.")

        return content.getvalue()

    def _read_from_inner(self, size: int) -> bytes:
        data = self._inner_stream.read(size)
        if len(data) != size:
            raise ValueError("Invalid structured message data detected. Stream content incomplete.")
        return data

    def _read_message_header(self) -> None:
        # The first byte should always be the message version
        self.message_version = int.from_bytes(self._read_from_inner(1), 'little')

        if self.message_version == 1:
            message_length = int.from_bytes(self._read_from_inner(8), 'little')
            if message_length != self.message_length:
                raise ValueError(f"Structured message length {message_length} "
                                 f"did not match content length {self.message_length}")

            self.flags = StructuredMessageProperties(int.from_bytes(self._read_from_inner(2), 'little'))
            self.num_segments = int.from_bytes(self._read_from_inner(2), 'little')

            self._message_offset += StructuredMessageConstants.V1_HEADER_LENGTH

        else:
            raise ValueError(f"The structured message version is not supported: {self.message_version}")

    def _read_message_footer(self) -> None:
        # Sanity check: There should only be self._message_footer_length (could be 0) bytes left to consume.
        # If not, it is likely the message header contained incorrect info.
        if self.message_length - self._message_offset != self._message_footer_length:
            raise ValueError("Invalid structured message data detected.")

        if StructuredMessageProperties.CRC64 in self.flags:
            message_crc = self._read_from_inner(StructuredMessageConstants.CRC64_LENGTH)

            if self._message_crc64 != int.from_bytes(message_crc, 'little'):
                raise ValueError("CRC64 mismatch detected in message trailer. "
                                 "All data read should be considered invalid.")

        self._message_offset += self._message_footer_length

    def _read_segment_header(self) -> None:
        segment_number = int.from_bytes(self._read_from_inner(2), 'little')
        if segment_number != self._segment_number + 1:
            raise ValueError(f"Structured message segment number invalid or out of order {segment_number}")
        self._segment_number = segment_number
        self._segment_content_length = int.from_bytes(self._read_from_inner(8), 'little')
        self._message_offset += self._segment_header_length

        self._segment_content_offset = 0
        self._segment_crc64 = 0

    def _read_segment_footer(self) -> None:
        if StructuredMessageProperties.CRC64 in self.flags:
            segment_crc = self._read_from_inner(StructuredMessageConstants.CRC64_LENGTH)

            if self._segment_crc64 != int.from_bytes(segment_crc, 'little'):
                raise ValueError(f"CRC64 mismatch detected in segment {self._segment_number}. "
                                 f"All data read should be considered invalid.")

        self._message_offset += self._segment_footer_length

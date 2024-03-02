# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
from enum import IntFlag, auto
from io import BytesIO
from typing import IO

from azure.storage.extensions import crc64


class StructuredMessageError(Exception):
    pass


class StructuredMessageConstants:
    V1_HEADER_LENGTH = 13
    V1_SEGMENT_HEADER_LENGTH = 10
    CRC64_LENGTH = 8


class StructuredMessageProperties(IntFlag):
    NONE = 0
    CRC64 = auto()


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

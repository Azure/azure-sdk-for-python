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


class StructuredMessageConstants:
    V1_HEADER_LENGTH = 13
    V1_SEGMENT_HEADER_LENGTH = 10
    CRC64_LENGTH = 8


class StructuredMessageProperties(IntFlag):
    NONE = 0
    CRC64 = auto()


def verify_crc64(data: bytes, expected_crc: bytes) -> None:
    actual_crc = crc64.compute_crc64(data, 0).to_bytes(StructuredMessageConstants.CRC64_LENGTH, 'little')
    if actual_crc != expected_crc:
        raise ValueError("CRC64 mismatch detected.")


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
    _segment_number: int
    _segment_content: bytes
    _segment_content_length: int
    _segment_content_offset: int

    def __init__(self, inner_stream: IO[bytes], content_length: int) -> None:
        self.message_length = content_length
        # The stream should be at least long enough to hold minimum header length
        if self.message_length < StructuredMessageConstants.V1_HEADER_LENGTH:
            raise ValueError("Content not long enough to contain a valid message header.")

        self._inner_stream = inner_stream
        self._message_offset = 0

        self._segment_number = 0
        self._segment_content = b''
        self._segment_content_length = 0
        self._segment_content_offset = 0

    @property
    def _end_of_segment(self) -> bool:
        return self._segment_content_offset == self._segment_content_length

    @property
    def _end_of_message(self) -> bool:
        return self._message_offset == self.message_length

    def read(self, size: int = -1) -> bytes:
        if size == 0:
            return b''
        if size < 0:
            size = sys.maxsize

        # On the first read, read the header and first segment
        if self._message_offset == 0:
            self._read_message_header()
            self._read_segment()

        count = 0
        content = BytesIO()
        while count < size and not (self._end_of_segment and self._end_of_message):
            if self._end_of_segment:
                self._read_segment()

            remaining_segment_size = self._segment_content_length - self._segment_content_offset
            read_length = min((size - count), remaining_segment_size)

            segment_content = self._segment_content[self._segment_content_offset:
                                                    self._segment_content_offset + read_length]
            self._segment_content_offset += read_length

            content.write(segment_content)
            count += read_length

        return content.getvalue()

    def _read_message_header(self) -> None:
        # The first byte should always be the message version
        self.message_version = int.from_bytes(self._inner_stream.read(1), 'little')

        if self.message_version == 1:
            message_length = int.from_bytes(self._inner_stream.read(8), 'little')
            if message_length != self.message_length:
                raise ValueError(f"Structured message length {message_length} "
                                 f"did not match content length {self.message_length}")

            self.flags = StructuredMessageProperties(int.from_bytes(self._inner_stream.read(2), 'little'))
            self.num_segments = int.from_bytes(self._inner_stream.read(2), 'little')

            self._message_offset += StructuredMessageConstants.V1_HEADER_LENGTH

        else:
            raise ValueError(f"The structured message version is not supported: {self.message_version}")

    def _read_message_footer(self) -> None:
        # V1 does not have a message footer
        pass

    def _read_segment(self) -> None:
        self._read_segment_header()
        self._read_segment_content()
        self._read_segment_footer()

    def _read_segment_header(self) -> None:
        segment_number = int.from_bytes(self._inner_stream.read(2), 'little')
        if segment_number != self._segment_number + 1:
            raise ValueError(f"Structured message segment number invalid or out of order {segment_number}")
        self._segment_number = segment_number
        self._segment_content_length = int.from_bytes(self._inner_stream.read(8), 'little')
        self._segment_content_offset = 0

        self._message_offset += StructuredMessageConstants.V1_SEGMENT_HEADER_LENGTH

    def _read_segment_content(self) -> None:
        self._segment_content = self._inner_stream.read(self._segment_content_length)
        self._message_offset += self._segment_content_length

    def _read_segment_footer(self) -> None:
        footer_length = 0
        if StructuredMessageProperties.CRC64 in self.flags:
            segment_crc = self._inner_stream.read(StructuredMessageConstants.CRC64_LENGTH)
            footer_length += StructuredMessageConstants.CRC64_LENGTH

            verify_crc64(self._segment_content, segment_crc)

        self._message_offset += footer_length

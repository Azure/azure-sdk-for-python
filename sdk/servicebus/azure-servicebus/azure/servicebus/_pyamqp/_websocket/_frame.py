# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from dataclasses import dataclass
import io
import os
import struct
import enum

from ._exceptions import WebSocketPayloadError, WebSocketProtocolError
from ._utils import mask_payload


class Opcode(enum.IntEnum):
    CONTINUATION = 0x00
    TEXT = 0x01
    BINARY = 0x02
    CLOSE = 0x08
    PING = 0x09
    PONG = 0x0A

FRAMES = {
    Opcode.CONTINUATION,
    Opcode.TEXT,
    Opcode.BINARY,
    Opcode.CLOSE,
    Opcode.PING,
    Opcode.PONG
}

CONTROL_FRAMES = {
    Opcode.CLOSE,
    Opcode.PING,
    Opcode.PONG,
}

DATA_FRAMES = {
    Opcode.TEXT,
    Opcode.BINARY,
    Opcode.CONTINUATION,
}


class CloseReason(enum.IntEnum):
    '''
    The status codes for the close frame as per RFC 6455.
    https://datatracker.ietf.org/doc/html/rfc6455#section-7.4.1
   '''
    NORMAL = 1000
    GOING_AWAY = 1001
    PROTOCOL_ERROR = 1002
    UNSUPPORTED_DATA = 1003
    NO_STATUS_RCVD = 1005
    ABNORMAL_CLOSURE = 1006
    INVALID_PAYLOAD = 1007
    POLICY_VIOLATION = 1008
    MESSAGE_TOO_BIG = 1009
    MANDATORY_EXT = 1010
    INTERNAL_ERROR = 1011
    SERVICE_RESTART = 1012
    TRY_AGAIN_LATER = 1013
    BAD_GATEWAY = 1014
    TLS_HANDSHAKE = 1015

ALLOWED_CLOSED_REASONS = {
    CloseReason.NORMAL,
    CloseReason.GOING_AWAY,
    CloseReason.PROTOCOL_ERROR,
    CloseReason.UNSUPPORTED_DATA,
    CloseReason.INVALID_PAYLOAD,
    CloseReason.POLICY_VIOLATION,
    CloseReason.MESSAGE_TOO_BIG,
    CloseReason.MANDATORY_EXT,
    CloseReason.INTERNAL_ERROR,
    CloseReason.SERVICE_RESTART,
    CloseReason.TRY_AGAIN_LATER,
    CloseReason.BAD_GATEWAY,
}


@dataclass
class Frame:
    """
    Represents a WebSocket frame
    """
    data: bytes
    opcode: int = Opcode.TEXT
    fin: bool = True
    mask: bool = True
    rsv1: int = 0
    rsv2: int = 0
    rsv3: int = 0

    def encode(self) -> bytes:
        output = io.BytesIO()

        header = output.write(struct.pack('!B', # pylint: disable=unused-variable
                             (
                                    self.fin << 7 |  # FIN
                                    self.rsv1 << 6 |  # RSV1
                                    self.rsv2 << 5 |  # RSV2
                                    self.rsv3 << 4 |  # RSV3
                                    self.opcode
                             )))
        mask_bit = 1 << 7
        length = len(self.data)
        payload = bytearray(self.data)

        if length < 126:
            output.write(struct.pack('!B', mask_bit | length))
        elif length < 65536:
            output.write(struct.pack('!BH', mask_bit | 126, length))
        else:
            output.write(struct.pack('!BQ', mask_bit | 127, length))

        if self.mask:
            masking_key = os.urandom(4)
            output.write(masking_key)
            mask_payload(masking_key, payload)
        output.write(payload)

        return output.getvalue()

    def validate(self) -> None:
        """
        Validate the frame according to the RFC 6455
        """
        if self.rsv1 or self.rsv2 or self.rsv3:
            raise WebSocketProtocolError("Reserved bits are set")

        if self.opcode not in FRAMES:
            raise WebSocketProtocolError(f"Invalid opcode {self.opcode}. Expected one of {FRAMES}")

        # Validations for control frames
        # https://datatracker.ietf.org/doc/html/rfc6455#section-5.5

        if self.opcode in CONTROL_FRAMES:
            if not self.fin:
                raise WebSocketProtocolError("Control frames must not be fragmented")

            if len(self.data) > 125:
                raise WebSocketProtocolError(f"Control frames must not be larger than 125 bytes. Got {len(self.data)}")

            if self.opcode == Opcode.CLOSE:
                if not self.data:
                    return

                payload_length = len(self.data)

                # if there is a body, it must be at least 2 bytes long in order to contain the status code
                # https://datatracker.ietf.org/doc/html/rfc6455#section-5.5.1
                if payload_length <= 1:
                    raise WebSocketProtocolError("Close frame with payload length of less than 2 bytes")

                code = struct.unpack('!H', self.data[:2])[0]
                payload = self.data[2:]

                if not (code in ALLOWED_CLOSED_REASONS or 3000 <= code <= 4999):
                    raise WebSocketProtocolError(f"Invalid close code {code}")

                try:
                    payload.decode("utf-8")
                except UnicodeDecodeError as ude:
                    raise WebSocketPayloadError('Invalid UTF-8 payload') from ude

        elif self.opcode == Opcode.TEXT and self.fin:
            try:
                self.data.decode("utf-8")
            except UnicodeDecodeError as ude:
                raise WebSocketPayloadError('Invalid UTF-8 payload') from ude
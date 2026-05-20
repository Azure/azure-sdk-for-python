# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
# cSpell:ignore phdr

from typing import Any, Iterator

# Special marker for "break" stop code in indefinite-length items
_CBOR_BREAK = object()


class CBORDecoder:
    """Simple CBOR decoder without external dependencies.

    Implements RFC 8949 (CBOR) decoding for all major types:
    - Major type 0: Unsigned integers
    - Major type 1: Negative integers
    - Major type 2: Byte strings (definite and indefinite length)
    - Major type 3: Text strings (definite and indefinite length)
    - Major type 4: Arrays (definite and indefinite length)
    - Major type 5: Maps (definite and indefinite length)
    - Major type 6: Tags
    - Major type 7: Simple values and floats
    """

    def __init__(self, data: bytes):
        """Initialize a CBORDecoder with raw CBOR data.

        :param data: The CBOR-encoded bytes to decode.
        :type data: bytes
        """
        self.data = data
        self.pos = 0

    @staticmethod
    def from_response(response: Iterator[bytes]) -> "CBORDecoder":
        """Create a CBORDecoder instance from an iterator of bytes.

        This is useful for decoding API responses directly.

        :param response: An iterator yielding bytes chunks (e.g., from an API response).
        :type response: Iterator[bytes]
        :return: A CBORDecoder instance initialized with the concatenated bytes.
        :rtype: CBORDecoder

        Example usage::

            resp = client.get_entry(...)
            decoded = CBORDecoder.from_response(resp).decode()
        """
        data = b"".join(response)
        return CBORDecoder(data)

    def decode(  # pylint: disable=too-many-return-statements
        self, allow_break: bool = False
    ) -> Any:
        """Decode the next CBOR item.

        :param allow_break: If True, allow "break" stop code and return the internal
            _CBOR_BREAK sentinel. Defaults to False.
        :type allow_break: bool
        :return: The decoded value. The type depends on the CBOR major type:
            int, bytes, str, list, dict, bool, None, float, or a dict for tags/simple values.
        :rtype: Any
        :raises ValueError: If the data is not well-formed CBOR.
        """
        if len(self.data) == 0:
            raise ValueError("No CBOR data to decode")

        if self.pos >= len(self.data):
            raise ValueError("Unexpected end of CBOR data")

        initial_byte = self.data[self.pos]
        self.pos += 1

        major_type = (initial_byte >> 5) & 0x07
        additional_info = initial_byte & 0x1F

        # Check for reserved additional info values (RFC 8949 Section 3)
        if additional_info in (28, 29, 30):
            raise ValueError(f"Reserved additional info value: {additional_info}")

        # Handle "break" stop code (0xFF = major type 7, additional info 31)
        if major_type == 7 and additional_info == 31:
            if allow_break:
                return _CBOR_BREAK
            raise ValueError(
                "Unexpected 'break' stop code outside indefinite-length item"
            )

        # Check for indefinite length (additional info 31) - only valid for types 2-5
        if additional_info == 31:
            if major_type in (0, 1, 6):
                raise ValueError(
                    f"Indefinite length not allowed for major type {major_type}"
                )
            return self._decode_indefinite(major_type)

        if major_type == 0:  # Unsigned integer
            return self._decode_unsigned(additional_info)
        if major_type == 1:  # Negative integer (-1 - n)
            return -1 - self._decode_unsigned(additional_info)
        if major_type == 2:  # Byte string
            length = self._decode_unsigned(additional_info)
            if self.pos + length > len(self.data):
                raise ValueError("Byte string length exceeds available data")
            byte_value = self.data[self.pos : self.pos + length]
            self.pos += length
            return byte_value
        if major_type == 3:  # Text string (UTF-8)
            length = self._decode_unsigned(additional_info)
            if self.pos + length > len(self.data):
                raise ValueError("Text string length exceeds available data")
            text_value = self.data[self.pos : self.pos + length].decode("utf-8")
            self.pos += length
            return text_value
        if major_type == 4:  # Array
            count = self._decode_unsigned(additional_info)
            return [self.decode() for _ in range(count)]
        if major_type == 5:  # Map
            count = self._decode_unsigned(additional_info)
            result = {}
            for _ in range(count):
                key = self.decode()
                value = self.decode()
                result[key] = value
            return result
        if major_type == 6:  # Tag
            tag_number = self._decode_unsigned(additional_info)
            tagged_value = self.decode()
            return {"tag": tag_number, "value": tagged_value}
        if major_type == 7:  # Simple values and floats
            return self._decode_simple_or_float(additional_info)

        raise ValueError(f"Unknown CBOR major type: {major_type}")

    def _decode_unsigned(self, additional_info: int) -> int:
        """Decode an unsigned integer based on additional info (RFC 8949 Section 3).

        :param additional_info: The 5-bit additional info from the CBOR initial byte.
            Values 0-23 are the value itself, 24-27 indicate extended byte lengths.
        :type additional_info: int
        :return: The decoded unsigned integer value.
        :rtype: int
        :raises ValueError: If there is insufficient data or invalid additional info.
        """
        if additional_info < 24:
            return additional_info
        if additional_info == 24:
            if self.pos >= len(self.data):
                raise ValueError("Unexpected end of data reading uint8")
            value = self.data[self.pos]
            self.pos += 1
            return value
        if additional_info == 25:
            if self.pos + 2 > len(self.data):
                raise ValueError("Unexpected end of data reading uint16")
            value = int.from_bytes(self.data[self.pos : self.pos + 2], "big")
            self.pos += 2
            return value
        if additional_info == 26:
            if self.pos + 4 > len(self.data):
                raise ValueError("Unexpected end of data reading uint32")
            value = int.from_bytes(self.data[self.pos : self.pos + 4], "big")
            self.pos += 4
            return value
        if additional_info == 27:
            if self.pos + 8 > len(self.data):
                raise ValueError("Unexpected end of data reading uint64")
            value = int.from_bytes(self.data[self.pos : self.pos + 8], "big")
            self.pos += 8
            return value

        # Should not reach here due to earlier checks
        raise ValueError(f"Invalid additional info: {additional_info}")

    def _decode_indefinite(self, major_type: int) -> Any:
        """Decode indefinite-length items (RFC 8949 Section 3.2).

        Indefinite-length items are terminated by the "break" stop code (0xFF).

        :param major_type: The CBOR major type (2=byte string, 3=text string,
            4=array, 5=map).
        :type major_type: int
        :return: The decoded value: bytes, str, list, or dict depending on major_type.
        :rtype: Union[bytes, str, list, dict]
        :raises ValueError: If the major type doesn't support indefinite length or
            if chunks are not of the correct type.
        """
        if major_type == 2:  # Indefinite-length byte string
            chunks: list[bytes] = []
            while True:
                item = self.decode(allow_break=True)
                if item is _CBOR_BREAK:
                    break
                if not isinstance(item, bytes):
                    raise ValueError(
                        "Indefinite byte string chunk must be definite-length byte string"
                    )
                chunks.append(item)
            return b"".join(chunks)
        if major_type == 3:  # Indefinite-length text string
            text_chunks: list[str] = []
            while True:
                item = self.decode(allow_break=True)
                if item is _CBOR_BREAK:
                    break
                if not isinstance(item, str):
                    raise ValueError(
                        "Indefinite text string chunk must be definite-length text string"
                    )
                text_chunks.append(item)
            return "".join(text_chunks)
        if major_type == 4:  # Indefinite-length array
            items = []
            while True:
                item = self.decode(allow_break=True)
                if item is _CBOR_BREAK:
                    break
                items.append(item)
            return items
        if major_type == 5:  # Indefinite-length map
            result = {}
            while True:
                key = self.decode(allow_break=True)
                if key is _CBOR_BREAK:
                    break
                value = self.decode(allow_break=False)  # Value cannot be break
                result[key] = value
            return result

        raise ValueError(f"Indefinite length not supported for major type {major_type}")

    def _decode_simple_or_float(  # pylint: disable=too-many-return-statements
        self, additional_info: int
    ) -> Any:  # pylint: disable=too-many-return-statements
        """Decode simple values and floats (RFC 8949 Section 3.3).

        :param additional_info: The 5-bit additional info from the CBOR initial byte.
        :type additional_info: int
        :return: The decoded value: False, True, None, float, or a dict
            for undefined/unassigned simple values (e.g., {"simple": n}).
        :rtype: Union[bool, None, float, dict]
        :raises ValueError: If there is insufficient data or invalid encoding.
        """
        if additional_info < 20:
            # Unassigned simple value 0-19
            return {"simple": additional_info}
        if additional_info == 20:
            return False
        if additional_info == 21:
            return True
        if additional_info == 22:
            return None  # null
        if additional_info == 23:
            return {"undefined": True}  # undefined (distinct from null)
        if additional_info == 24:
            # Two-byte simple value encoding
            if self.pos >= len(self.data):
                raise ValueError("Unexpected end of data reading simple value")
            simple_val = self.data[self.pos]
            self.pos += 1
            # RFC 8949: Simple values 0-31 MUST NOT use two-byte encoding
            if simple_val < 32:
                raise ValueError(
                    f"Invalid two-byte encoding for simple value {simple_val}"
                )
            return {"simple": simple_val}
        if additional_info == 25:  # Half-precision float (16-bit)
            if self.pos + 2 > len(self.data):
                raise ValueError("Unexpected end of data reading half-precision float")
            half = int.from_bytes(self.data[self.pos : self.pos + 2], "big")
            self.pos += 2
            return self._decode_half_float(half)
        if additional_info == 26:  # Single-precision float (32-bit)
            import struct

            if self.pos + 4 > len(self.data):
                raise ValueError(
                    "Unexpected end of data reading single-precision float"
                )
            value = struct.unpack(">f", self.data[self.pos : self.pos + 4])[0]
            self.pos += 4
            return value
        if additional_info == 27:  # Double-precision float (64-bit)
            import struct

            if self.pos + 8 > len(self.data):
                raise ValueError(
                    "Unexpected end of data reading double-precision float"
                )
            value = struct.unpack(">d", self.data[self.pos : self.pos + 8])[0]
            self.pos += 8
            return value

        # Simple values 24-31 without extension byte are unassigned
        return {"simple": additional_info}

    def _decode_half_float(self, half: int) -> float:
        """Decode IEEE 754 half-precision float (binary16).

        Format (16 bits): 1 sign + 5 exponent + 10 mantissa.
        Implementation based on RFC 8949 Appendix D.

        :param half: The 16-bit integer representation of the half-precision float.
        :type half: int
        :return: The decoded floating-point value.
        :rtype: float
        """
        import struct
        from math import ldexp

        def decode_single(single: int) -> float:
            """Convert 32-bit integer to single-precision float."""
            return struct.unpack("!f", struct.pack("!I", single))[0]

        # Shift mantissa and exponent to single-precision position,
        # preserve sign bit
        value = (half & 0x7FFF) << 13 | (half & 0x8000) << 16

        if (half & 0x7C00) != 0x7C00:
            # Not infinity or NaN - scale the value
            return ldexp(decode_single(value), 112)

        # Infinity or NaN - set exponent to all 1s for single precision
        return decode_single(value | 0x7F800000)

    def decode_cose_sign1(self) -> dict:
        """Decode a COSE_Sign1 structure.

        :return: A dictionary representation of the COSE_Sign1 structure with keys:

            - **protected_headers** (*dict*): The decoded protected headers map.
            - **unprotected_headers** (*dict*): The unprotected headers map.
            - **payload** (*bytes*): The payload bytes.
            - **signature** (*bytes*): The signature bytes.
            - **was_tagged** (*bool*): True if the structure was tagged with COSE_Sign1 tag (18).

        :rtype: dict
        :raises ValueError: If the data is not a well-formed COSE_Sign1 structure.
        """
        cose_structure = self.decode()

        # Handle COSE_Sign1 structure (tag 18)
        was_tagged = (
            isinstance(cose_structure, dict) and cose_structure.get("tag") == 18
        )
        if was_tagged:
            cose_structure = cose_structure["value"]

        if not isinstance(cose_structure, list) or len(cose_structure) != 4:
            raise ValueError("Invalid COSE_Sign1 structure")

        protected_headers_bytes = cose_structure[0]
        unprotected_headers = cose_structure[1]
        payload_bytes = cose_structure[2]
        signature_bytes = cose_structure[3]

        # Decode protected headers
        protected_headers = {}
        if (
            isinstance(protected_headers_bytes, bytes)
            and len(protected_headers_bytes) > 0
        ):
            phdr_decoder = CBORDecoder(protected_headers_bytes)
            protected_headers = phdr_decoder.decode()
            if not isinstance(protected_headers, dict):
                protected_headers = {}

        # Decode nested CWT header if present in protected headers under the label 15
        cwt_header_bytes = protected_headers.get(15)
        if isinstance(cwt_header_bytes, bytes) and len(cwt_header_bytes) > 0:
            cwt_decoder = CBORDecoder(cwt_header_bytes)
            cwt_headers = cwt_decoder.decode()
            if isinstance(cwt_headers, dict):
                # replace the CWT header bytes with the decoded headers
                protected_headers[15] = cwt_headers

        return {
            "protected_headers": protected_headers,
            "unprotected_headers": (
                unprotected_headers if isinstance(unprotected_headers, dict) else {}
            ),
            "payload": payload_bytes,
            "signature": signature_bytes,
            "was_tagged": was_tagged,
        }

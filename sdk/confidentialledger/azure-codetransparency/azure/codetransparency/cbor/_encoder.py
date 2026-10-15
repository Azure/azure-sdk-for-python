# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from typing import Any, Dict, List, Optional, Union
import struct
from math import isnan, isinf


class CBOREncoder:
    """Simple CBOR encoder without external dependencies.

    Implements RFC 8949 (CBOR) encoding for all major types:
    - Major type 0: Unsigned integers
    - Major type 1: Negative integers
    - Major type 2: Byte strings
    - Major type 3: Text strings (UTF-8)
    - Major type 4: Arrays
    - Major type 5: Maps
    - Major type 6: Tags
    - Major type 7: Simple values and floats
    """

    def __init__(self) -> None:
        """Initialize a CBOREncoder with an empty buffer."""
        self._buffer: bytearray = bytearray()

    def encode(self, value: Any) -> bytes:
        """Encode a Python value to CBOR format.

        :param value: The Python value to encode.
        :type value: Any
        :return: The CBOR-encoded bytes.
        :rtype: bytes

        Example usage::

            encoder = CBOREncoder()
            encoded = encoder.encode({"key": "value", "number": 42})
        """
        self._buffer = bytearray()
        self._encode_value(value)
        return bytes(self._buffer)

    @staticmethod
    def encode_value(value: Any) -> bytes:
        """Convenience static method to encode a value directly.

        :param value: The Python value to encode.
        :type value: Any
        :return: The CBOR-encoded bytes.
        :rtype: bytes

        Example usage::

            encoded = CBOREncoder.encode_value({"key": "value"})
        """
        encoder = CBOREncoder()
        return encoder.encode(value)

    def _encode_value(self, value: Any) -> None:
        """Encode a single value and append to the buffer.

        :param value: The Python value to encode.
        :type value: Any
        :raises ValueError: If the value type is not supported for CBOR encoding.
        """
        if value is None:
            self._encode_null()
        elif isinstance(value, bool):
            # Must check bool before int since bool is a subclass of int
            self._encode_bool(value)
        elif isinstance(value, int):
            self._encode_int(value)
        elif isinstance(value, float):
            self._encode_float(value)
        elif isinstance(value, bytes):
            self._encode_bytes(value)
        elif isinstance(value, str):
            self._encode_string(value)
        elif isinstance(value, (list, tuple)):
            self._encode_array(value)
        elif isinstance(value, dict):
            # Check for special tagged value representation
            if "tag" in value and "value" in value and len(value) == 2:
                self._encode_tag(value["tag"], value["value"])
            # Check for simple value representation
            elif "simple" in value and len(value) == 1:
                self._encode_simple(value["simple"])
            # Check for undefined representation
            elif "undefined" in value and value.get("undefined") is True:
                self._encode_undefined()
            else:
                self._encode_map(value)
        else:
            raise ValueError(f"Cannot encode type: {type(value).__name__}")

    def _encode_initial_byte(self, major_type: int, additional_info: int) -> None:
        """Encode the initial byte with major type and additional info.

        :param major_type: The CBOR major type (0-7).
        :type major_type: int
        :param additional_info: The 5-bit additional info value (0-31).
        :type additional_info: int
        """
        self._buffer.append((major_type << 5) | additional_info)

    def _encode_unsigned(self, major_type: int, value: int) -> None:
        """Encode an unsigned integer with the given major type (RFC 8949 Section 3).

        :param major_type: The CBOR major type (0-7).
        :type major_type: int
        :param value: The unsigned integer value to encode.
        :type value: int
        :raises ValueError: If the value is negative or too large to encode.
        """
        if value < 0:
            raise ValueError("Cannot encode negative value as unsigned")

        if value <= 23:
            self._encode_initial_byte(major_type, value)
        elif value <= 0xFF:
            self._encode_initial_byte(major_type, 24)
            self._buffer.append(value)
        elif value <= 0xFFFF:
            self._encode_initial_byte(major_type, 25)
            self._buffer.extend(value.to_bytes(2, "big"))
        elif value <= 0xFFFFFFFF:
            self._encode_initial_byte(major_type, 26)
            self._buffer.extend(value.to_bytes(4, "big"))
        elif value <= 0xFFFFFFFFFFFFFFFF:
            self._encode_initial_byte(major_type, 27)
            self._buffer.extend(value.to_bytes(8, "big"))
        else:
            raise ValueError(f"Integer too large to encode: {value}")

    def _encode_int(self, value: int) -> None:
        """Encode an integer (major type 0 for positive, major type 1 for negative).

        :param value: The integer value to encode.
        :type value: int
        """
        if value >= 0:
            # Major type 0: Unsigned integer
            self._encode_unsigned(0, value)
        else:
            # Major type 1: Negative integer (-1 - n)
            # The encoded value is -1 - value, which equals abs(value) - 1
            self._encode_unsigned(1, -1 - value)

    def _encode_bytes(self, value: bytes) -> None:
        """Encode a byte string (major type 2).

        :param value: The byte string to encode.
        :type value: bytes
        """
        self._encode_unsigned(2, len(value))
        self._buffer.extend(value)

    def _encode_string(self, value: str) -> None:
        """Encode a text string as UTF-8 (major type 3).

        :param value: The text string to encode.
        :type value: str
        """
        encoded = value.encode("utf-8")
        self._encode_unsigned(3, len(encoded))
        self._buffer.extend(encoded)

    def _encode_array(self, value: Union[List[Any], tuple]) -> None:
        """Encode an array (major type 4).

        :param value: The list or tuple to encode as a CBOR array.
        :type value: Union[List[Any], tuple]
        """
        self._encode_unsigned(4, len(value))
        for item in value:
            self._encode_value(item)

    def _encode_map(self, value: Dict[Any, Any]) -> None:
        """Encode a map (major type 5).

        :param value: The dictionary to encode as a CBOR map.
        :type value: Dict[Any, Any]
        """
        self._encode_unsigned(5, len(value))
        for k, v in value.items():
            self._encode_value(k)
            self._encode_value(v)

    def _encode_tag(self, tag_number: int, tagged_value: Any) -> None:
        """Encode a tagged value (major type 6).

        :param tag_number: The CBOR tag number (must be non-negative).
        :type tag_number: int
        :param tagged_value: The value to be tagged.
        :type tagged_value: Any
        :raises ValueError: If tag_number is negative.
        """
        if tag_number < 0:
            raise ValueError(f"Tag number must be non-negative: {tag_number}")
        self._encode_unsigned(6, tag_number)
        self._encode_value(tagged_value)

    def _encode_bool(self, value: bool) -> None:
        """Encode a boolean (major type 7, simple values 20/21).

        :param value: The boolean value to encode.
        :type value: bool
        """
        if value:
            self._encode_initial_byte(7, 21)  # true
        else:
            self._encode_initial_byte(7, 20)  # false

    def _encode_null(self) -> None:
        """Encode null (major type 7, simple value 22)."""
        self._encode_initial_byte(7, 22)

    def _encode_undefined(self) -> None:
        """Encode undefined (major type 7, simple value 23)."""
        self._encode_initial_byte(7, 23)

    def _encode_simple(self, value: int) -> None:
        """Encode a simple value (major type 7).

        :param value: The simple value to encode (0-255).
        :type value: int
        :raises ValueError: If value is not in the range 0-255.
        """
        if value < 0 or value > 255:
            raise ValueError(f"Simple value must be 0-255: {value}")

        if value <= 23:
            self._encode_initial_byte(7, value)
        else:
            # Two-byte encoding for values 32-255
            # RFC 8949: Simple values 0-31 MUST NOT use two-byte encoding
            self._encode_initial_byte(7, 24)
            self._buffer.append(value)

    def _encode_float(self, value: float) -> None:
        """Encode a floating-point number (major type 7).

        Uses the smallest representation that preserves the value:
        half-precision (16-bit), single-precision (32-bit), or
        double-precision (64-bit).

        :param value: The floating-point value to encode.
        :type value: float
        """
        # Handle special values
        if isnan(value):
            # Encode NaN as half-precision
            self._encode_initial_byte(7, 25)
            self._buffer.extend(b"\x7e\x00")  # Canonical NaN
            return

        if isinf(value):
            # Encode infinity as half-precision
            self._encode_initial_byte(7, 25)
            if value > 0:
                self._buffer.extend(b"\x7c\x00")  # +Infinity
            else:
                self._buffer.extend(b"\xfc\x00")  # -Infinity
            return

        # Try half-precision first
        half_encoded = self._try_encode_half(value)
        if half_encoded is not None:
            self._encode_initial_byte(7, 25)
            self._buffer.extend(half_encoded)
            return

        # Try single-precision
        single_encoded = struct.pack(">f", value)
        single_decoded = struct.unpack(">f", single_encoded)[0]
        if single_decoded == value:
            self._encode_initial_byte(7, 26)
            self._buffer.extend(single_encoded)
            return

        # Fall back to double-precision
        self._encode_initial_byte(7, 27)
        self._buffer.extend(struct.pack(">d", value))

    def _try_encode_half(self, value: float) -> Optional[bytes]:  # pylint: disable=too-many-return-statements
        """Try to encode a float as half-precision (16-bit IEEE 754).

        Format (16 bits): 1 sign + 5 exponent + 10 mantissa.

        :param value: The floating-point value to encode.
        :type value: float
        :return: The encoded bytes if the value can be represented exactly
            in half-precision, or None if it would lose precision.
        :rtype: Optional[bytes]
        """
        # Convert to single precision first to get the bit pattern
        single_bytes = struct.pack(">f", value)
        single_int = struct.unpack(">I", single_bytes)[0]

        # Extract components from single precision
        sign = (single_int >> 31) & 0x1
        exponent = (single_int >> 23) & 0xFF
        mantissa = single_int & 0x7FFFFF

        # Check for zero
        if exponent == 0 and mantissa == 0:
            half = sign << 15
            return half.to_bytes(2, "big")

        # Check for denormalized numbers in single precision
        if exponent == 0:
            # Denormalized single - likely too small for half
            return None

        # Convert exponent from single (bias 127) to half (bias 15)
        # Single exponent range: 1-254 (0 and 255 are special)
        # Half exponent range: 1-30 (0 and 31 are special)
        half_exponent = exponent - 127 + 15

        # Check if exponent is in valid half-precision range
        if half_exponent <= 0:
            # Value is too small - would become denormalized or zero in half
            # Try to encode as denormalized half-precision
            if half_exponent >= -10:
                # Shift mantissa right to create denormalized value
                shift = 1 - half_exponent
                half_mantissa = (mantissa | 0x800000) >> (13 + shift)
                # Check if this loses precision
                reconstructed = half_mantissa << (13 + shift)
                if reconstructed != (mantissa | 0x800000):
                    return None
                half = (sign << 15) | half_mantissa
                return half.to_bytes(2, "big")
            return None

        if half_exponent >= 31:
            # Value is too large for half-precision
            return None

        # Check if mantissa fits in 10 bits (truncating 13 bits from 23)
        if mantissa & 0x1FFF != 0:
            # Would lose precision
            return None

        half_mantissa = mantissa >> 13
        half = (sign << 15) | (half_exponent << 10) | half_mantissa
        return half.to_bytes(2, "big")

    def encode_cose_sign1(
        self,
        protected_headers: Dict[Any, Any],
        unprotected_headers: Dict[Any, Any],
        payload: bytes,
        signature: bytes,
        include_tag: bool = True,
    ) -> bytes:
        """Encode a COSE_Sign1 structure.

        :param protected_headers: The protected headers as a dictionary.
        :type protected_headers: Dict[Any, Any]
        :param unprotected_headers: The unprotected headers as a dictionary.
        :type unprotected_headers: Dict[Any, Any]
        :param payload: The payload bytes.
        :type payload: bytes
        :param signature: The signature bytes.
        :type signature: bytes
        :param include_tag: Whether to include the COSE_Sign1 tag (18).
        :type include_tag: bool
        :return: The CBOR-encoded COSE_Sign1 structure.
        :rtype: bytes

        Example usage::

            encoder = CBOREncoder()
            encoded = encoder.encode_cose_sign1(
                protected_headers={1: -7},  # alg: ES256
                unprotected_headers={},
                payload=b"example payload",
                signature=b"signature bytes"
            )
        """
        self._buffer = bytearray()

        # Encode protected headers to bytes
        protected_encoder = CBOREncoder()
        protected_bytes = protected_encoder.encode(protected_headers) if protected_headers else b""

        # Build the COSE_Sign1 array: [protected, unprotected, payload, signature]
        cose_array = [
            protected_bytes,
            unprotected_headers if unprotected_headers else {},
            payload,
            signature,
        ]

        if include_tag:
            # Tag 18 for COSE_Sign1
            self._encode_value({"tag": 18, "value": cose_array})
        else:
            self._encode_value(cose_array)

        return bytes(self._buffer)

    def encode_indefinite_bytes(self, chunks: List[bytes]) -> bytes:
        """Encode an indefinite-length byte string from chunks.

        :param chunks: List of byte string chunks.
        :type chunks: List[bytes]
        :return: The CBOR-encoded indefinite-length byte string.
        :rtype: bytes
        """
        self._buffer = bytearray()
        # Major type 2, additional info 31 (indefinite length)
        self._encode_initial_byte(2, 31)
        for chunk in chunks:
            self._encode_bytes(chunk)
        # Break stop code
        self._buffer.append(0xFF)
        return bytes(self._buffer)

    def encode_indefinite_string(self, chunks: List[str]) -> bytes:
        """Encode an indefinite-length text string from chunks.

        :param chunks: List of text string chunks.
        :type chunks: List[str]
        :return: The CBOR-encoded indefinite-length text string.
        :rtype: bytes
        """
        self._buffer = bytearray()
        # Major type 3, additional info 31 (indefinite length)
        self._encode_initial_byte(3, 31)
        for chunk in chunks:
            self._encode_string(chunk)
        # Break stop code
        self._buffer.append(0xFF)
        return bytes(self._buffer)

    def encode_indefinite_array(self, items: List[Any]) -> bytes:
        """Encode an indefinite-length array.

        :param items: List of items to encode.
        :type items: List[Any]
        :return: The CBOR-encoded indefinite-length array.
        :rtype: bytes
        """
        self._buffer = bytearray()
        # Major type 4, additional info 31 (indefinite length)
        self._encode_initial_byte(4, 31)
        for item in items:
            self._encode_value(item)
        # Break stop code
        self._buffer.append(0xFF)
        return bytes(self._buffer)

    def encode_indefinite_map(self, items: Dict[Any, Any]) -> bytes:
        """Encode an indefinite-length map.

        :param items: Dictionary of key-value pairs to encode.
        :type items: Dict[Any, Any]
        :return: The CBOR-encoded indefinite-length map.
        :rtype: bytes
        """
        self._buffer = bytearray()
        # Major type 5, additional info 31 (indefinite length)
        self._encode_initial_byte(5, 31)
        for k, v in items.items():
            self._encode_value(k)
            self._encode_value(v)
        # Break stop code
        self._buffer.append(0xFF)
        return bytes(self._buffer)

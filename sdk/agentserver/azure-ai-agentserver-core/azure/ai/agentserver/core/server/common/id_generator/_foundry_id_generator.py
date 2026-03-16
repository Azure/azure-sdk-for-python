# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import annotations

import base64
import os
import re
from typing import Optional

from ._id_generator import IdGenerator

_WATERMARK_RE = re.compile(r"^[A-Za-z0-9]*$")


class FoundryIdGenerator(IdGenerator):
    """
    Python port of the C# FoundryIdGenerator.

    Notable behaviors preserved:
      - Secure, alphanumeric entropy via base64 filtering, retrying until exact length.
      - Watermark must be strictly alphanumeric; inserted mid-entropy.
      - Only one delimiter (default "_") after the prefix; no delimiter between entropy and partition key.
      - Partition key is the last N characters of the second ID segment (post-delimiter).
    """

    def __init__(self, response_id: Optional[str], conversation_id: Optional[str]):
        """Initialize the ID generator.

        :param response_id: An existing response ID, or ``None`` to generate one.
        :type response_id: Optional[str]
        :param conversation_id: An existing conversation ID, or ``None``.
        :type conversation_id: Optional[str]
        """
        self.response_id = response_id or self._new_id("resp")
        self.conversation_id = conversation_id
        partition_source = self.conversation_id or self.response_id
        try:
            self._partition_id = self._extract_partition_id(partition_source)
        except ValueError:
            self._partition_id = self._secure_entropy(18)

    @classmethod
    def from_request(cls, payload: dict) -> "FoundryIdGenerator":
        """Create a generator from an incoming request payload.

        :param payload: The raw request payload dictionary.
        :type payload: dict
        :return: A configured :class:`FoundryIdGenerator` instance.
        :rtype: FoundryIdGenerator
        """
        response_id = payload.get("metadata", {}).get("response_id", None)
        conv_id_raw = payload.get("conversation", None)
        if isinstance(conv_id_raw, str):
            conv_id = conv_id_raw
        elif isinstance(conv_id_raw, dict):
            conv_id = conv_id_raw.get("id", None)  # type: ignore[assignment]
        else:
            conv_id = None
        return cls(response_id, conv_id)

    def generate(self, category: Optional[str] = None) -> str:
        """Generate a new unique ID for the given category.

        :param category: Optional prefix category (e.g. ``"msg"``, ``"func"``).  Defaults to ``"id"``.
        :type category: Optional[str]
        :return: The generated unique identifier string.
        :rtype: str
        """
        prefix = "id" if not category else category
        return self._new_id(prefix, partition_key=self._partition_id)

    # --- Static helpers (mirror C# private static methods) --------------------

    @staticmethod
    def _new_id(
        prefix: str,
        string_length: int = 32,
        partition_key_length: int = 18,
        infix: Optional[str] = "",
        watermark: str = "",
        delimiter: str = "_",
        partition_key: Optional[str] = None,
        partition_key_hint: str = "",
    ) -> str:
        """Generate a new ID matching the C# FoundryIdGenerator format.

        Format: ``"{prefix}{delimiter}{infix}{partitionKey}{entropy}"``

        :param prefix: The ID prefix (e.g. ``"resp"``, ``"msg"``).
        :type prefix: str
        :param string_length: Length of the random entropy portion.
        :type string_length: int
        :param partition_key_length: Length of the partition key.
        :type partition_key_length: int
        :param infix: Optional infix inserted between delimiter and partition key.
        :type infix: Optional[str]
        :param watermark: Optional alphanumeric watermark inserted mid-entropy.
        :type watermark: str
        :param delimiter: Delimiter between prefix and the rest of the ID.
        :type delimiter: str
        :param partition_key: Explicit partition key; if ``None``, derived or generated.
        :type partition_key: Optional[str]
        :param partition_key_hint: ID string to extract a partition key from.
        :type partition_key_hint: str
        :return: The generated ID string.
        :rtype: str
        :raises ValueError: If the watermark contains non-alphanumeric characters.
        """
        entropy = FoundryIdGenerator._secure_entropy(string_length)

        if partition_key is not None:
            pkey = partition_key
        elif partition_key_hint:
            pkey = FoundryIdGenerator._extract_partition_id(
                partition_key_hint,
                string_length=string_length,
                partition_key_length=partition_key_length,
                delimiter=delimiter,
            )
        else:
            pkey = FoundryIdGenerator._secure_entropy(partition_key_length)

        if watermark:
            if not _WATERMARK_RE.fullmatch(watermark):
                raise ValueError(f"Only alphanumeric characters may be in watermark: {watermark}")
            half = string_length // 2
            entropy = f"{entropy[:half]}{watermark}{entropy[half:]}"

        infix = infix or ""
        prefix_part = f"{prefix}{delimiter}" if prefix else ""
        return f"{prefix_part}{infix}{pkey}{entropy}"

    @staticmethod
    def _secure_entropy(string_length: int) -> str:
        """Generate a cryptographically secure alphanumeric string.

        Uses :func:`os.urandom` and base64 encoding, filtering to alphanumeric
        characters and retrying until the exact length is reached.

        :param string_length: Desired length of the output string.
        :type string_length: int
        :return: A random alphanumeric string of exactly *string_length* characters.
        :rtype: str
        :raises ValueError: If *string_length* is less than 1.
        """
        if string_length < 1:
            raise ValueError("Must be greater than or equal to 1")

        while True:
            # Use cryptographically secure bytes; base64 then filter to alnum.
            buf = os.urandom(string_length)
            encoded = base64.b64encode(buf).decode("ascii")
            alnum = "".join(ch for ch in encoded if ch.isalnum())
            if len(alnum) >= string_length:
                return alnum[:string_length]
            # else: retry, same as the C# loop which discards and regenerates

    @staticmethod
    def _extract_partition_id(
        id_str: str,
        string_length: int = 32,
        partition_key_length: int = 18,
        delimiter: str = "_",
    ) -> str:
        """Extract the partition key from an existing ID.

        Expected shape: ``"<prefix>_<infix+partitionKey+entropy>"``.
        Returns the first *partition_key_length* characters of the second segment.

        :param id_str: The ID string to extract from.
        :type id_str: str
        :param string_length: Expected entropy length used for validation.
        :type string_length: int
        :param partition_key_length: Number of characters to extract as partition key.
        :type partition_key_length: int
        :param delimiter: The delimiter separating ID segments.
        :type delimiter: str
        :return: The extracted partition key.
        :rtype: str
        :raises ValueError: If the ID format is invalid.
        """
        if not id_str:
            raise ValueError("Id cannot be null or empty")

        parts = [p for p in id_str.split(delimiter) if p]  # remove empty entries like C# Split(..., RemoveEmptyEntries)
        if len(parts) < 2:
            raise ValueError(f"Id '{id_str}' does not contain a valid partition key.")

        segment = parts[1]
        if len(segment) < string_length + partition_key_length:
            raise ValueError(f"Id '{id_str}' does not contain a valid id.")

        return segment[:partition_key_length]

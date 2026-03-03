# pylint: disable=docstring-missing-return,docstring-missing-param,docstring-missing-rtype
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import annotations

import base64
import os
import re
from typing import Optional

from .id_generator import IdGenerator

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
        self.response_id = response_id or self._new_id("resp")
        self.conversation_id = conversation_id or self._new_id("conv")
        self._partition_id = self._extract_partition_id(self.conversation_id)

    @classmethod
    def from_request(cls, payload: dict) -> "FoundryIdGenerator":
        response_id = payload.get("metadata", {}).get("response_id", None)
        conv_id_raw = payload.get("conversation", None)
        if isinstance(conv_id_raw, str):
            conv_id = conv_id_raw
        elif isinstance(conv_id_raw, dict):
            conv_id = conv_id_raw.get("id", None)
        else:
            conv_id = None
        return cls(response_id, conv_id)

    def generate(self, category: Optional[str] = None) -> str:
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
        """
        Generates a new ID.

        Format matches the C# logic:
            f"{prefix}{delimiter}{infix}{partitionKey}{entropy}"
        (i.e., exactly one delimiter after prefix; no delimiter between entropy and partition key)
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
        return f"{prefix_part}{entropy}{infix}{pkey}"

    @staticmethod
    def _secure_entropy(string_length: int) -> str:
        """
        Generates a secure random alphanumeric string of exactly `string_length`.
        Re-tries whole generation until the filtered base64 string is exactly the desired length,
        matching the C# behavior.
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
        """
        Extracts partition key from an existing ID.

        Expected shape (per C# logic): "<prefix>_<infix+partitionKey+entropy>"
        We take the last `partition_key_length` characters from the *second* segment.
        """
        if not id_str:
            raise ValueError("Id cannot be null or empty")

        parts = [p for p in id_str.split(delimiter) if p]  # remove empty entries like C# Split(..., RemoveEmptyEntries)
        if len(parts) < 2:
            raise ValueError(f"Id '{id_str}' does not contain a valid partition key.")

        segment = parts[1]
        if len(segment) < string_length + partition_key_length:
            raise ValueError(f"Id '{id_str}' does not contain a valid id.")

        return segment[-partition_key_length:]

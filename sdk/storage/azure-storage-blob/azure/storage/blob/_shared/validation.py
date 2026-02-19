# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=c-extension-no-member

from enum import Enum
from typing import cast

from azure.core import CaseInsensitiveEnumMeta

CRC64_LENGTH = 8


class ChecksumAlgorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    AUTO = "auto"
    MD5 = "md5"
    CRC64 = "crc64"


def calculate_crc64(data: bytes, initial_crc: int) -> int:
    # Locally import to avoid error if not installed.
    from azure.storage.extensions import crc64

    return cast(int, crc64.compute(data, initial_crc))


def calculate_crc64_bytes(data: bytes) -> bytes:
    # Locally import to avoid error if not installed.
    from azure.storage.extensions import crc64

    return cast(bytes, crc64.compute(data, 0).to_bytes(CRC64_LENGTH, 'little'))

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=c-extension-no-member
from __future__ import annotations

import hashlib
from enum import Enum
from typing import Optional, Union

from azure.core import CaseInsensitiveEnumMeta

CRC64_LENGTH = 8
SM_HEADER_V1_CRC64 = "XSM/1.0; properties=crc64"


class ChecksumAlgorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    AUTO = "auto"
    MD5 = "md5"
    CRC64 = "crc64"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


def _verify_extensions(module: str) -> None:
    try:
        import azure.storage.extensions  # pylint: disable=unused-import
    except ImportError as exc:
        raise ValueError(f"The use of {module} requires the azure-storage-extensions package to be installed. "
                         f"Please install this package and try again.") from exc


def parse_validation_option(validate_content: Optional[Union[bool, str]]) -> Optional[Union[bool, str]]:
    if validate_content is None:
        return None

    # Legacy support for bool
    if isinstance(validate_content, bool):
        return validate_content

    if validate_content not in (ChecksumAlgorithm.list()):
        raise ValueError("Invalid value for `validate_content` specified.")

    # Resolve auto
    if validate_content == ChecksumAlgorithm.AUTO:
        validate_content = ChecksumAlgorithm.CRC64.lower()

    if validate_content == ChecksumAlgorithm.CRC64:
        _verify_extensions("CRC64")

    return validate_content


def calculate_md5(data: bytes) -> bytes:
    md5 = hashlib.md5()  # nosec
    md5.update(data)
    return md5.digest()


def calculate_crc64(data: bytes, initial_crc: int) -> int:
    # Locally import to avoid error if not installed.
    from azure.storage.extensions import crc64

    return crc64.compute_crc64(data, initial_crc)


def calculate_crc64_bytes(data: bytes) -> bytes:
    # Locally import to avoid error if not installed.
    from azure.storage.extensions import crc64

    return crc64.compute_crc64(data, 0).to_bytes(CRC64_LENGTH, 'little')

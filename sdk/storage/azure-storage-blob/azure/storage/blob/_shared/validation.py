# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=c-extension-no-member

import hashlib
from enum import Enum
from io import SEEK_SET
from typing import IO, Literal, Optional, Union, cast

from azure.core import CaseInsensitiveEnumMeta

CRC64_LENGTH = 8
CV_TYPE_ERROR_MSG = "Data should be bytes or seekable IO[bytes] for content validation."

CV_TYPE = Optional[Union[bool, Literal["auto", "crc64", "md5"]]]
CV_TYPE_PARSED = Optional[Union[bool, Literal["crc64", "md5"]]]


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
        raise ValueError(
            f"The use of {module} requires the azure-storage-extensions package to be installed. "
            f"Please install this package and try again."
        ) from exc


def parse_validation_option(
    validate_content: CV_TYPE,
) -> CV_TYPE_PARSED:
    if validate_content is None:
        return None

    # Legacy support for bool
    if isinstance(validate_content, bool):
        return validate_content

    if validate_content not in (ChecksumAlgorithm.list()):
        raise ValueError("Invalid value for `validate_content` specified.")

    # Resolve auto
    if validate_content == ChecksumAlgorithm.AUTO:
        validate_content = ChecksumAlgorithm.CRC64.value

    if validate_content == ChecksumAlgorithm.CRC64:
        _verify_extensions("crc64")

    return cast(CV_TYPE_PARSED, validate_content)


def is_md5_validation(
    validate_content: CV_TYPE_PARSED,
) -> bool:
    if validate_content is None:
        return False
    if isinstance(validate_content, bool):
        return validate_content
    return validate_content == ChecksumAlgorithm.MD5


def calculate_content_md5(data: Union[bytes, IO[bytes]]) -> bytes:
    md5 = hashlib.md5()  # nosec
    if isinstance(data, bytes):
        md5.update(data)
    elif hasattr(data, "read"):
        pos = 0
        try:
            pos = data.tell()
        except:  # pylint: disable=bare-except
            pass
        for chunk in iter(lambda: data.read(4096), b""):
            md5.update(chunk)
        try:
            data.seek(pos, SEEK_SET)
        except (AttributeError, IOError) as exc:
            raise ValueError(CV_TYPE_ERROR_MSG) from exc
    else:
        raise ValueError(CV_TYPE_ERROR_MSG)

    return md5.digest()


def calculate_crc64(data: bytes, initial_crc: int) -> int:
    # Locally import to avoid error if not installed.
    from azure.storage.extensions import crc64

    return cast(int, crc64.compute(data, initial_crc))


def calculate_crc64_bytes(data: bytes) -> bytes:
    # Locally import to avoid error if not installed.
    from azure.storage.extensions import crc64

    return cast(bytes, crc64.compute(data, 0).to_bytes(CRC64_LENGTH, "little"))

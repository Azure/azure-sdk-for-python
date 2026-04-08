# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=c-extension-no-member

import hashlib
from io import SEEK_SET
from typing import IO, Literal, Optional, Union, cast

CRC64_LENGTH = 8
CV_TYPE_ERROR_MSG = "Data should be bytes or seekable IO[bytes] for content validation."

_VALID_CV_OPTIONS = ("auto", "crc64", "md5")

CV_TYPE = Optional[Union[bool, Literal["auto", "crc64", "md5"]]]
CV_TYPE_PARSED = Optional[Union[bool, Literal["crc64", "md5"]]]


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

    validate_content = validate_content.lower()
    if validate_content not in _VALID_CV_OPTIONS:
        raise ValueError("Invalid value for `validate_content` specified.")

    # Resolve auto
    if validate_content == "auto":
        validate_content = "crc64"

    if validate_content == "crc64":
        _verify_extensions("crc64")

    return cast(CV_TYPE_PARSED, validate_content)


def is_md5_validation(
    validate_content: CV_TYPE_PARSED,
) -> bool:
    if validate_content is None:
        return False
    if isinstance(validate_content, bool):
        return validate_content
    return validate_content == "md5"


def is_crc64_validation(
    validate_content: CV_TYPE_PARSED,
) -> bool:
    if validate_content is None:
        return False
    if isinstance(validate_content, bool):
        return False
    return validate_content == "crc64"


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

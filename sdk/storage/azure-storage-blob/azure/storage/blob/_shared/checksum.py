# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import base64
import hashlib
from typing import Any, Literal, Optional, Tuple

from ..crc64 import compute_crc64


def get_content_checksum(checksum: str, data: bytes) -> Tuple[Optional[bytes], Optional[bytes]]:
    content_md5, content_crc64 = None, None
    if checksum == 'md5':
        content_md5 = _calculate_content_md5(data)
    elif checksum == 'crc64':
        content_crc64 = _calculate_content_crc64(data)
    return content_md5, content_crc64


def parse_checksum_response_headers(response) -> Tuple[Optional[bytes], Optional[bytes]]:
    content_md5, content_crc64 = None, None

    headers = response.headers
    if 'Content-MD5' in headers:
        content_md5 = headers['Content-MD5']
        content_md5 = base64.b64decode(content_md5)
    elif 'x-ms-content-crc64' in headers:
        content_crc64 = headers['x-ms-content-crc64']
        content_crc64 = base64.b64decode(content_crc64)

    return content_md5, content_crc64


def verify_download_checksum(response: Any, data: bytes, checksum: str) -> None:
    server_checksum, content_checksum = None, None

    if checksum == 'md5':
        server_checksum = response.headers['Content-MD5']
        if not server_checksum:
            raise ValueError("MD5 was not returned in response.")

        content_checksum = _calculate_content_md5(data)

    elif checksum == 'crc64':
        server_checksum = response.headers['x-ms-content-crc64']
        if not server_checksum:
            raise ValueError("CRC64 was not returned in response.")

        content_checksum = _calculate_content_crc64(data)

    server_checksum = base64.b64decode(server_checksum)
    if server_checksum != content_checksum:
        raise ValueError("Checksum did not match server checksum!")


def _calculate_content_md5(data: bytes) -> bytes:
    md5 = hashlib.md5()
    md5.update(data)
    return md5.digest()


def _calculate_content_crc64(data: bytes) -> bytes:
    crc64 = compute_crc64(data, 0)
    return crc64.to_bytes(8, 'little')

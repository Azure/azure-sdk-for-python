# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from hashlib import sha1
import os
import base64
from typing import Dict, List, Tuple, Optional
from ._constants import WS_KEY


def build_request_headers(
        resource: str,
        host: str,
        port: int,
        is_secure: bool,
        key: bytes,
        *,
        subprotocols: Optional[List[str]] = None
    ) -> bytes:
    request: List[bytes] = [
        f'GET {resource} HTTP/1.1'.encode(),
    ]
    origin: str = 'https://' if is_secure else 'http://'
    origin = f'{origin}{build_host(host, port)}'

    headers: Dict[bytes, bytes] = {
        b'Host: ': build_host(host, port).encode(),
        b'Connection: ': b'Upgrade',
        b'Upgrade: ': b'websocket',
        b'Origin: ': origin.encode(),
        b'Sec-WebSocket-Key: ': key,
        b'Sec-WebSocket-Version: ': b'13'
    }

    if subprotocols:
        headers[b'Sec-WebSocket-Protocol: '] = ','.join(subprotocols).encode()

    for header, value in headers.items():
        request.append(header + value)

    request.append(b'\r\n')
    request_bytes: bytes = b'\r\n'.join(request)
    return request_bytes

def build_host(host: str, port: int) -> str:
    if ':' in host:
        return f'[{host}]:{port}'

    if port in (80, 443):
        return host

    return f'{host}:{port}'

def build_key() -> bytes:
    random_bytes: bytes = os.urandom(16)
    return base64.b64encode(random_bytes)

def match_key(client_header_key: bytes, server_header_key: bytes) -> bool:
    # the use of sha1 is a websocket protocol requirement and is used for hashing and not cryptography
    # other impls have the same behavior
    # websocket spec: https://datatracker.ietf.org/doc/html/rfc6455
    # https://github.com/dotnet/runtime/blob/45caaf85faa654114f7a3744910df86d8e92882f/src/libraries/System.Net.HttpListener/src/System/Net/WebSockets/HttpWebSocket.cs#L18
    match = base64.b64encode(sha1(client_header_key + WS_KEY).digest()).lower() # nosec

    return match == server_header_key

def parse_response_headers(response_headers: bytes) -> Tuple[bytes, bytes,  Dict[bytes, bytes]]:
    response_line = response_headers.split(b'\r\n')[0]
    _, code, status = response_line.split(b' ', 2)

    headers: Dict[bytes, bytes] = {}

    for header in response_headers.split(b'\r\n')[1:]:
        if not header:
            break
        key, value = header.split(b': ')
        headers[key.lower()] = value.lower()

    return code, status, headers

def parse_proxy_response(response_headers: bytes) -> Tuple[bytes, bytes, bytes]:
    if not response_headers:
        return b'', b'', b''

    response_line = response_headers.split(b'\r\n')[0]

    try:
        version, status, reason = response_line.split(b' ', 2)
    except ValueError:
        try:
            version, status = response_line.split(b' ', 1)
            reason = b''
        except ValueError:
            version = b''

    return version, status, reason
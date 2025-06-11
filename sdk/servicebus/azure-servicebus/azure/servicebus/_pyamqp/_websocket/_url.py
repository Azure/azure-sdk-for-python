# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from urllib.parse import ParseResult, urlparse
from dataclasses import dataclass


@dataclass
class WebSocketURL:
    scheme: str
    hostname: str
    port: int
    path: str
    query: str
    fragment: str
    is_secure: bool

def parse_url(url: str) -> WebSocketURL:
    parsed_url: ParseResult = urlparse(url)
    if parsed_url.scheme not in ('ws', 'wss'):
        raise ValueError('Scheme must be ws or wss')
    if not parsed_url.hostname:
        raise ValueError('Provided hostname is invalid')
    if not parsed_url.port:
        port = 80 if parsed_url.scheme == 'ws' else 443
    if not parsed_url.path:
        path = '/'
    else:
        path = parsed_url.path

    return WebSocketURL(
        scheme=parsed_url.scheme,
        hostname=parsed_url.hostname,
        port=port if not parsed_url.port else parsed_url.port,
        path=path,
        query=parsed_url.query,
        fragment=parsed_url.fragment,
        is_secure=parsed_url.scheme == 'wss'
    )
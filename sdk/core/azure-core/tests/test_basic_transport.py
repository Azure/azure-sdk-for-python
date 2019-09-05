# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import time

from azure.core.pipeline.transport import HttpRequest

def test_http_request_serialization():
    # Method + Url
    request = HttpRequest("DELETE", "/container0/blob0")
    serialized = request.serialize()

    expected = b'DELETE /container0/blob0 HTTP/1.1\r\n\r\n'
    assert serialized == expected

    # Method + Url + Headers
    request = HttpRequest(
        "DELETE",
        "/container0/blob0",
        headers={
            "x-ms-date": "Thu, 14 Jun 2018 16:46:54 GMT",
            "Authorization": "SharedKey account:G4jjBXA7LI/RnWKIOQ8i9xH4p76pAQ+4Fs4R1VxasaE=",
            "Content-Length": "0",
        }
    )
    serialized = request.serialize()

    expected = (
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'Authorization: SharedKey account:G4jjBXA7LI/RnWKIOQ8i9xH4p76pAQ+4Fs4R1VxasaE=\r\n'
        b'Content-Length: 0\r\n\r\n'
    )
    assert serialized == expected


    # Method + Url + Headers + Body
    request = HttpRequest(
        "DELETE",
        "/container0/blob0",
        headers={
            "x-ms-date": "Thu, 14 Jun 2018 16:46:54 GMT",
        },
    )
    request.set_bytes_body(b"I am groot")
    serialized = request.serialize()

    expected = (
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'Content-Length: 10\r\n'
        b'\r\n'
        b'I am groot'
    )
    assert serialized == expected

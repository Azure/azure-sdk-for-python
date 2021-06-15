# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
import concurrent.futures
import pytest
import requests.utils

from azure.core.pipeline.transport import HttpRequest, RequestsTransport, RequestsTransportResponse
from azure.core.configuration import Configuration


def test_threading_basic_requests():
    # Basic should have the session for all threads, it's why it's not recommended
    sender = RequestsTransport()
    main_thread_session = sender.session

    def thread_body(local_sender):
        # Should be the same session - we are no longer managing a session per thread.
        assert local_sender.session is main_thread_session

        return True

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(thread_body, sender)
        assert future.result()

def test_requests_auto_headers():
    request = HttpRequest("POST", "https://www.bing.com/")
    with RequestsTransport() as sender:
        response = sender.send(request)
        auto_headers = response.internal_response.request.headers
        assert 'Content-Type' not in auto_headers

def _create_requests_response(body_bytes, headers=None):
    # https://github.com/psf/requests/blob/67a7b2e8336951d527e223429672354989384197/requests/adapters.py#L255
    req_response = requests.Response()
    req_response._content = body_bytes
    req_response._content_consumed = True
    req_response.status_code = 200
    req_response.reason = 'OK'
    if headers:
        # req_response.headers is type CaseInsensitiveDict
        req_response.headers.update(headers)
    req_response.encoding = requests.utils.get_encoding_from_headers(req_response.headers)

    response = RequestsTransportResponse(
        None, # Don't need a request here
        req_response
    )

    return response


def test_requests_response_text():

    for encoding in ["utf-8", "utf-8-sig", None]:

        res = _create_requests_response(
            b'\xef\xbb\xbf56',
            {'Content-Type': 'text/plain'}
        )
        assert res.text(encoding) == '56', "Encoding {} didn't work".format(encoding)

def test_repr():
    res = _create_requests_response(
        b'\xef\xbb\xbf56',
        {'Content-Type': 'text/plain'}
    )
    assert repr(res) == "<RequestsTransportResponse: 200 OK, Content-Type: text/plain>"

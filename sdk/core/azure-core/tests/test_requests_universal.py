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
import requests.utils
import pytest
from azure.core.pipeline.transport import RequestsTransport
from utils import HTTP_REQUESTS, REQUESTS_TRANSPORT_RESPONSES, create_transport_response
from azure.core.pipeline._tools import is_rest


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

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_requests_auto_headers(port, http_request):
    request = http_request("POST", "http://localhost:{}/basic/string".format(port))
    with RequestsTransport() as sender:
        response = sender.send(request)
        auto_headers = response.internal_response.request.headers
        assert 'Content-Type' not in auto_headers

def _create_requests_response(http_response, body_bytes, headers=None):
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

    response = create_transport_response(
        http_response,
        None, # Don't need a request here
        req_response
    )

    return response

@pytest.mark.parametrize("http_response", REQUESTS_TRANSPORT_RESPONSES)
def test_requests_response_text(http_response):

    for encoding in ["utf-8", "utf-8-sig", None]:

        res = _create_requests_response(
            http_response,
            b'\xef\xbb\xbf56',
            {'Content-Type': 'text/plain'}
        )
        if is_rest(http_response):
            res.read()
        assert res.text(encoding) == '56', "Encoding {} didn't work".format(encoding)

@pytest.mark.parametrize("http_response", REQUESTS_TRANSPORT_RESPONSES)
def test_repr(http_response):
    res = _create_requests_response(
        http_response,
        b'\xef\xbb\xbf56',
        {'Content-Type': 'text/plain'}
    )
    class_name = "HttpResponse" if is_rest(http_response) else "RequestsTransportResponse"
    assert repr(res) == "<{}: 200 OK, Content-Type: text/plain>".format(class_name)

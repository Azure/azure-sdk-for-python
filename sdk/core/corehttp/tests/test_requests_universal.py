# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import concurrent.futures
import requests.utils

from corehttp.rest import HttpRequest
from corehttp.transport.requests import RequestsTransport
from corehttp.rest._requests_basic import RestRequestsTransportResponse
from utils import create_transport_response, SYNC_TRANSPORT_RESPONSES


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


def test_requests_auto_headers(port):
    request = HttpRequest("POST", "http://localhost:{}/basic/string".format(port))
    with RequestsTransport() as sender:
        response = sender.send(request)
        auto_headers = response._internal_response.request.headers
        assert "Content-Type" not in auto_headers


def _create_requests_response(http_response, body_bytes, headers=None):
    # https://github.com/psf/requests/blob/67a7b2e8336951d527e223429672354989384197/requests/adapters.py#L255
    req_response = requests.Response()
    req_response._content = body_bytes
    req_response._content_consumed = True
    req_response.status_code = 200
    req_response.reason = "OK"
    if headers:
        # req_response.headers is type CaseInsensitiveDict
        req_response.headers.update(headers)
    req_response.encoding = requests.utils.get_encoding_from_headers(req_response.headers)

    response = create_transport_response(http_response, None, req_response)  # Don't need a request here

    return response


def test_requests_response_text():
    for encoding in ["utf-8", "utf-8-sig", None]:
        res = _create_requests_response(
            RestRequestsTransportResponse, b"\xef\xbb\xbf56", {"Content-Type": "text/plain"}
        )
        res.read()
        assert res.text(encoding) == "56", "Encoding {} didn't work".format(encoding)


def test_repr():
    res = _create_requests_response(RestRequestsTransportResponse, b"\xef\xbb\xbf56", {"Content-Type": "text/plain"})
    class_name = "HttpResponse"
    assert repr(res) == "<{}: 200 OK, Content-Type: text/plain>".format(class_name)

# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Regression tests for the cross-host redirect credential-leak fix (MSRC 126697).

The legacy ``EventGridPublisherClient`` must not re-send credential headers to a
different host when following an HTTP 3xx redirect. These tests drive the client
pipeline built by ``_policies`` through a mock transport that issues a cross-host
redirect and assert the credential header is stripped from the redirected request.
"""
import time

import pytest
from requests import Response

from azure.core.credentials import AzureKeyCredential, AzureSasCredential, AccessToken
from azure.core.pipeline import Pipeline, AsyncPipeline
from azure.core.pipeline.transport import HttpTransport, AsyncHttpTransport, HttpRequest

from azure.eventgrid._legacy._publisher_client import EventGridPublisherClient
from azure.eventgrid._legacy.aio._publisher_client_async import (
    EventGridPublisherClient as EventGridPublisherClientAsync,
)

ORIGINAL_URL = "https://topic.westus-1.eventgrid.azure.net/api/events"
REDIRECT_URL = "https://redirected.example.net/api/events"


class FakeTokenCredential(object):
    def get_token(self, *scopes, **kwargs):
        return AccessToken("fake-token", int(time.time()) + 3600)


def _redirect_response():
    response = Response()
    response.status_code = 301
    response.headers["location"] = REDIRECT_URL
    return response


def _ok_response():
    response = Response()
    response.status_code = 200
    return response


CREDENTIAL_CASES = [
    (AzureKeyCredential("my-secret-key"), "aeg-sas-key", "my-secret-key"),
    (AzureSasCredential("my-sas-token"), "aeg-sas-token", "my-sas-token"),
    (FakeTokenCredential(), "Authorization", "Bearer fake-token"),
]


@pytest.mark.parametrize("credential, cred_header, cred_value", CREDENTIAL_CASES)
def test_credentials_not_leaked_on_cross_host_redirect(credential, cred_header, cred_value):
    class MockTransport(HttpTransport):
        def __init__(self):
            self.first = True
            self.redirected_headers = None

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def close(self):
            pass

        def open(self):
            pass

        def send(self, request, **kwargs):
            if self.first:
                self.first = False
                # The credential header is present on the original (in-host) request.
                assert request.headers.get(cred_header) == cred_value
                return _redirect_response()
            # After following the cross-host redirect the credential must be gone.
            self.redirected_headers = dict(request.headers)
            return _ok_response()

    transport = MockTransport()
    pipeline = Pipeline(transport=transport, policies=EventGridPublisherClient._policies(credential))
    pipeline.run(HttpRequest("POST", ORIGINAL_URL))

    assert transport.redirected_headers is not None, "cross-host redirect was not followed"
    assert not transport.redirected_headers.get(cred_header)


@pytest.mark.asyncio
@pytest.mark.parametrize("credential, cred_header, cred_value", CREDENTIAL_CASES)
async def test_credentials_not_leaked_on_cross_host_redirect_async(credential, cred_header, cred_value):
    class MockAsyncTransport(AsyncHttpTransport):
        def __init__(self):
            self.first = True
            self.redirected_headers = None

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def close(self):
            pass

        async def open(self):
            pass

        async def send(self, request, **kwargs):
            if self.first:
                self.first = False
                assert request.headers.get(cred_header) == cred_value
                return _redirect_response()
            self.redirected_headers = dict(request.headers)
            return _ok_response()

    transport = MockAsyncTransport()
    pipeline = AsyncPipeline(
        transport=transport, policies=EventGridPublisherClientAsync._policies(credential)
    )
    await pipeline.run(HttpRequest("POST", ORIGINAL_URL))

    assert transport.redirected_headers is not None, "cross-host redirect was not followed"
    assert not transport.redirected_headers.get(cred_header)

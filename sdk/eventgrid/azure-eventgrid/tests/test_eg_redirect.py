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


class AsyncFakeTokenCredential(object):
    async def get_token(self, *scopes, **kwargs):
        return AccessToken("fake-token", int(time.time()) + 3600)


def _redirect_response():
    # 307/308 preserve the original method (POST) and are followed by azure-core's
    # RedirectPolicy; a 301/302 would only be followed for GET/HEAD, so a POST publish
    # is exposed to the cross-host leak specifically via a method-preserving redirect.
    response = Response()
    response.status_code = 307
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

# The async client wraps a `TokenCredential` in `AsyncBearerTokenCredentialPolicy`
# which awaits `get_token`, so the async AAD case needs an async credential.
ASYNC_CREDENTIAL_CASES = [
    (AzureKeyCredential("my-secret-key"), "aeg-sas-key", "my-secret-key"),
    (AzureSasCredential("my-sas-token"), "aeg-sas-token", "my-sas-token"),
    (AsyncFakeTokenCredential(), "Authorization", "Bearer fake-token"),
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
@pytest.mark.parametrize("credential, cred_header, cred_value", ASYNC_CREDENTIAL_CASES)
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


@pytest.mark.parametrize("credential, cred_header, cred_value", CREDENTIAL_CASES)
def test_credentials_not_leaked_on_redirect_then_retry(credential, cred_header, cred_value):
    """A retry after a cross-host redirect (301 -> 500 -> 200) must not re-leak the credential.

    Requires azure-core >= 1.38.3, which persists the ``insecure_domain_change`` flag across
    retries so the cleanup keeps stripping the credential re-added by the auth policy.
    """

    class MockTransport(HttpTransport):
        def __init__(self):
            self.calls = 0
            self.post_redirect_headers = []

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def close(self):
            pass

        def open(self):
            pass

        def send(self, request, **kwargs):
            self.calls += 1
            if self.calls == 1:
                assert request.headers.get(cred_header) == cred_value
                return _redirect_response()
            # Every request to the redirected host - including the retry - must be clean.
            self.post_redirect_headers.append(request.headers.get(cred_header))
            if self.calls == 2:
                retryable = Response()
                retryable.status_code = 500
                return retryable
            return _ok_response()

    transport = MockTransport()
    policies = EventGridPublisherClient._policies(credential, retry_backoff_factor=0)
    pipeline = Pipeline(transport=transport, policies=policies)
    pipeline.run(HttpRequest("POST", ORIGINAL_URL))

    assert transport.calls >= 3, "expected a redirect followed by a retry"
    assert not any(transport.post_redirect_headers)

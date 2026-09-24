# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Default POST retry safety through real public sync and async client pipelines."""

from contextlib import asynccontextmanager
from copy import deepcopy
import inspect

import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.core.pipeline import AsyncPipeline, Pipeline, policies
from azure.core.pipeline.transport import AsyncHttpResponse, AsyncHttpTransport, HttpResponse, HttpTransport
from azure.core.rest import HttpRequest
from azure.core.utils import case_insensitive_dict

from azure.ai.finetuningsessions import FineTuningSessionClient
from azure.ai.finetuningsessions.aio import FineTuningSessionClient as AsyncClient


pytestmark = pytest.mark.asyncio

_ENDPOINT = "https://unit.invalid/api/projects/p"
_CREATE = _ENDPOINT + "/fine_tuning/sessions"
_GRADIENT = _CREATE + "/session_test/forward_backward"
_OPTIMIZER = _CREATE + "/session_test/optim_step"
_STATUS = _CREATE + "/session_test/request/request_test"
_SUCCESS = (200, {})
_DEFAULT_OPTIONS = [
    pytest.param({}, id="omitted"),
    pytest.param({"retry_policy": None, "policies": None, "pipeline": None}, id="explicit-none"),
]


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def asynchronous(request):
    """Exercise both public client implementations without mocking send_request."""
    return request.param


class _ResponseBody:
    """Minimal JSON response accepted by the real Azure Core policies."""

    def __init__(self, request, status, headers):
        super().__init__(request, None)
        self.status_code = status
        self.headers = case_insensitive_dict({"Content-Type": "application/json", **headers})
        self.content_type = "application/json"
        self.reason = "fixture"

    def body(self):
        """Return an empty JSON document."""
        return b"{}"

    def json(self):
        """Return the decoded fixture document."""
        return {}


class _SyncResponse(_ResponseBody, HttpResponse):
    """Synchronous transport response."""


class _AsyncResponse(_ResponseBody, AsyncHttpResponse):
    """Asynchronous transport response."""


class _RecordingTransport:
    """Record every wire attempt and replace retry sleeps with observations."""

    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.requests = []
        self.options = []
        self.sleeps = []

    def respond(self, request, response_type, options):
        """Snapshot before redirects mutate the request, then return or raise."""
        self.requests.append(deepcopy(request))
        self.options.append(dict(options))
        assert len(self.requests) <= len(self.outcomes), "Unexpected extra transport send"
        outcome = self.outcomes[len(self.requests) - 1]
        if isinstance(outcome, Exception):
            raise outcome
        status, headers = outcome
        return response_type(request, status, headers)


class _SyncTransport(_RecordingTransport, HttpTransport):
    """Synchronous scripted transport; never opens a network connection."""

    def send(self, request, **kwargs):
        return self.respond(request, _SyncResponse, kwargs)

    def open(self):
        pass

    def close(self):
        pass

    def __exit__(self, *args):
        self.close()

    def sleep(self, duration):
        self.sleeps.append(duration)


class _AsyncTransport(_RecordingTransport, AsyncHttpTransport):
    """Asynchronous scripted transport; never opens a network connection."""

    async def send(self, request, **kwargs):
        return self.respond(request, _AsyncResponse, kwargs)

    async def open(self):
        pass

    async def close(self):
        pass

    async def __aexit__(self, *args):
        await self.close()

    async def sleep(self, duration):
        self.sleeps.append(duration)


@asynccontextmanager
async def _client(asynchronous, outcomes=(), **options):
    """Use real defaults: do not pre-disable retries in this fixture."""
    transport = options.pop("transport", None)
    if transport is None:
        transport = (_AsyncTransport if asynchronous else _SyncTransport)(outcomes)
    client = (AsyncClient if asynchronous else FineTuningSessionClient)(
        _ENDPOINT, AzureKeyCredential("fixture-api-key"), transport=transport, **options
    )
    try:
        yield client, transport
    finally:
        result = client.close()
        if inspect.isawaitable(result):
            await result


async def _send(client, request, **options):
    """Send through the public API, awaiting only the asynchronous client."""
    result = client.send_request(request, **options)
    return await result if inspect.isawaitable(result) else result


@pytest.mark.parametrize("options", _DEFAULT_OPTIONS)
@pytest.mark.parametrize("url", [_CREATE, _GRADIENT, _OPTIMIZER], ids=["create", "gradient", "optimizer"])
@pytest.mark.parametrize(
    "failure",
    [(500, {}), (503, {}), (504, {}), (408, {"Retry-After": "1"}), (429, {"Retry-After": "1"})],
    ids=["500", "503", "504", "408-retry-after", "429-retry-after"],
)
async def test_default_post_failure_is_not_replayed(asynchronous, options, url, failure):
    """An ambiguous mutation response must be returned after exactly one send."""
    request = HttpRequest("POST", url, json={"seq_id": 7})
    async with _client(asynchronous, [failure, _SUCCESS], **options) as (client, transport):
        response = await _send(client, request)
        assert len(transport.requests) == 1
        assert response.status_code == failure[0]
        assert transport.requests[0].content == request.content
        assert transport.sleeps == []


@pytest.mark.parametrize("error_type", [ServiceRequestError, ServiceResponseError])
@pytest.mark.parametrize(
    "options", [{}, {"retry_total": 4, "retry_connect": 4, "retry_read": 4, "retry_on_methods": ["POST"]}]
)
async def test_post_transport_exception_is_not_replayed(asynchronous, error_type, options):
    """Neither connection nor read failures may replay POST, even with an allowlist override."""
    error = error_type("ambiguous transport failure")
    async with _client(asynchronous, [error, _SUCCESS], retry_total=4) as (client, transport):
        with pytest.raises(error_type) as caught:
            await _send(client, HttpRequest("POST", _OPTIMIZER, json={"seq_id": 7}), **options)
        assert caught.value is error
        assert len(transport.requests) == 1
        assert transport.sleeps == []


@pytest.mark.parametrize("failure", [(503, {}), (429, {"Retry-After": "1"})])
@pytest.mark.parametrize(
    "client_options,request_options",
    [
        ({"retry_total": 4, "retry_status": 4}, {}),
        ({}, {"retry_total": 4, "retry_status": 4, "retry_on_methods": ["POST"]}),
        ({"retry_total": 0}, {"retry_total": 4, "retry_status": 4, "retry_on_methods": ["POST"]}),
    ],
    ids=["client-count", "request-count", "request-overrides-client"],
)
async def test_retry_counts_cannot_opt_post_back_in(asynchronous, failure, client_options, request_options):
    """Only a caller-owned retry policy, not ordinary retry kwargs, opts POST in."""
    async with _client(asynchronous, [failure, _SUCCESS], **client_options) as (client, transport):
        response = await _send(client, HttpRequest("POST", _CREATE, json={}), **request_options)
        assert len(transport.requests) == 1
        assert response.status_code == failure[0]
        assert transport.sleeps == []
        assert all("retry_total" not in options for options in transport.options)


@pytest.mark.parametrize("failure_kind", ["503", "retry-after", "connection", "read"])
async def test_get_status_keeps_default_retries(asynchronous, failure_kind):
    """Request-status GET still retries responses and transport failures."""
    failures = {
        "503": (503, {}),
        "retry-after": (429, {"Retry-After": "1"}),
        "connection": ServiceRequestError("connection failure"),
        "read": ServiceResponseError("read failure"),
    }
    async with _client(asynchronous, [failures[failure_kind], _SUCCESS]) as (client, transport):
        response = await _send(client, HttpRequest("GET", _STATUS))
        assert response.status_code == 200
        assert [request.method for request in transport.requests] == ["GET", "GET"]
        assert transport.sleeps == ([1.0] if failure_kind == "retry-after" else [])


@pytest.mark.parametrize(
    "client_options,request_options,sends,sleeps",
    [
        ({"retry_total": 0}, {}, 1, []),
        ({"retry_total": 2, "retry_backoff_factor": 0.25}, {}, 3, [0.5]),
        ({}, {"retry_total": 0}, 1, []),
        ({"retry_total": 0}, {"retry_total": 2, "retry_backoff_factor": 0.125}, 3, [0.25]),
    ],
)
async def test_get_retry_configuration_is_preserved(asynchronous, client_options, request_options, sends, sleeps):
    """Client and per-call GET retry budgets and backoff retain Azure Core semantics."""
    async with _client(asynchronous, [(503, {}), (503, {}), _SUCCESS], **client_options) as (client, transport):
        response = await _send(client, HttpRequest("GET", _STATUS), **request_options)
        assert len(transport.requests) == sends
        assert response.status_code == (200 if sends == 3 else 503)
        assert transport.sleeps == sleeps


@pytest.mark.parametrize("options", _DEFAULT_OPTIONS)
async def test_post_guard_does_not_mutate_shared_get_retry_defaults(asynchronous, options):
    """Disabling one POST must not disable the next GET on the same client."""
    async with _client(asynchronous, [(503, {}), (503, {}), _SUCCESS], **options) as (client, transport):
        budget = client._config.retry_policy.total_retries
        assert (await _send(client, HttpRequest("POST", _CREATE, json={}))).status_code == 503
        assert (await _send(client, HttpRequest("GET", _STATUS))).status_code == 200
        assert [request.method for request in transport.requests] == ["POST", "GET", "GET"]
        assert client._config.retry_policy.total_retries == budget


@pytest.mark.parametrize("failure_kind", ["503", "retry-after", "connection", "read"])
@pytest.mark.parametrize("budget", [0, 1])
async def test_explicit_retry_policy_owns_post_replay(asynchronous, failure_kind, budget):
    """An explicit sync/async retry policy is preserved, including its POST behavior."""
    failures = {
        "503": (503, {}),
        "retry-after": (429, {"Retry-After": "1"}),
        "connection": ServiceRequestError("connection failure"),
        "read": ServiceResponseError("read failure"),
    }
    failure = failures[failure_kind]
    retry = (policies.AsyncRetryPolicy if asynchronous else policies.RetryPolicy)(retry_total=budget)
    async with _client(asynchronous, [failure, _SUCCESS], retry_policy=retry) as (client, transport):
        request = HttpRequest("POST", _OPTIMIZER, json={"seq_id": 7})
        assert client._config.retry_policy is retry
        if budget == 0 and isinstance(failure, Exception):
            with pytest.raises(type(failure)) as caught:
                await _send(client, request, retry_on_methods=["POST"])
            assert caught.value is failure
        else:
            response = await _send(client, request, retry_on_methods=["POST"])
            assert response.status_code == (200 if budget else failure[0])
        assert len(transport.requests) == budget + 1
        assert transport.sleeps == ([1.0] if budget and failure_kind == "retry-after" else [])


@pytest.mark.parametrize("owner", ["policies", "pipeline"])
@pytest.mark.parametrize("empty", [False, True])
async def test_caller_owned_pipeline_is_not_augmented(asynchronous, owner, empty):
    """Caller policy lists and pipelines keep their exact policies and retry behavior."""
    transport = (_AsyncTransport if asynchronous else _SyncTransport)([(503, {}), _SUCCESS])
    retry = (policies.AsyncRetryPolicy if asynchronous else policies.RetryPolicy)(retry_total=1)
    supplied = [] if empty else [retry]
    original = list(supplied)
    pipeline = (AsyncPipeline if asynchronous else Pipeline)(transport, supplied) if owner == "pipeline" else None
    options = {owner: pipeline if owner == "pipeline" else supplied}
    async with _client(asynchronous, transport=transport, **options) as (client, transport):
        response = await _send(client, HttpRequest("POST", _OPTIMIZER, json={}))
        actual = [getattr(runner, "_policy", runner) for runner in client._client._pipeline._impl_policies]
        assert supplied == original == actual
        if pipeline is not None:
            assert client._client._pipeline is pipeline
        assert len(transport.requests) == (1 if empty else 2)
        assert response.status_code == (503 if empty else 200)
        assert "api-key" not in transport.requests[0].headers


async def test_custom_auth_and_extension_policies_are_preserved(asynchronous):
    """Custom authentication and extension policies do not bypass the default POST guard."""
    authentication = policies.HeadersPolicy(headers={"X-Custom-Auth": "fixture"})
    per_call = [policies.HeadersPolicy(headers={"X-Per-Call": "present"})]
    per_retry = [policies.HeadersPolicy(headers={"X-Per-Retry": "present"})]
    original_call, original_retry = list(per_call), list(per_retry)
    async with _client(
        asynchronous,
        [(503, {}), _SUCCESS],
        authentication_policy=authentication,
        per_call_policies=per_call,
        per_retry_policies=per_retry,
    ) as (client, transport):
        response = await _send(client, HttpRequest("POST", _CREATE, json={}))
        assert response.status_code == 503
        assert len(transport.requests) == 1
        assert client._config.authentication_policy is authentication
        assert per_call == original_call
        assert per_retry == original_retry
        for name, value in {"X-Custom-Auth": "fixture", "X-Per-Call": "present", "X-Per-Retry": "present"}.items():
            assert transport.requests[0].headers[name] == value


@pytest.mark.parametrize("redirect_status", [307, 308])
@pytest.mark.parametrize("failure", [(503, {}), (429, {"Retry-After": "1"})])
async def test_redirected_post_reapplies_guard_without_disabling_redirects(asynchronous, redirect_status, failure):
    """Redirects remain compatible, but consuming retry_total cannot revive POST retries."""
    location = _OPTIMIZER + "?redirected=1"
    outcomes = [(redirect_status, {"Location": location}), failure, _SUCCESS]
    async with _client(asynchronous, outcomes, retry_total=4) as (client, transport):
        response = await _send(
            client, HttpRequest("POST", _OPTIMIZER, json={"seq_id": 7}), retry_total=4, retry_on_methods=["POST"]
        )
        assert len(transport.requests) == 2
        assert response.status_code == failure[0]
        assert [request.method for request in transport.requests] == ["POST", "POST"]
        assert [request.url for request in transport.requests] == [_OPTIMIZER, location]
        assert transport.requests[0].content == transport.requests[1].content
        assert transport.sleeps == []


async def test_303_redirected_get_keeps_retries(asynchronous):
    """A 303 changes POST to GET; that GET retains its normal retry budget."""
    outcomes = [(303, {"Location": _STATUS}), (503, {}), _SUCCESS]
    async with _client(asynchronous, outcomes) as (client, transport):
        response = await _send(client, HttpRequest("POST", _CREATE, json={}))
        assert response.status_code == 200
        assert [request.method for request in transport.requests] == ["POST", "GET", "GET"]
        assert [request.url for request in transport.requests] == [_CREATE, _STATUS, _STATUS]


async def test_default_retry_subclass_keeps_security_policy_order(asynchronous):
    """A RetryPolicy subclass remains between redirect and the existing security guards."""
    async with _client(asynchronous) as (client, _):
        actual = [getattr(runner, "_policy", runner) for runner in client._client._pipeline._impl_policies]
        retry = client._config.retry_policy
        redirect = client._config.redirect_policy
        names = [type(policy).__name__ for policy in actual]
        assert isinstance(retry, policies.AsyncRetryPolicy if asynchronous else policies.RetryPolicy)
        assert actual.index(redirect) < actual.index(retry) < names.index("_ApiKeyTransportPolicy")
        assert names.index("_ApiKeyTransportPolicy") < names.index("_DirectContextPolicy")
        assert names.index("_DirectContextPolicy") < names.index("_ScopedAzureKeyCredentialPolicy")
        assert names.index("_ScopedAzureKeyCredentialPolicy") < names.index("SensitiveHeaderCleanupPolicy")

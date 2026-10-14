# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Transport-boundary security regressions using real sync and async pipelines."""

from contextlib import asynccontextmanager
from copy import deepcopy
import inspect

import pytest
from azure.core.credentials import AccessToken, AzureKeyCredential
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import AsyncPipeline, Pipeline, policies
from azure.core.pipeline.transport import AsyncHttpResponse, AsyncHttpTransport, HttpResponse, HttpTransport
from azure.core.rest import HttpRequest
from azure.core.utils import case_insensitive_dict

from azure.ai.finetuningsessions import FineTuningSessionClient
from azure.ai.finetuningsessions import _patch
from azure.ai.finetuningsessions.aio import FineTuningSessionClient as AsyncClient

pytestmark = pytest.mark.asyncio

_ENDPOINT = "https://unit.invalid/api/projects/p"
_PATH = "/api/projects/p/fine_tuning/sessions/s/heartbeat"
_URL = "https://unit.invalid" + _PATH
_OTHER = "https://other.invalid" + _PATH
_KEY = "fixture-api-key"
_ENVIRONMENT = {
    "X_COGNITIVE_SUBSCRIPTION_ID": "environment-sub",
    "LOOM_AZURE_RESOURCE_ID": "environment-resource",
    "LOOM_AZURE_RESOURCE_TENANT_ID": "environment-tenant",
    "LOOM_AZURE_RESOURCE_LOCATION": "environment-location",
    "LOOM_WORKSPACE_RESOURCE_ID": "environment-workspace",
}


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def asynchronous(request):
    return request.param


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    for name in (*_ENVIRONMENT, "COGNITIVE_SUBSCRIPTION_ID", "AZURE_SUBSCRIPTION_ID"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def direct_headers(monkeypatch):
    for name, value in _ENVIRONMENT.items():
        monkeypatch.setenv(name, value)
    return {
        name.lower(): value
        for name, value in _patch._base_headers().items()
        if name.lower() not in {"accept", "foundry-features"}
    }


class _ResponseBody:
    def __init__(self, request, status, headers):
        super().__init__(request, None)
        self.status_code = status
        self.headers = case_insensitive_dict({"Content-Type": "application/json", **headers})
        self.content_type = "application/json"
        self.reason = "fixture"

    def body(self):
        return b"{}"

    def json(self):
        return {}


class _SyncResponse(_ResponseBody, HttpResponse):
    pass


class _AsyncResponse(_ResponseBody, AsyncHttpResponse):
    pass


class _RecordingTransport:
    def __init__(self, responses=None):
        self.responses = list(responses or [(200, {})])
        self.requests = []
        self.sleeps = []
        self.on_send = None

    def respond(self, request, response_type):
        # Redirects mutate the request in place; assertions must inspect the
        # exact headers/URL at EACH transport send, not just the final request.
        self.requests.append(deepcopy(request))
        assert len(self.requests) <= len(self.responses), "Unexpected transport send"
        if self.on_send:
            self.on_send(request)
        status, headers = self.responses[len(self.requests) - 1]
        return response_type(request, status, headers)


class _SyncTransport(_RecordingTransport, HttpTransport):
    def send(self, request, **kwargs):
        return self.respond(request, _SyncResponse)

    def open(self):
        pass

    def close(self):
        pass

    def __exit__(self, *args):
        self.close()

    def sleep(self, duration):
        self.sleeps.append(duration)


class _AsyncTransport(_RecordingTransport, AsyncHttpTransport):
    async def send(self, request, **kwargs):
        return self.respond(request, _AsyncResponse)

    async def open(self):
        pass

    async def close(self):
        pass

    async def __aexit__(self, *args):
        await self.close()

    async def sleep(self, duration):
        self.sleeps.append(duration)


@asynccontextmanager
async def _client(asynchronous, *, endpoint=_ENDPOINT, credential=None, responses=None, **options):
    transport = options.pop("transport", None)
    if transport is None:
        transport = (_AsyncTransport if asynchronous else _SyncTransport)(responses)
    options.setdefault("retry_total", 0)
    client = (AsyncClient if asynchronous else FineTuningSessionClient)(
        endpoint, credential or AzureKeyCredential(_KEY), transport=transport, **options
    )
    try:
        yield client, transport
    finally:
        result = client.close()
        if inspect.isawaitable(result):
            await result


async def _send(client, request, **kwargs):
    result = client.send_request(request, **kwargs)
    return await result if inspect.isawaitable(result) else result


def _redirect(location, status=307):
    return [(status, {"Location": location}), (200, {})]


@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
@pytest.mark.parametrize("location", [_OTHER, "https://unit.invalid:444" + _PATH])
async def test_redirect_does_not_forward_sdk_api_key(asynchronous, status, location):
    async with _client(asynchronous, responses=_redirect(location, status)) as (client, transport):
        assert (await _send(client, HttpRequest("GET", _URL))).status_code == 200
        assert len(transport.requests) == 2
        assert transport.requests[0].headers["api-key"] == _KEY
        assert transport.requests[1].url == location
        assert "api-key" not in transport.requests[1].headers


@pytest.mark.parametrize(
    "location",
    [
        _PATH + "?redirected=1",
        _URL + "?redirected=1",
        "https://UNIT.INVALID" + _PATH,
        "https://unit.invalid:443" + _PATH,
    ],
)
@pytest.mark.parametrize("prepopulated", [False, True])
async def test_same_origin_redirect_keeps_authentication(asynchronous, direct_headers, location, prepopulated):
    headers = _patch._base_headers() if prepopulated else {}
    async with _client(asynchronous, responses=_redirect(location)) as (client, transport):
        await _send(client, HttpRequest("POST", _URL, headers=headers, json={"sequence_id": 1}))
        assert len(transport.requests) == 2
        for sent in transport.requests:
            assert sent.method == "POST"
            assert sent.headers["api-key"] == _KEY
            for name, value in direct_headers.items():
                assert sent.headers[name] == value


@pytest.mark.parametrize("header_mode", ["raw", "base", "mixed-case-base"])
@pytest.mark.parametrize(
    "location",
    [_OTHER, "https://unit.invalid:444" + _PATH, _ENDPOINT + "/other", _ENDPOINT + "/fine_tuning/sessions-other"],
)
async def test_redirect_removes_only_sdk_direct_context(asynchronous, direct_headers, header_mode, location):
    headers = {} if header_mode == "raw" else _patch._base_headers()
    if header_mode == "mixed-case-base":
        headers = {name.swapcase(): value for name, value in headers.items()}
    async with _client(asynchronous, responses=_redirect(location)) as (client, transport):
        await _send(client, HttpRequest("GET", _URL, headers=headers))
        assert len(transport.requests) == 2
        for name, value in direct_headers.items():
            assert transport.requests[0].headers[name] == value
            assert name not in transport.requests[1].headers


@pytest.mark.parametrize("location", [_OTHER, _ENDPOINT + "/other"])
async def test_prepopulated_context_is_removed_from_initial_out_of_scope_request(
    asynchronous, direct_headers, location
):
    async with _client(asynchronous) as (client, transport):
        await _send(client, HttpRequest("GET", location, headers=_patch._base_headers()))
        assert len(transport.requests) == 1
        assert not (set(direct_headers) & {name.lower() for name in transport.requests[0].headers})


@pytest.mark.parametrize("prepopulated", [False, True])
async def test_caller_overrides_survive_redirect_case_insensitively(asynchronous, direct_headers, prepopulated):
    overrides = {
        "APIM-SUBSCRIPTION-ID": "caller-sub",
        "x-workSPACE-resource-ID": "caller-workspace",
        "X-Caller": "caller",
    }
    # _base_headers returns a plain dict; HttpRequest normalizes duplicates of
    # different case, so a caller override must win before ownership is tested.
    headers = _patch._base_headers(overrides) if prepopulated else overrides
    async with _client(asynchronous, responses=_redirect(_OTHER)) as (client, transport):
        await _send(client, HttpRequest("GET", _URL, headers=headers))
        assert len(transport.requests) == 2
        for sent in transport.requests:
            for name, value in overrides.items():
                assert sent.headers[name] == value
        for name in set(direct_headers) - {"apim-subscription-id", "x-workspace-resource-id"}:
            assert name not in transport.requests[1].headers


@pytest.mark.parametrize("prepopulated", [False, True])
async def test_cleanup_retains_snapshot_but_preserves_later_caller_override(
    asynchronous, direct_headers, monkeypatch, prepopulated
):
    class CallerPolicy(policies.SansIOHTTPPolicy):
        def on_request(self, request):
            if request.http_request.url == _OTHER:
                request.http_request.headers["AZURE-RESOURCE-ID"] = "caller-resource"

    caller_policy = CallerPolicy()
    caller_policies = [caller_policy]
    headers = _patch._base_headers() if prepopulated else {}

    def clear_environment(_):
        for name in _ENVIRONMENT:
            monkeypatch.delenv(name, raising=False)

    async with _client(asynchronous, responses=_redirect(_OTHER), per_retry_policies=caller_policies) as (
        client,
        transport,
    ):
        transport.on_send = clear_environment
        await _send(client, HttpRequest("GET", _URL, headers=headers))
        assert caller_policies == [caller_policy]
        assert len(transport.requests) == 2
        assert transport.requests[0].headers["azure-resource-id"] == "environment-resource"
        assert transport.requests[1].headers["azure-resource-id"] == "caller-resource"
        for name in set(direct_headers) - {"azure-resource-id"}:
            assert name not in transport.requests[1].headers


@pytest.mark.parametrize("blocked", [None, [], ["X-Caller-Secret", "API-KEY"]])
async def test_cleanup_runs_after_explicit_auth_reinjection(asynchronous, blocked):
    credential = AzureKeyCredential(_KEY)
    authentication = policies.AzureKeyCredentialPolicy(credential, "API-KEY")
    before_cleanup = []

    class ObserveAuthentication(policies.SansIOHTTPPolicy):
        def on_request(self, request):
            before_cleanup.append(request.http_request.headers.get("api-key"))

    original_blocked = deepcopy(blocked)
    async with _client(
        asynchronous,
        credential=credential,
        responses=_redirect(_OTHER),
        authentication_policy=authentication,
        custom_hook_policy=ObserveAuthentication(),
        blocked_redirect_headers=blocked,
    ) as (client, transport):
        request = HttpRequest(
            "GET",
            _URL,
            headers={"X-MS-Authorization-Auxiliary": "auxiliary", "X-Caller-Secret": "private", "X-Caller": "keep"},
        )
        await _send(client, request)
        assert client._config.authentication_policy is authentication
        assert blocked == original_blocked
        assert before_cleanup == [_KEY, _KEY], "The actual auth policy must run again on the redirected request"
        assert len(transport.requests) == 2
        assert "api-key" not in transport.requests[1].headers
        assert "x-ms-authorization-auxiliary" not in transport.requests[1].headers
        assert transport.requests[1].headers["x-caller"] == "keep"
        if blocked:
            assert "x-caller-secret" not in transport.requests[1].headers


async def test_explicit_core_cleanup_opt_out_does_not_unbind_sdk_credential(asynchronous, direct_headers):
    async with _client(
        asynchronous, responses=_redirect(_OTHER), disable_redirect_cleanup=True, blocked_redirect_headers=[]
    ) as (client, transport):
        await _send(client, HttpRequest("GET", _URL, headers=_patch._base_headers()))
        assert len(transport.requests) == 2
        assert transport.requests[0].headers["api-key"] == _KEY
        assert "api-key" not in transport.requests[1].headers
        assert not (set(direct_headers) & {name.lower() for name in transport.requests[1].headers})


@pytest.mark.parametrize("allow_insecure_http", [False, True])
@pytest.mark.parametrize(
    "endpoint",
    [
        "http://remote.invalid",
        "http://localhost.evil.invalid",
        "http://localhost@remote.invalid",
        "http://169.254.169.254",
    ],
)
async def test_remote_plaintext_key_rejected_before_transport(asynchronous, endpoint, allow_insecure_http):
    async with _client(asynchronous, endpoint=endpoint, allow_insecure_http=allow_insecure_http) as (client, transport):
        with pytest.raises(ValueError, match="HTTPS"):
            await _send(client, HttpRequest("POST", endpoint + "/fine_tuning/sessions", json={}), enforce_https=False)
        assert transport.requests == []


@pytest.mark.parametrize("allow_insecure_http", [False, True])
@pytest.mark.parametrize(
    "location", ["http://unit.invalid" + _PATH, "http://unit.invalid:443" + _PATH, "http://localhost:8080/"]
)
async def test_http_downgrade_rejected_before_redirected_transport(asynchronous, location, allow_insecure_http):
    async with _client(asynchronous, responses=_redirect(location), allow_insecure_http=allow_insecure_http) as (
        client,
        transport,
    ):
        with pytest.raises(ValueError, match="HTTPS"):
            await _send(client, HttpRequest("GET", _URL))
        assert len(transport.requests) == 1
        assert transport.requests[0].url == _URL
        assert transport.requests[0].headers["api-key"] == _KEY


@pytest.mark.parametrize("allow_insecure_http", [False, True])
@pytest.mark.parametrize(
    "endpoint", ["http://localhost:8080", "http://127.0.0.1:8080/api", "http://[::1]:8080", "http://LOCALHOST:9000"]
)
async def test_loopback_key_requires_explicit_opt_in(asynchronous, endpoint, allow_insecure_http):
    async with _client(asynchronous, endpoint=endpoint, allow_insecure_http=allow_insecure_http) as (client, transport):
        request = HttpRequest("GET", endpoint + "/fine_tuning/sessions/s")
        if allow_insecure_http:
            assert (await _send(client, request)).status_code == 200
            assert transport.requests[0].headers["api-key"] == _KEY
        else:
            with pytest.raises(ValueError, match="HTTPS"):
                await _send(client, request, enforce_https=False)
            assert transport.requests == []


@pytest.mark.parametrize(
    "location",
    ["http://remote.invalid/", "http://localhost.evil.invalid/", "http://localhost:8081/", "http://127.0.0.1:8080/"],
)
async def test_loopback_exception_cannot_follow_plaintext_redirect_off_origin(asynchronous, location):
    endpoint = "http://localhost:8080"
    async with _client(asynchronous, endpoint=endpoint, responses=_redirect(location), allow_insecure_http=True) as (
        client,
        transport,
    ):
        with pytest.raises(ValueError, match="HTTPS"):
            await _send(client, HttpRequest("GET", endpoint + "/fine_tuning/sessions/s"))
        assert len(transport.requests) == 1


async def test_scheme_change_without_authority_change_does_not_forward_key(asynchronous, direct_headers):
    endpoint = "http://localhost:8080"
    location = "https://localhost:8080/fine_tuning/sessions/s"
    async with _client(asynchronous, endpoint=endpoint, responses=_redirect(location), allow_insecure_http=True) as (
        client,
        transport,
    ):
        await _send(client, HttpRequest("GET", endpoint + "/fine_tuning/sessions/s", headers=_patch._base_headers()))
        assert len(transport.requests) == 2
        assert transport.requests[0].headers["api-key"] == _KEY
        assert "api-key" not in transport.requests[1].headers
        assert not (set(direct_headers) & {name.lower() for name in transport.requests[1].headers})


@pytest.mark.parametrize("allow_insecure_http", [False, True])
async def test_loopback_bearer_still_requires_opt_in(asynchronous, allow_insecure_http):
    class Credential:
        def get_token(self, *scopes, **kwargs):
            return AccessToken("fixture-token", 2**31)

    class AsyncCredential:
        async def get_token(self, *scopes, **kwargs):
            return AccessToken("fixture-token", 2**31)

    endpoint = "http://localhost:8080"
    credential = AsyncCredential() if asynchronous else Credential()
    async with _client(
        asynchronous, endpoint=endpoint, credential=credential, allow_insecure_http=allow_insecure_http
    ) as (client, transport):
        request = HttpRequest("GET", endpoint + "/fine_tuning/sessions/s")
        if allow_insecure_http:
            await _send(client, request)
            assert transport.requests[0].headers["Authorization"] == "Bearer fixture-token"
        else:
            with pytest.raises(ServiceRequestError, match="non-TLS"):
                await _send(client, request)
            assert transport.requests == []


@pytest.mark.parametrize("caller_key", [None, "caller-owned-key"])
async def test_raw_off_origin_request_does_not_receive_sdk_key(asynchronous, caller_key):
    headers = {"API-KEY": caller_key} if caller_key else {}
    async with _client(asynchronous) as (client, transport):
        await _send(client, HttpRequest("GET", _OTHER, headers=headers))
        assert transport.requests[0].headers.get("api-key") == caller_key


async def test_same_origin_key_rotation_is_preserved(asynchronous):
    credential = AzureKeyCredential(_KEY)
    async with _client(asynchronous, credential=credential, responses=_redirect(_URL + "?next=1")) as (
        client,
        transport,
    ):
        transport.on_send = lambda _: credential.update("rotated-fixture-key")
        await _send(client, HttpRequest("GET", _URL))
        assert [request.headers["api-key"] for request in transport.requests] == [_KEY, "rotated-fixture-key"]


@pytest.mark.parametrize("empty", [False, True])
async def test_explicit_policy_list_is_not_replaced_or_augmented(asynchronous, direct_headers, empty):
    caller_policy = policies.HeadersPolicy(headers={"X-Caller-Policy": "present"})
    supplied = [] if empty else [caller_policy]
    async with _client(asynchronous, policies=supplied) as (client, transport):
        await _send(client, HttpRequest("GET", _URL, headers={"AZURE-RESOURCE-ID": "caller-resource"}))
        actual = [getattr(runner, "_policy", runner) for runner in client._client._pipeline._impl_policies]
        assert actual == supplied == ([] if empty else [caller_policy])
        sent = transport.requests[0].headers
        assert "api-key" not in sent
        assert sent["azure-resource-id"] == "caller-resource"
        assert all(name not in sent for name in set(direct_headers) - {"azure-resource-id"})
        assert sent.get("x-caller-policy") == (None if empty else "present")


async def test_explicit_pipeline_identity_and_headers_are_preserved(asynchronous, direct_headers):
    transport = (_AsyncTransport if asynchronous else _SyncTransport)()
    pipeline = (AsyncPipeline if asynchronous else Pipeline)(
        transport, [policies.HeadersPolicy(headers={"X-Caller": "yes"})]
    )
    async with _client(asynchronous, pipeline=pipeline, transport=transport) as (client, transport):
        await _send(client, HttpRequest("GET", _URL, headers={"API-KEY": "caller-owned-key"}))
        assert client._client._pipeline is pipeline
        assert transport.requests[0].headers["api-key"] == "caller-owned-key"
        assert transport.requests[0].headers["x-caller"] == "yes"
        assert not (set(direct_headers) & {name.lower() for name in transport.requests[0].headers})


async def test_explicit_redirect_policy_is_preserved(asynchronous):
    redirect = (policies.AsyncRedirectPolicy if asynchronous else policies.RedirectPolicy)(permit_redirects=False)
    async with _client(asynchronous, responses=_redirect(_OTHER), redirect_policy=redirect) as (client, transport):
        response = await _send(client, HttpRequest("GET", _URL))
        assert client._config.redirect_policy is redirect
        assert response.status_code == 307
        assert len(transport.requests) == 1


@pytest.mark.parametrize("prepopulated", [False, True])
async def test_operation_group_uses_the_protected_pipeline(asynchronous, direct_headers, prepopulated):
    async with _client(asynchronous, responses=_redirect(_OTHER)) as (client, transport):
        result = client.sessions.heartbeat(
            "s",
            foundry_features=_patch._PREVIEW,
            api_version="v1",
            headers=_patch._base_headers() if prepopulated else {},
        )
        if inspect.isawaitable(result):
            await result
        assert len(transport.requests) == 2
        assert transport.requests[0].headers["api-key"] == _KEY
        assert "api-key" not in transport.requests[1].headers
        for name, value in direct_headers.items():
            assert transport.requests[0].headers[name] == value
            assert name not in transport.requests[1].headers


@pytest.mark.parametrize("location", ["http://remote.invalid/fine_tuning/sessions", "http://unit.invalid" + _PATH])
async def test_custom_auth_policy_cannot_bypass_default_pipeline_tls_guard(asynchronous, location):
    credential = AzureKeyCredential(_KEY)
    authentication = policies.AzureKeyCredentialPolicy(credential, "API-KEY")
    async with _client(
        asynchronous,
        credential=credential,
        responses=_redirect(location),
        authentication_policy=authentication,
        allow_insecure_http=True,
    ) as (client, transport):
        assert client._config.authentication_policy is authentication
        with pytest.raises(ValueError, match="HTTPS"):
            await _send(client, HttpRequest("GET", _URL), enforce_https=False)
        assert len(transport.requests) == 1


@pytest.mark.parametrize("endpoint", ["http://localhost:8080", "http://remote.invalid"])
async def test_custom_auth_policy_is_preserved_but_cannot_send_plaintext(asynchronous, endpoint):
    credential = AzureKeyCredential(_KEY)
    authentication = policies.AzureKeyCredentialPolicy(credential, "API-KEY")
    async with _client(
        asynchronous, endpoint=endpoint, credential=credential, authentication_policy=authentication
    ) as (
        client,
        transport,
    ):
        assert client._config.authentication_policy is authentication
        with pytest.raises(ValueError, match="HTTPS"):
            await _send(client, HttpRequest("GET", endpoint + "/fine_tuning/sessions/s"))
        assert transport.requests == []


async def test_same_authority_scheme_change_cleans_reinjected_custom_auth(asynchronous):
    endpoint = "http://localhost:8080"
    credential = AzureKeyCredential(_KEY)
    authentication = policies.AzureKeyCredentialPolicy(credential, "API-KEY")
    async with _client(
        asynchronous,
        endpoint=endpoint,
        credential=credential,
        responses=_redirect("https://localhost:8080/fine_tuning/sessions/s"),
        authentication_policy=authentication,
        allow_insecure_http=True,
    ) as (client, transport):
        await _send(client, HttpRequest("GET", endpoint + "/fine_tuning/sessions/s"))
        assert len(transport.requests) == 2
        assert transport.requests[0].headers["api-key"] == _KEY
        assert "api-key" not in transport.requests[1].headers


async def test_explicit_loopback_opt_in_allows_only_same_origin_redirects(asynchronous, direct_headers):
    endpoint = "http://localhost:8080"
    location = endpoint + "/fine_tuning/sessions/s?redirected=1"
    async with _client(asynchronous, endpoint=endpoint, responses=_redirect(location), allow_insecure_http=True) as (
        client,
        transport,
    ):
        await _send(client, HttpRequest("GET", endpoint + "/fine_tuning/sessions/s"))
        assert len(transport.requests) == 2
        for sent in transport.requests:
            assert sent.headers["api-key"] == _KEY
            for name, value in direct_headers.items():
                assert sent.headers[name] == value


@pytest.mark.parametrize("disable_redirect_cleanup", [False, True])
async def test_rotated_key_and_context_do_not_reappear_across_multiple_foreign_redirects(
    asynchronous, direct_headers, disable_redirect_cleanup
):
    credential = AzureKeyCredential(_KEY)
    responses = [(307, {"Location": _OTHER}), (308, {"Location": "https://third.invalid/"}), (200, {})]
    async with _client(
        asynchronous,
        credential=credential,
        responses=responses,
        disable_redirect_cleanup=disable_redirect_cleanup,
    ) as (client, transport):
        transport.on_send = lambda _: credential.update("rotated-fixture-key")
        await _send(client, HttpRequest("POST", _URL, headers=_patch._base_headers(), json={"sequence_id": 1}))
        assert len(transport.requests) == 3
        assert transport.requests[0].headers["api-key"] == _KEY
        for sent in transport.requests[1:]:
            assert "api-key" not in sent.headers
            assert not (set(direct_headers) & {name.lower() for name in sent.headers})


async def test_default_pipeline_guards_are_inside_redirect_and_retry_but_cleanup_is_after_auth(asynchronous):
    async with _client(asynchronous) as (client, _):
        pipeline = [getattr(runner, "_policy", runner) for runner in client._client._pipeline._impl_policies]
        actual = [type(policy).__name__ for policy in pipeline]
        redirect = "AsyncRedirectPolicy" if asynchronous else "RedirectPolicy"
        retry_type = policies.AsyncRetryPolicy if asynchronous else policies.RetryPolicy
        retry = next(index for index, policy in enumerate(pipeline) if isinstance(policy, retry_type))
        assert actual.index(redirect) < retry < actual.index("_ApiKeyTransportPolicy")
        assert actual.index("_ApiKeyTransportPolicy") < actual.index("_DirectContextPolicy")
        assert actual.index("_DirectContextPolicy") < actual.index("_ScopedAzureKeyCredentialPolicy")
        assert actual.index("_ScopedAzureKeyCredentialPolicy") < actual.index("SensitiveHeaderCleanupPolicy")


@pytest.mark.parametrize("scheme", ["http", "https"])
async def test_ambiguous_authority_is_rejected_before_transport(asynchronous, scheme):
    endpoint = scheme + "://localhost:8080"
    ambiguous = scheme + "://remote.invalid\\@localhost:8080/fine_tuning/sessions/s"
    async with _client(asynchronous, endpoint=endpoint, allow_insecure_http=True) as (client, transport):
        with pytest.raises(ValueError, match="backslashes"):
            await _send(client, HttpRequest("GET", ambiguous))
        assert transport.requests == []
    async with _client(asynchronous, endpoint=endpoint, responses=_redirect(ambiguous), allow_insecure_http=True) as (
        client,
        transport,
    ):
        with pytest.raises(ValueError, match="backslashes"):
            await _send(client, HttpRequest("GET", endpoint + "/fine_tuning/sessions/s"))
        assert len(transport.requests) == 1
        assert transport.requests[0].headers["api-key"] == _KEY


@pytest.mark.parametrize("endpoint", ["http://remote.invalid\\@localhost:8080", "http://user@localhost:8080"])
async def test_loopback_exception_rejects_ambiguous_or_userinfo_endpoints(asynchronous, endpoint):
    from azure.ai.finetuningsessions._client_options import _is_local_endpoint

    assert not _is_local_endpoint(endpoint)
    transport = (_AsyncTransport if asynchronous else _SyncTransport)()
    with pytest.raises(ValueError, match="backslashes|HTTPS"):
        async with _client(asynchronous, endpoint=endpoint, transport=transport, allow_insecure_http=True) as (
            client,
            _,
        ):
            await _send(client, HttpRequest("GET", endpoint + "/fine_tuning/sessions/s"))
    assert transport.requests == []

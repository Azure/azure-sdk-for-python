# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
import copy
import io
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
import requests

from azure.core.credentials import AccessToken, TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.core.pipeline import AsyncPipeline, Pipeline
from azure.core.pipeline.policies import (
    AsyncRetryPolicy,
    HttpLoggingPolicy,
    NetworkTraceLoggingPolicy,
    RedirectPolicy,
    RetryPolicy,
    SansIOHTTPPolicy,
)
from azure.core.pipeline.policies import AsyncRedirectPolicy
from azure.core.pipeline.transport import (
    AsyncHttpResponse,
    AsyncHttpTransport,
    HttpRequest as LegacyHttpRequest,
    HttpResponse,
    HttpTransport,
    RequestsTransport,
)
from azure.core.rest import HttpRequest
from azure.core.rest import AsyncHttpResponse as RestAsyncHttpResponse
from azure.core.utils import case_insensitive_dict
from azure.mgmt.core.policies import (
    AsyncExternalEvaluationPolicy,
    ExternalEvaluationPolicy,
    PolicyTokenRequestContext,
)


SUBSCRIPTION = "00000000-0000-0000-0000-000000000000"
URI = "https://management.azure.com/subscriptions/" + SUBSCRIPTION + "/resourceGroups/probe?api-version=2025-04-01"
HEADER = "x-ms-policy-external-evaluations"
TOKEN = "PoP offline-test-token"
DENIAL = {
    "error": {
        "code": "RequestDisallowedByPolicy",
        "message": "External evaluation required.",
        "additionalInfo": [
            {
                "type": "PolicyViolation",
                "info": {"evaluationDetails": {"missingPolicyTokenDetails": {"isChangeReferenceRequired": False}}},
            }
        ],
    }
}


def acquisition_result(**overrides):
    return {
        "result": "Succeeded",
        "token": TOKEN,
        "results": [{"policyAction": "Allow"}],
        **overrides,
    }


class MemoryResponse(HttpResponse):
    def __init__(self, request, status, payload, headers=None):
        super().__init__(request, None)
        self.status_code = status
        self.headers = case_insensitive_dict({"Content-Type": "application/json", **(headers or {})})
        self.content_type = "application/json"
        self.reason = "Test"
        self._content = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")

    def body(self):
        return self._content


class MemoryAsyncResponse(AsyncHttpResponse):
    def __init__(self, request, status, payload, headers=None):
        super().__init__(request, None)
        self.status_code = status
        self.headers = case_insensitive_dict({"Content-Type": "application/json", **(headers or {})})
        self.content_type = "application/json"
        self.reason = "Test"
        self._content = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
        self.closed = False
        self.loaded = False

    def body(self):
        return self._content

    async def load_body(self):
        self.loaded = True

    async def close(self):
        self.closed = True


class MemoryTransport(HttpTransport):
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def open(self):
        pass

    def close(self):
        pass

    def __exit__(self, *args):
        self.close()

    def send(self, request, **kwargs):
        body = request.content if isinstance(request, HttpRequest) else request.body
        self.calls.append((request.method, request.url, body, dict(request.headers), dict(kwargs)))
        status, payload, *headers = self.responses.pop(0)
        return MemoryResponse(request, status, payload, headers[0] if headers else None)


class MemoryAsyncTransport(AsyncHttpTransport):
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    async def open(self):
        pass

    async def close(self):
        pass

    async def __aexit__(self, *args):
        await self.close()

    async def send(self, request, **kwargs):
        body = request.content if isinstance(request, HttpRequest) else request.body
        self.calls.append((request.method, request.url, body, dict(request.headers), dict(kwargs)))
        status, payload, *headers = self.responses.pop(0)
        return MemoryAsyncResponse(request, status, payload, headers[0] if headers else None)


@pytest.fixture(params=["sync", "async"])
def run_flow(request):
    mode = request.param

    def run(
        http_request,
        responses=None,
        result=None,
        provider_error=None,
        extra_policies=None,
    ):
        contexts = []

        def provider(context):
            contexts.append(context)
            if provider_error is not None:
                raise provider_error
            return acquisition_result() if result is None else result

        responses = responses or [(403, DENIAL), (200, {})]
        if mode == "sync":
            transport = MemoryTransport(responses)
            policies = [
                ExternalEvaluationPolicy(provider),
                RedirectPolicy(),
                RetryPolicy(retry_backoff_factor=0),
            ]
            with Pipeline(transport, policies=policies + (extra_policies or [])) as pipeline:
                try:
                    response = pipeline.run(http_request)
                except HttpResponseError as error:
                    return transport.calls, contexts, error
            return transport.calls, contexts, response.http_response

        async def run_async():
            async def async_provider(context):
                await asyncio.sleep(0)
                return provider(context)

            transport = MemoryAsyncTransport(responses)
            policies = [
                AsyncExternalEvaluationPolicy(async_provider),
                AsyncRedirectPolicy(),
                AsyncRetryPolicy(retry_backoff_factor=0),
            ]
            async with AsyncPipeline(transport, policies=policies + (extra_policies or [])) as pipeline:
                try:
                    response = await pipeline.run(http_request)
                except HttpResponseError as error:
                    return transport.calls, contexts, error
            return transport.calls, contexts, response.http_response

        return asyncio.run(run_async())

    return run


@pytest.mark.parametrize("request_type", ["legacy", "rest"])
@pytest.mark.parametrize("method", ["PUT", "PATCH", "POST", "DELETE"])
@pytest.mark.parametrize(
    "body",
    [
        b'{\r\n  "value":1.00, "escaped":"\\u0061"\r\n}',
        '{"tags":{"unicode":"\u00e9"},"z":1,"a":2}'.encode("utf-8"),
    ],
)
def test_exact_bytes_and_headers(run_flow, request_type, method, body):
    headers = {"Content-Type": "application/json", "If-Match": '"etag"'}
    if request_type == "legacy":
        request = LegacyHttpRequest(method, URI, headers=headers, data=body)
    else:
        request = HttpRequest(method, URI, headers=headers, content=body)
    calls, contexts, response = run_flow(request)
    assert response.status_code == 200
    assert len(calls) == 2
    assert calls[0][:3] == calls[1][:3] == (method, URI, body)
    assert calls[1][3][HEADER] == TOKEN
    assert calls[1][3]["If-Match"] == '"etag"'
    assert calls[1][3]["Content-Length"] == str(len(body))
    assert contexts[0].subscription_id == SUBSCRIPTION
    assert b',"content":' + body in contexts[0].get_request_body()
    assert HEADER not in request.headers


@pytest.mark.parametrize("body", [None, b""])
def test_bodyless_delete(run_flow, body):
    calls, contexts, response = run_flow(HttpRequest("DELETE", URI, content=body))
    assert response.status_code == 200
    assert len(calls) == 2
    assert "content" not in json.loads(contexts[0].get_request_body())["operation"]
    assert not calls[1][2]


@pytest.mark.parametrize(
    "method,url,headers",
    [
        ("GET", URI, {}),
        ("HEAD", URI, {}),
        ("PUT", URI, {HEADER: "caller-token"}),
        (
            "PUT",
            "https://management.azure.com/providers/Microsoft.Management/managementGroups/example",
            {},
        ),
        (
            "PUT",
            "http://management.azure.com/subscriptions/" + SUBSCRIPTION + "/resourceGroups/example",
            {},
        ),
        (
            "POST",
            "https://management.azure.com/subscriptions/"
            + SUBSCRIPTION
            + "/providers/Microsoft.Authorization/acquirePolicyToken?api-version=2025-11-01",
            {},
        ),
    ],
)
def test_ineligible_requests_pass_through(run_flow, method, url, headers):
    calls, contexts, response = run_flow(HttpRequest(method, url, headers=headers), responses=[(403, DENIAL)])
    assert response.status_code == 403
    assert len(calls) == 1
    assert contexts == []


@pytest.mark.parametrize(
    "status,payload",
    [
        (200, {}),
        (403, {"error": {"code": "AuthorizationFailed"}}),
        (403, {"error": {"code": "RequestDisallowedByPolicy"}}),
        (403, b"not json"),
        (403, []),
        (
            403,
            {
                "error": {
                    "code": "RequestDisallowedByPolicy",
                    "additionalInfo": [None, {}],
                }
            },
        ),
    ],
)
def test_unrelated_responses_pass_through(run_flow, status, payload):
    calls, contexts, response = run_flow(HttpRequest("PUT", URI), responses=[(status, payload)])
    assert response.status_code == status
    assert len(calls) == 1
    assert contexts == []


def test_nested_hint(run_flow):
    denial = {"error": {"code": "RequestDisallowedByPolicy", "details": [DENIAL["error"]]}}
    calls, contexts, response = run_flow(HttpRequest("PUT", URI), responses=[(403, denial), (200, {})])
    assert response.status_code == 200
    assert len(contexts) == 1
    assert len(calls) == 2


def test_change_reference_required(run_flow):
    denial = copy.deepcopy(DENIAL)
    denial["error"]["additionalInfo"][0]["info"]["evaluationDetails"]["missingPolicyTokenDetails"][
        "isChangeReferenceRequired"
    ] = True
    calls, contexts, error = run_flow(HttpRequest("PUT", URI), responses=[(403, denial)])
    assert isinstance(error, HttpResponseError)
    assert error.status_code == 403
    assert "change reference" in str(error)
    assert len(calls) == 1
    assert contexts == []


@pytest.mark.parametrize(
    "body,content_type",
    [
        (io.BytesIO(b"{}"), "application/json"),
        (iter([b"{}"]), "application/json"),
        (b"not-json", "application/json"),
        (b"{}", "text/plain"),
        (b'"\xff"', "application/json"),
    ],
)
def test_unsupported_bodies_fail_explicitly(run_flow, body, content_type):
    calls, contexts, error = run_flow(HttpRequest("PUT", URI, content=body, headers={"Content-Type": content_type}))
    assert isinstance(error, HttpResponseError)
    assert error.status_code == 403
    assert len(calls) == 1
    assert contexts == []


@pytest.mark.parametrize(
    "result",
    [
        acquisition_result(result="Failed"),
        acquisition_result(results=[{"policyAction": "Deny"}]),
        acquisition_result(results=[{"policyAction": "Error"}]),
        acquisition_result(results=[{"policyAction": "Unknown"}]),
        acquisition_result(results=[{"policyAction": "Allow", "result": "Failed"}]),
        acquisition_result(results=[]),
        acquisition_result(results="invalid"),
        acquisition_result(results=[{"policyAction": "Allow"}, {"policyAction": "Deny"}]),
        acquisition_result(token=""),
        acquisition_result(token=None),
        acquisition_result(token="PoP bad\r\nheader"),
    ],
)
def test_failed_evaluation_does_not_replay(run_flow, result):
    calls, contexts, error = run_flow(HttpRequest("PUT", URI), result=result)
    assert isinstance(error, HttpResponseError)
    assert error.status_code == 403
    assert error.error.code == "RequestDisallowedByPolicy"
    assert len(calls) == len(contexts) == 1
    assert TOKEN not in str(error)


def test_provider_error_preserves_original_denial(run_flow):
    failure = ServiceRequestError("offline provider failed")
    calls, contexts, error = run_flow(HttpRequest("PUT", URI), provider_error=failure)
    assert isinstance(error, HttpResponseError)
    assert error.status_code == 403
    assert error.__cause__ is failure
    assert len(calls) == len(contexts) == 1


def test_second_denial_does_not_loop(run_flow):
    calls, contexts, response = run_flow(HttpRequest("POST", URI), responses=[(403, DENIAL), (403, DENIAL)])
    assert response.status_code == 403
    assert len(calls) == 2
    assert len(contexts) == 1


def test_replay_reuses_standard_retry(run_flow):
    calls, contexts, response = run_flow(HttpRequest("PUT", URI), responses=[(403, DENIAL), (503, {}), (200, {})])
    assert response.status_code == 200
    assert len(calls) == 3
    assert len(contexts) == 1
    assert all(call[3][HEADER] == TOKEN for call in calls[1:])


def test_token_replay_does_not_follow_redirect(run_flow):
    calls, contexts, response = run_flow(
        HttpRequest("PUT", URI),
        responses=[
            (403, DENIAL),
            (307, {}, {"Location": "https://untrusted.example/target"}),
        ],
    )
    assert response.status_code == 307
    assert len(calls) == 2
    assert len(contexts) == 1


def test_cross_origin_challenge_does_not_acquire(run_flow):
    target = "https://untrusted.example/subscriptions/" + SUBSCRIPTION + "/resourceGroups/probe"
    calls, contexts, response = run_flow(
        HttpRequest("PUT", URI), responses=[(307, {}, {"Location": target}), (403, DENIAL)]
    )
    assert response.status_code == 403
    assert len(calls) == 2
    assert contexts == []


def test_token_is_not_debug_logged(run_flow, caplog):
    caplog.set_level("DEBUG")
    _, _, response = run_flow(
        HttpRequest("PUT", URI),
        extra_policies=[
            NetworkTraceLoggingPolicy(logging_enable=True),
            HttpLoggingPolicy(),
        ],
    )
    assert response.status_code == 200
    assert TOKEN not in caplog.text


def test_token_is_not_debug_logged_on_retry(run_flow, caplog):
    caplog.set_level("DEBUG")
    calls, contexts, response = run_flow(
        HttpRequest("PUT", URI),
        responses=[(403, DENIAL), (503, {}), (200, {})],
        extra_policies=[NetworkTraceLoggingPolicy(logging_enable=True), HttpLoggingPolicy()],
    )
    assert response.status_code == 200
    assert len(calls) == 3
    assert len(contexts) == 1
    assert TOKEN not in caplog.text


def test_authentication_policies_run_on_replay(run_flow):
    class AuthenticationProbe(SansIOHTTPPolicy):
        def __init__(self):
            self.count = 0

        def on_request(self, request):
            self.count += 1
            request.http_request.headers["Authorization"] = "test-auth"

    authentication = AuthenticationProbe()
    calls, _, response = run_flow(HttpRequest("PUT", URI), extra_policies=[authentication])
    assert response.status_code == 200
    assert authentication.count == 2
    assert all(call[3]["Authorization"] == "test-auth" for call in calls)


def test_context_is_immutable_and_envelope_escapes_uri():
    context = PolicyTokenRequestContext(URI + '&name="quoted"', "PUT", SUBSCRIPTION, b'{ "number":1.00 }')
    envelope = context.get_request_body()
    assert json.loads(envelope)["operation"]["uri"] == context.uri
    assert b'{ "number":1.00 }' in envelope
    with pytest.raises(AttributeError):
        context.content = b"{}"


@pytest.mark.parametrize("retry_acquisition", [False, True])
def test_generated_policy_client_provider_and_opt_in(retry_acquisition, caplog):
    # Exercise the README adapter when the adjacent policy package is available.
    policy_module = pytest.importorskip("azure.mgmt.resource.policy")
    resource_module = pytest.importorskip("azure.mgmt.resource.resources")
    caplog.set_level("DEBUG")
    session = Mock(spec=requests.Session)
    calls = []

    def wire_request(method, url, **kwargs):
        data = kwargs["data"]
        if hasattr(data, "read"):
            data = data.read()
        if isinstance(data, str):
            data = data.encode("utf-8")
        headers = dict(kwargs["headers"])
        calls.append((method, url, data, headers, kwargs))
        if "/acquirePolicyToken?" in url:
            assert kwargs["allow_redirects"] is False
            acquisition_count = sum("/acquirePolicyToken?" in call[1] for call in calls)
            status, payload = (503, {}) if retry_acquisition and acquisition_count == 1 else (200, acquisition_result())
        elif HEADER in headers:
            status, payload = 200, {"name": "probe", "location": "westus2"}
        else:
            status, payload = 403, DENIAL
        response = requests.Response()
        response.status_code = status
        response.headers["Content-Type"] = "application/json"
        response._content = json.dumps(payload).encode("utf-8")
        response._content_consumed = True
        response.raw = SimpleNamespace(enforce_content_length=False)
        response.reason = "Test"
        return response

    session.request.side_effect = wire_request
    credential = Mock(spec=TokenCredential)
    credential.get_token.return_value = AccessToken("offline-test", 4102444800)
    token_client = policy_module.PolicyClient(
        credential,
        SUBSCRIPTION,
        api_version="2025-11-01",
        transport=RequestsTransport(session=session, session_owner=False),
        logging_enable=True,
        retry_backoff_factor=0,
    )

    def provider(context):
        assert context.subscription_id == SUBSCRIPTION
        return token_client.policy_tokens.acquire(
            io.BytesIO(context.get_request_body()),
            logging_enable=False,
            permit_redirects=False,
        )

    guarded_client = resource_module.ResourceManagementClient(
        credential,
        SUBSCRIPTION,
        transport=RequestsTransport(session=session, session_owner=False),
        per_call_policies=[ExternalEvaluationPolicy(provider)],
        logging_enable=True,
    )
    try:
        group = guarded_client.resource_groups.create_or_update("probe", {"location": "westus2"})
        assert group.name == "probe"
        assert len(calls) == (4 if retry_acquisition else 3)
        body = calls[0][2]
        assert calls[-1][2] == body
        assert all(b',"content":' + body in call[2] for call in calls[1:-1])
        assert calls[-1][3][HEADER] == TOKEN
        assert TOKEN not in caplog.text
    finally:
        guarded_client.close()
        token_client.close()


def test_generated_async_user_example(caplog):
    policy_module = pytest.importorskip("azure.mgmt.resource.policy.aio")
    resource_module = pytest.importorskip("azure.mgmt.resource.resources.aio")
    caplog.set_level("DEBUG")
    calls = []

    class GeneratedAsyncTransport(MemoryAsyncTransport):
        async def send(self, request, **kwargs):
            body = request.content
            if hasattr(body, "read"):
                body = body.read()
            if isinstance(body, str):
                body = body.encode("utf-8")
            headers = dict(request.headers)
            calls.append((request.method, request.url, body, headers))
            if "/acquirePolicyToken?" in request.url:
                status, payload = 200, acquisition_result()
            elif HEADER in headers:
                status, payload = 200, {"name": "probe", "location": "westus2"}
            else:
                status, payload = 403, DENIAL
            response = AsyncMock(spec=RestAsyncHttpResponse)
            response.status_code = status
            response.request = request
            response.headers = {"Content-Type": "application/json"}
            response.reason = "Test"
            response.content_type = "application/json"
            response.content = json.dumps(payload).encode("utf-8")
            response.text.return_value = json.dumps(payload)
            response.json.return_value = payload
            response.read.return_value = response.content
            return response

    async def example():
        credential = AsyncMock(spec=AsyncTokenCredential)
        credential.get_token.return_value = AccessToken("offline-test", 4102444800)
        async with policy_module.PolicyClient(
            credential,
            SUBSCRIPTION,
            api_version="2025-11-01",
            transport=GeneratedAsyncTransport([]),
            logging_enable=True,
        ) as token_client:

            async def provider(context):
                return await token_client.policy_tokens.acquire(
                    io.BytesIO(context.get_request_body()), logging_enable=False, permit_redirects=False
                )

            async with resource_module.ResourceManagementClient(
                credential,
                SUBSCRIPTION,
                transport=GeneratedAsyncTransport([]),
                per_call_policies=[AsyncExternalEvaluationPolicy(provider)],
                logging_enable=True,
            ) as resource_client:
                group = await resource_client.resource_groups.create_or_update("probe", {"location": "westus2"})
                assert group.name == "probe"

    asyncio.run(example())
    assert len(calls) == 3
    assert calls[0][2] == calls[2][2]
    assert b',"content":' + calls[0][2] in calls[1][2]
    assert calls[2][3][HEADER] == TOKEN
    assert TOKEN not in caplog.text

# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline test plan for the narrow legacy begin_* adapters.

Both client variants exercise every alias against sequenced HTTP 200 envelopes.
No service, credential acquisition, wall-clock polling sleeps, or heartbeat is
needed. Installation is local to test subclasses: production operation hooks
and the regeneration verifier's handwritten manifest are integrated separately.
"""

import asyncio
import json
from contextlib import asynccontextmanager
from copy import deepcopy
from inspect import iscoroutinefunction
from threading import Event
from urllib.parse import parse_qs, quote, urlsplit

import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import DeserializationError, HttpResponseError, ServiceRequestError
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, LROPoller, NoPolling

from azure.ai.finetuningsessions import FineTuningSessionClient, aio, models
from azure.ai.finetuningsessions._exceptions import (
    BatchTooLargeError,
    NoCapacityError,
    OperationResultUnavailableError,
    RequestRetryableError,
    RequestValidationError,
    TrainingEngineError,
)
from azure.ai.finetuningsessions._legacy_polling import install_legacy_pollers
from conftest import FakeHttpResponse, FakeTransport
from test_generated_contract import _AsyncResponse, _AsyncTransport

_ENDPOINT = "https://fake/api/projects/project_test"
_PREVIEW = "FineTuningSessions=V1Preview"
_SESSION = "model_raw/session ?#%"
_REQUEST = "request/raw ?#%"
_ACCEPTED = {"request_id": _REQUEST, "session_id": _SESSION, "status": "pending"}
_PENDING = {"status": "pending"}
_COMPLETED = {"status": "completed", "result": {}}
_CREATE = {"type": "training", "base_model": "model_test", "lora_config": {"rank": 16}}
_FORWARD = {"forward_backward_input": {"data": [], "loss_fn": "cross_entropy"}}
_OPTIMIZER = {"adam_params": {"learning_rate": 0.001}}
_SAMPLE = {"prompt": {"chunks": [{"tokens": [1]}]}, "sampling_params": {"max_tokens": 2}, "num_samples": 1}

# Exact hook contract, duplicated here intentionally rather than depending on
# production hooks being installed before this separately owned module lands.
_MAPPINGS = {
    "sessions": {
        "begin_create": ("create", "create_session"),
        "begin_unload": ("unload", "unload_session"),
    },
    "training": {
        "begin_forward_backward": ("forward_backward", "forward_backward"),
        "begin_optim_step": ("optimizer_step", "optim_step"),
    },
    "checkpoints": {
        "begin_save": ("save", "save_checkpoint"),
        "begin_save_sampler_weights": ("save_sampler_weights", "save_sampler_weights"),
    },
    "sampling": {"begin_sample": ("sample", "sample")},
}
_CASES = [
    pytest.param("sessions", "begin_create", "session", _CREATE, {}, models.OperationResult, "", id="create"),
    pytest.param("sessions", "begin_unload", None, None, {}, models.OperationResult, "/complete", id="unload"),
    pytest.param(
        "training", "begin_forward_backward", "request", _FORWARD,
        {"metrics": {"total_loss:sum": 1.25}, "loss_fn_outputs": [{"logprobs": [None, -0.5]}]},
        models.ForwardBackwardOperationResult, "/forward_backward", id="forward-backward",
    ),
    pytest.param(
        "training", "begin_optim_step", "request", _OPTIMIZER,
        {"metrics": {"skyrl.ai/grad_norm": 0.75, "step_count": 3}},
        models.OptimStepOperationResult, "/optim_step", id="optim-step",
    ),
    pytest.param(
        "checkpoints", "begin_save", "checkpoint", {"path": "checkpoint_test"},
        {"path": "loom://weights/checkpoint_test", "extra": {"retained": True}},
        models.SaveCheckpointOperationResult, "/checkpoint", id="save",
    ),
    pytest.param(
        "checkpoints", "begin_save_sampler_weights", "checkpoint", {"path": "checkpoint_test"},
        {"type": "save_weights_for_sampler", "sampling_session_id": "sampler_raw"},
        models.SaveSamplerWeightsOperationResult, "/checkpoint_sample", id="save-sampler-weights",
    ),
    pytest.param(
        "sampling", "begin_sample", "sample", _SAMPLE,
        {"sequences": [{"tokens": [42], "text": "answer", "logprobs": [None]}]},
        models.SampleOperationResult, "/sample", id="sample",
    ),
]


class _Sequence:
    def __init__(self, *payloads):
        self._payloads = iter(payloads)
        self.requests, self.responses, self.options, self.sleeps = [], [], [], []

    def _response(self, request, kwargs, asynchronous=False):
        self.requests.append(request)
        self.options.append(dict(kwargs))
        try:
            item = next(self._payloads)
        except StopIteration:
            pytest.fail("Unexpected extra HTTP request (retry, resubmission, or guessed route)")
        if isinstance(item, Exception):
            raise item
        status, payload, headers = 200, item, {}
        if isinstance(item, tuple):
            status, payload, *extra = item
            headers = extra[0] if extra else {}
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        if asynchronous:
            response = _AsyncResponse(request, {})
            response._body = body
            response.status_code = status
        else:
            response = FakeHttpResponse(request, body, status)
        response.headers.update(headers)
        self.responses.append(response)
        return response


class _SequenceTransport(_Sequence, FakeTransport):
    def send(self, request, **kwargs):
        return self._response(request, kwargs)

    def sleep(self, duration):
        self.sleeps.append(duration)


class _AsyncSequenceTransport(_Sequence, _AsyncTransport):
    async def send(self, request, **kwargs):
        # Force real interleaving in the concurrent api_version isolation test.
        await asyncio.sleep(0)
        return self._response(request, kwargs, asynchronous=True)

    async def sleep(self, duration):
        self.sleeps.append(duration)


class _RoutingMarker(SansIOHTTPPolicy):
    """Demonstrate that poll GETs pass through the operation's own pipeline."""

    def on_request(self, request):
        request.http_request.headers["x-offline-routing-policy"] = "visited"


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def asynchronous(request):
    return request.param


@asynccontextmanager
async def _client(asynchronous, *payloads, **options):
    transport_type = _AsyncSequenceTransport if asynchronous else _SequenceTransport
    transport = options.pop("transport", None) or transport_type(*payloads)
    client_type = aio.FineTuningSessionClient if asynchronous else FineTuningSessionClient
    configuration = {"api_version": "configured-version", "polling_interval": 0, "retry_total": 0, **options}
    client = client_type(
        _ENDPOINT, AzureKeyCredential("offline-secret-not-a-token"), transport=transport, **configuration
    )
    for group_name, mapping in _MAPPINGS.items():
        group = getattr(client, group_name)
        operation_type = type(f"Legacy{type(group).__name__}", (type(group),), {})
        install_legacy_pollers(operation_type, mapping, asynchronous=asynchronous)
        setattr(client, group_name, operation_type(group._client, group._config, group._serialize, group._deserialize))
    try:
        yield client, transport
    finally:
        if asynchronous:
            await client.close()
        else:
            client.close()


async def _begin(method, asynchronous, *args, **kwargs):
    if asynchronous:
        return await method(*args, **kwargs)
    return method(*args, **kwargs)


async def _result(poller, asynchronous):
    if asynchronous:
        return await asyncio.wait_for(poller.result(), timeout=2)
    return poller.result(timeout=2)


def _assert_wire(transport, suffix, query, *, create=False, sample=False):
    post, *polls = transport.requests
    assert post.method == "POST" and len(polls) == 2
    assert post.url.split("?", 1)[0] == _ENDPOINT + "/fine_tuning_sessions" + (
        "" if create else f"/{quote(_SESSION, safe='')}{suffix}"
    )
    assert parse_qs(urlsplit(post.url).query) == {
        **query, **({"checkpoint_id": ["sampler_checkpoint"]} if sample else {})
    }
    for request in polls:
        assert request.method == "GET"
        assert request.url.split("?", 1)[0] == (
            f"{_ENDPOINT}/fine_tuning_sessions/{quote(_SESSION, safe='')}/request/{quote(_REQUEST, safe='')}"
        )
        assert parse_qs(urlsplit(request.url).query) == query
    for request in transport.requests:
        assert request.headers["Foundry-Features"] == _PREVIEW
        assert request.headers["Accept"] == "application/json"
        assert request.headers["api-key"] == "offline-secret-not-a-token"
        assert request.headers["x-offline-routing-policy"] == "visited"
        assert "/fine_tuning/sessions" not in request.url and "heartbeat" not in request.url
    forbidden = {"api_version", "body", "cls", "polling", "polling_interval", "continuation_token", "checkpoint_id"}
    assert all(not forbidden.intersection(options) for options in transport.options)
    for response in transport.responses:
        assert response.status_code == 200
        assert "operation-location" not in {name.lower() for name in response.headers}


@pytest.mark.asyncio
@pytest.mark.parametrize("argument_style", ["positional", "body", "generated"])
@pytest.mark.parametrize("group, old, body_name, body, payload, expected_type, suffix", _CASES)
async def test_all_aliases_submit_once_and_poll_the_real_protocol(
    asynchronous, argument_style, group, old, body_name, body, payload, expected_type, suffix
):
    completed = {"status": "completed", "result": deepcopy(payload)}
    observed = []
    async with _client(
        asynchronous, deepcopy(_ACCEPTED), _PENDING, completed, per_call_policies=[_RoutingMarker()]
    ) as (client, transport):
        operation = getattr(getattr(client, group), old)
        args, kwargs = [], {"raw_response_hook": observed.append, "polling_interval": 0}
        if old != "begin_create":
            if argument_style == "positional":
                args.append(_SESSION)
            else:
                kwargs["session_id"] = _SESSION
        if body_name:
            if argument_style == "positional":
                args.append(deepcopy(body))
            else:
                kwargs["body" if argument_style == "body" else body_name] = deepcopy(body)
        if old == "begin_sample":
            kwargs["checkpoint_id"] = "sampler_checkpoint"
        poller = await _begin(operation, asynchronous, *args, **kwargs)
        assert type(poller) is (AsyncLROPoller if asynchronous else LROPoller)
        result = await _result(poller, asynchronous)
        assert type(result) is expected_type
        assert result.operation_id == _REQUEST and result.status == "succeeded"
        assert result.type == _MAPPINGS[group][old][1]
        assert poller.status() == "completed" and poller.done()
        if old in ("begin_create", "begin_unload"):
            assert result["session_id"] == _SESSION  # No automatic model_/session_ rewriting.
        elif old == "begin_forward_backward":
            assert result.total_loss == 1.25 and result.loss_fn_outputs == payload["loss_fn_outputs"]
        elif old == "begin_optim_step":
            assert result.grad_norm == 0.75 and result.step_count == 3
        elif old in ("begin_save", "begin_save_sampler_weights"):
            assert result.checkpoint_id == "checkpoint_test"
            if old == "begin_save":
                assert result.path == payload["path"] and result["extra"] == payload["extra"]
            else:
                assert result.sampling_session_id == "sampler_raw"
        else:
            assert result.sequences[0].tokens == [42] and result.sequences[0].logprobs == [None]
        if body_name:
            assert json.loads(transport.requests[0].content) == body
        assert all(isinstance(response, PipelineResponse) for response in observed) and len(observed) == 3
        assert observed[0].http_response.json() == _ACCEPTED
        assert completed["result"] == payload  # No in-place normalization of wire data.
        _assert_wire(
            transport,
            suffix,
            {"api-version": ["configured-version"]},
            create=old == "begin_create",
            sample=old == "begin_sample",
        )
        assert not transport.sleeps


@pytest.mark.asyncio
@pytest.mark.parametrize("per_call_version", [None, "override-version"])
async def test_per_call_options_survive_polling_without_mutating_config(asynchronous, per_call_version):
    params = {"user-data": ["first value", "second/value"], "api-version": "must-not-win"}
    headers = {"x-user-header": "value", "Content-Type": "application/json"}
    original = deepcopy((params, headers))
    async with _client(
        asynchronous, {"request_id": _REQUEST}, _PENDING, _COMPLETED, _ACCEPTED,
        polling_interval=0.25, per_call_policies=[_RoutingMarker()],
    ) as (client, transport):
        kwargs = {"params": params, "headers": headers, "connection_timeout": 7, "read_timeout": 9}
        if per_call_version is not None:
            kwargs["api_version"] = per_call_version
            kwargs["polling_interval"] = 0.5
        poller = await _begin(client.training.begin_optim_step, asynchronous, _SESSION, body=_OPTIMIZER, **kwargs)
        result = await _result(poller, asynchronous)
        assert result.operation_id == _REQUEST
        assert client._config.api_version == "configured-version"
        assert client.training._config is client._config
        assert (params, headers) == original
        assert transport.sleeps == [0.5 if per_call_version else 0.25]
        query = {"api-version": [per_call_version or "configured-version"], "user-data": params["user-data"]}
        _assert_wire(transport, "/optim_step", query)
        assert all(request.headers["x-user-header"] == "value" for request in transport.requests)
        assert all("Content-Type" not in request.headers for request in transport.requests[1:])
        assert all(options["connection_timeout"] == 7 and options["read_timeout"] == 9 for options in transport.options)
        # A later generated operation still uses the shared configuration and
        # returns its raw handle, not a patched LRO result.
        raw_result = client.training.optimizer_step(_SESSION, _OPTIMIZER, foundry_features=_PREVIEW)
        if asynchronous:
            raw_result = await raw_result
        assert type(raw_result) is models.ActionOperation
        assert parse_qs(urlsplit(transport.requests[-1].url).query)["api-version"] == ["configured-version"]


@pytest.mark.asyncio
async def test_concurrent_async_calls_keep_their_own_api_version_snapshots():
    async with _client(True, _ACCEPTED, _ACCEPTED, _COMPLETED, _COMPLETED) as (client, transport):
        first, second = await asyncio.gather(
            client.training.begin_optim_step(_SESSION, _OPTIMIZER, api_version="first"),
            client.training.begin_optim_step(_SESSION, _OPTIMIZER, api_version="second"),
        )
        await asyncio.gather(first.result(), second.result())
        for method in ("POST", "GET"):
            assert sorted(
                parse_qs(urlsplit(request.url).query)["api-version"][0]
                for request in transport.requests if request.method == method
            ) == ["first", "second"]
        assert client._config.api_version == "configured-version"


@pytest.mark.asyncio
@pytest.mark.parametrize("polling", [False, True])
async def test_cls_gets_the_real_response_and_nopolling_keeps_the_handle(asynchronous, polling):
    calls = []
    sentinel = object()

    def transform(response, result, headers):
        calls.append((response, result, headers))
        return sentinel

    async with _client(asynchronous, _ACCEPTED, _COMPLETED) as (client, transport):
        poller = await _begin(
            client.sessions.begin_create, asynchronous, body=_CREATE, polling=polling, cls=transform
        )
        assert not calls  # cls is the poller's result callback, not the submission capture callback.
        assert await _result(poller, asynchronous) is sentinel
        response, result, headers = calls[0]
        assert isinstance(response, PipelineResponse) and response.http_response is transport.responses[-1]
        assert headers == {} and len(calls) == 1
        assert len(transport.requests) == (2 if polling else 1)
        if polling:
            assert type(result) is models.OperationResult and result.type == "create_session"
        else:
            assert isinstance(poller.polling_method(), AsyncNoPolling if asynchronous else NoPolling)
            assert type(result) is models.CreateSessionResponse and result.as_dict() == _ACCEPTED
        with pytest.raises(ValueError, match="do not support continuation tokens"):
            poller.continuation_token()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "operation, body_type",
    [("begin_save", models.SaveCheckpointRequest), ("begin_save_sampler_weights", models.SaveSamplerWeightsRequest)],
)
@pytest.mark.parametrize("server_id", [None, "server-wins"])
async def test_checkpoint_body_path_fallback_never_overwrites_server_value(asynchronous, operation, body_type, server_id):
    payload = {"path": "loom://weights/remote", "extra": {"future": [False, None, 0.5]}}
    if server_id is not None:
        payload["checkpoint_id"] = server_id
    async with _client(asynchronous, _ACCEPTED, {"status": "completed", "result": payload}) as (client, transport):
        poller = await _begin(
            getattr(client.checkpoints, operation), asynchronous, session_id=_SESSION, body=body_type(path="caller-path")
        )
        result = await _result(poller, asynchronous)
        assert result.checkpoint_id == (server_id or "caller-path")
        assert result["path"] == payload["path"] and result["extra"] == payload["extra"]
        assert [request.method for request in transport.requests] == ["POST", "GET"]


_FAILURES = [
    pytest.param({"error_code": "engine_oom"}, BatchTooLargeError, id="batch"),
    pytest.param({"error_code": "worker_crashed"}, TrainingEngineError, id="engine"),
    pytest.param({"error_code": "invalid_request"}, RequestValidationError, id="validation"),
    pytest.param({"error_code": "future_transient_code", "should_retry": True}, RequestRetryableError, id="retry-hint"),
    pytest.param(
        {"error_code": "operation_completed_result_unavailable", "should_retry": True},
        OperationResultUnavailableError, id="lost-result-no-resubmit",
    ),
    pytest.param({"error_code": "unknown"}, HttpResponseError, id="generic"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("details, expected_error", _FAILURES)
async def test_failed_envelopes_are_terminal_typed_and_never_resubmitted(asynchronous, details, expected_error, caplog):
    failed = {"status": "failed", "error": "offline failure", "debug_ref": "debug_test", **details}
    async with _client(asynchronous, _ACCEPTED, _PENDING, failed) as (client, transport):
        poller = await _begin(client.training.begin_forward_backward, asynchronous, _SESSION, body=_FORWARD)
        for _ in range(2):
            with pytest.raises(expected_error) as caught:
                await _result(poller, asynchronous)
            assert type(caught.value) is expected_error
            assert caught.value.continuation_token is None
        if expected_error is TrainingEngineError:
            assert caught.value.session_id == _SESSION and caught.value.debug_ref == "debug_test"
        if expected_error is OperationResultUnavailableError:
            assert caught.value.operation_completed is True
        assert poller.status() == "failed" and poller.polling_method().finished()
        assert [request.method for request in transport.requests] == ["POST", "GET", "GET"]
        assert "offline-secret-not-a-token" not in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize("phase", ["submission", "poll"])
@pytest.mark.parametrize("status, payload, expected_error", [
    (409, {"error_code": "engine_dead", "message": "engine died"}, TrainingEngineError),
    (413, {"message": "Batch size (20) exceeds the maximum allowed (10)"}, BatchTooLargeError),
    (503, {"reason": "engine_busy", "message": "No capacity"}, NoCapacityError),
    (404, {"error": "missing request"}, HttpResponseError),
    (500, {"message": "unknown failure"}, HttpResponseError),
])
async def test_http_failures_classify_without_an_extra_retry_loop(asynchronous, phase, status, payload, expected_error):
    responses = [(status, payload)] if phase == "submission" else [_ACCEPTED, (status, payload)]
    async with _client(asynchronous, *responses) as (client, transport):
        with pytest.raises(expected_error) as caught:
            poller = await _begin(client.sessions.begin_unload, asynchronous, _SESSION)
            await _result(poller, asynchronous)
        assert caught.value.response is transport.responses[-1]
        assert caught.value.status_code == status
        expected_methods = ["POST"] if phase == "submission" else ["POST", "GET"]
        assert [request.method for request in transport.requests] == expected_methods
        if expected_error is BatchTooLargeError:
            assert caught.value.max_batch_size == 10 and caught.value.actual_batch_size == 20


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", [
    (503, {"reason": "engine_busy", "message": "No capacity"}, {"Retry-After": "0"}),
    ServiceRequestError("offline connection error"),
    (307, {}, {"location": "https://other.invalid/must-not-submit"}),
])
async def test_post_is_not_retried_even_if_pipeline_or_caller_enables_retries(asynchronous, failure):
    async with _client(asynchronous, failure, retry_total=5) as (client, transport):
        with pytest.raises((HttpResponseError, ServiceRequestError)):
            await _begin(
                client.training.begin_optim_step, asynchronous, _SESSION, _OPTIMIZER,
                retry_total=5, permit_redirects=True,
            )
        assert [request.method for request in transport.requests] == ["POST"]
        assert not transport.sleeps


@pytest.mark.asyncio
async def test_get_retries_remain_bounded_by_existing_pipeline(asynchronous):
    failure = (503, {"reason": "engine_busy", "message": "No capacity"})
    async with _client(asynchronous, _ACCEPTED, failure, failure, retry_total=1) as (client, transport):
        poller = await _begin(client.sessions.begin_unload, asynchronous, _SESSION)
        with pytest.raises(NoCapacityError):
            await _result(poller, asynchronous)
        assert [request.method for request in transport.requests] == ["POST", "GET", "GET"]


@pytest.mark.asyncio
async def test_exhausted_poll_transport_error_is_not_retried_by_the_adapter(asynchronous):
    async with _client(asynchronous, _ACCEPTED, ServiceRequestError("offline transport failure")) as (client, transport):
        poller = await _begin(client.sessions.begin_unload, asynchronous, _SESSION)
        for _ in range(2):
            with pytest.raises(ServiceRequestError):
                await _result(poller, asynchronous)
        assert poller.status() == "failed"
        assert [request.method for request in transport.requests] == ["POST", "GET"]


@pytest.mark.asyncio
async def test_missing_submission_session_uses_the_supplied_keyword_id(asynchronous):
    async with _client(asynchronous, {"request_id": _REQUEST}, _COMPLETED) as (client, transport):
        poller = await _begin(client.sessions.begin_unload, asynchronous, session_id=_SESSION)
        result = await _result(poller, asynchronous)
        assert result["session_id"] == _SESSION
        assert urlsplit(transport.requests[-1].url).path.endswith(
            f"/{quote(_SESSION, safe='')}/request/{quote(_REQUEST, safe='')}"
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("polling", [False, True])
@pytest.mark.parametrize("payload", [
    {}, {"request_id": "request_without_session"},
    {"session_id": "session_without_request"},
    {**_ACCEPTED, "request_id": ""}, {**_ACCEPTED, "request_id": 3}, {**_ACCEPTED, "request_id": "  "},
    {**_ACCEPTED, "session_id": ["old-array-format"]}, {**_ACCEPTED, "session_id": None},
    {**_ACCEPTED, "session_id": ""}, None, [], b"not-json",
])
async def test_invalid_submission_handles_never_poll(asynchronous, polling, payload):
    async with _client(asynchronous, payload) as (client, transport):
        # Non-object/invalid JSON can be rejected by the generated deserializer
        # before the cls callback. Valid JSON objects are checked against raw IDs.
        with pytest.raises((HttpResponseError, DeserializationError, ValueError)):
            await _begin(client.sessions.begin_create, asynchronous, body=_CREATE, polling=polling)
        assert [request.method for request in transport.requests] == ["POST"]


@pytest.mark.asyncio
async def test_invalid_returned_session_does_not_fall_back_to_valid_supplied_id(asynchronous):
    async with _client(asynchronous, {"request_id": _REQUEST, "session_id": ["not-a-string"]}) as (client, transport):
        with pytest.raises(HttpResponseError, match="session_id"):
            await _begin(client.sessions.begin_unload, asynchronous, _SESSION)
        assert len(transport.requests) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("phase", ["submission", "poll"])
async def test_does_not_accept_202_or_follow_operation_location(asynchronous, phase):
    response = (202, _ACCEPTED, {"Operation-Location": "https://other.invalid/fictitious-lro"})
    responses = [response] if phase == "submission" else [_ACCEPTED, response]
    async with _client(asynchronous, *responses) as (client, transport):
        with pytest.raises(HttpResponseError):
            poller = await _begin(client.sessions.begin_create, asynchronous, body=_CREATE)
            await _result(poller, asynchronous)
        assert len(transport.requests) == (1 if phase == "submission" else 2)
        assert all(request.url.startswith(_ENDPOINT) for request in transport.requests)


@pytest.mark.asyncio
async def test_poll_redirect_does_not_change_the_endpoint(asynchronous):
    redirect = (307, {}, {"location": "https://other.invalid/must-not-poll"})
    async with _client(asynchronous, _ACCEPTED, redirect) as (client, transport):
        poller = await _begin(client.sessions.begin_unload, asynchronous, _SESSION, permit_redirects=True)
        with pytest.raises(HttpResponseError):
            await _result(poller, asynchronous)
        assert [request.method for request in transport.requests] == ["POST", "GET"]
        assert all(request.url.startswith(_ENDPOINT) for request in transport.requests)


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [{"status": "completed"}, {"status": "completed", "result": None}])
async def test_empty_completed_unload_result_is_normalized(asynchronous, payload):
    async with _client(asynchronous, _ACCEPTED, payload) as (client, transport):
        poller = await _begin(client.sessions.begin_unload, asynchronous, _SESSION)
        result = await _result(poller, asynchronous)
        assert isinstance(result, models.OperationResult) and result.type == "unload_session"
        assert result.status == "succeeded" and result.operation_id == _REQUEST
        assert [request.method for request in transport.requests] == ["POST", "GET"]


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [
    {"status": "succeeded", "result": {}}, {"status": "running"}, {}, [],
    {"status": "completed", "result": []}, {"status": "completed", "result": "wrong"},
])
async def test_bad_poll_payloads_fail_instead_of_polling_forever(asynchronous, payload):
    async with _client(asynchronous, _ACCEPTED, payload) as (client, transport):
        poller = await _begin(client.sessions.begin_unload, asynchronous, _SESSION)
        with pytest.raises(HttpResponseError):
            await _result(poller, asynchronous)
        assert [request.method for request in transport.requests] == ["POST", "GET"]


@pytest.mark.asyncio
@pytest.mark.parametrize("options", [
    {"continuation_token": "untrusted-opaque-token"}, {"continuation_token": ""},
    {"polling": object()}, {"polling_interval": -1}, {"polling_interval": float("inf")},
    {"polling_interval": float("nan")}, {"stream": True},
])
async def test_unsupported_options_are_rejected_before_submission(asynchronous, options):
    async with _client(asynchronous) as (client, transport):
        with pytest.raises(ValueError):
            await _begin(client.sessions.begin_create, asynchronous, body=_CREATE, **options)
        assert not transport.requests


@pytest.mark.asyncio
async def test_conflicting_body_keywords_are_rejected_before_submission(asynchronous):
    async with _client(asynchronous) as (client, transport):
        with pytest.raises(TypeError, match="either 'body' or 'session'"):
            await _begin(client.sessions.begin_create, asynchronous, body=_CREATE, session=_CREATE)
        assert not transport.requests


@pytest.mark.asyncio
async def test_session_and_real_sampler_checkpoint_are_still_required(asynchronous):
    async with _client(asynchronous) as (client, transport):
        for group, mapping in _MAPPINGS.items():
            for old in mapping:
                if old == "begin_create":
                    continue
                with pytest.raises(TypeError, match="session_id"):
                    await _begin(getattr(getattr(client, group), old), asynchronous, body={})
        with pytest.raises(TypeError, match="checkpoint_id"):
            await _begin(client.sampling.begin_sample, asynchronous, _SESSION, body=_SAMPLE)
        for invalid in (None, "", 1):
            with pytest.raises(ValueError, match="checkpoint_id"):
                await _begin(client.sampling.begin_sample, asynchronous, _SESSION, body=_SAMPLE, checkpoint_id=invalid)
        assert not transport.requests


def test_installation_is_idempotent_and_does_not_replace_generated_or_existing_methods():
    class Operations:
        def create(self):
            pass

    original = Operations.create
    mapping = {"begin_create": ("create", "create_session")}
    install_legacy_pollers(Operations, mapping)
    installed = Operations.begin_create
    install_legacy_pollers(Operations, mapping)
    assert Operations.create is original and Operations.begin_create is installed
    assert installed.__name__ == "begin_create" and not iscoroutinefunction(installed)
    assert set(vars(Operations)).intersection({"begin_forward", "begin_optimizer_step", "begin_delete"}) == set()

    class AsyncOperations:
        async def create(self):
            pass

    install_legacy_pollers(AsyncOperations, mapping, asynchronous=True)
    assert iscoroutinefunction(AsyncOperations.begin_create)


@pytest.mark.asyncio
async def test_sync_result_timeout_is_native_and_does_not_resubmit():
    entered, release = Event(), Event()

    class BlockedTransport(_SequenceTransport):
        def send(self, request, **kwargs):
            if request.method == "GET":
                entered.set()
                assert release.wait(2), "Test must release the offline poll response"
            return super().send(request, **kwargs)

    transport = BlockedTransport(_ACCEPTED, _COMPLETED)
    async with _client(False, transport=transport) as (client, _):
        poller = client.sessions.begin_unload(_SESSION)
        try:
            assert entered.wait(2)
            assert poller.result(timeout=0) is None and not poller.done()
            assert poller.status() == "pending"
        finally:
            release.set()
            poller.wait(timeout=2)
        assert poller.result(timeout=2).type == "unload_session"
        assert [request.method for request in transport.requests] == ["POST", "GET"]
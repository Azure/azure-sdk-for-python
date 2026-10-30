# pylint: disable=too-many-lines
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Public text-only operations through real SDK pipelines; no network/services."""

import asyncio
import inspect
import json
from contextlib import asynccontextmanager
from copy import deepcopy

import pytest
from azure.ai.finetuningsessions import (
    FineTuningSession,
    FineTuningSessionClient,
    MalformedResponseError,
    TextOnlyTrainingChunkError,
)
from azure.ai.finetuningsessions import _patch as sync_patch
from azure.ai.finetuningsessions.aio import FineTuningSessionClient as AsyncClient
from azure.ai.finetuningsessions.aio import _patch as async_patch
from azure.ai.finetuningsessions.models import (
    AdamParams,
    LoRAConfig,
    SampleOperationResult,
    SamplingParams,
    TextOnlyAssistantMessage,
    TextOnlyInvalidSampleChoice,
    TextOnlySampleChoice,
    TextOnlySampleOperationResult,
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import (
    HttpResponseError,
    ServiceRequestError,
    ServiceResponseError,
)
from azure.core.pipeline.transport import (
    AsyncHttpResponse,
    AsyncHttpTransport,
    HttpResponse,
    HttpTransport,
)
from azure.core.utils import case_insensitive_dict

ENDPOINT = "https://unit.invalid/api/projects/p"
HISTORY = {
    "messages": [
        {"role": "system", "content": "Use the available tool."},
        {"role": "user", "content": "What is the temperature?"},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {"id": "call_1", "type": "function", "function": {"name": "weather", "arguments": '{"city":"Oslo"}'}}
            ],
        },
        {"role": "tool", "tool_call_id": "call_1", "content": "4°C"},
    ],
    "tools": [
        {
            "type": "function",
            "function": {"name": "weather", "description": "Get weather", "parameters": {"type": "object"}},
        }
    ],
}
PUBLIC_RESULT = {
    "choices": [
        {
            "index": 0,
            "message": {"role": "assistant", "content": "4°C", "tool_calls": []},
            "sample_ref": "opaque.server.reference/never-decode-this",
            "finish_reason": "stop",
        },
        {
            "index": 1,
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_2",
                        "type": "function",
                        "function": {"name": "weather", "arguments": '{"city":"Rome"}'},
                    }
                ],
            },
            "sample_ref": "another-opaque-reference",
            "finish_reason": "tool_calls",
        },
    ]
}
TRAINING = {"samples": [{"sample_ref": choice["sample_ref"], "advantage": 0.5} for choice in PUBLIC_RESULT["choices"]]}
SCALAR = {"loss_fn_output_type": "scalar", "loss_fn_outputs": [], "metrics": {"loss": 0.25, "num_samples": 2}}
ACCEPTED = (200, {"request_id": "request_test", "session_id": "session_test", "status": "pending"})


def completed(result):
    return 200, {"status": "completed", "result": result}


class _RawJson(str):
    pass


class _Response:
    def __init__(self, request, status, data):
        super().__init__(request, None)
        self.status_code = status
        self.headers = case_insensitive_dict({"Content-Type": "application/json"})
        self.content_type = "application/json"
        self.reason = "fixture"
        self.data = data

    def body(self):
        if isinstance(self.data, _RawJson):
            return self.data.encode()
        return json.dumps(self.data).encode()

    def json(self):
        if isinstance(self.data, _RawJson):
            return json.loads(self.data)
        return self.data


class _SyncResponse(_Response, HttpResponse):
    pass


class _AsyncResponse(_Response, AsyncHttpResponse):
    pass


class _Recording:
    def __init__(self, outcomes):
        self.outcomes = iter(outcomes)
        self.requests = []

    def respond(self, request, response_type):
        self.requests.append(deepcopy(request))
        outcome = next(self.outcomes)
        if isinstance(outcome, Exception):
            raise outcome
        return response_type(request, *outcome)


class _SyncTransport(_Recording, HttpTransport):
    def send(self, request, **kwargs):
        return self.respond(request, _SyncResponse)

    def open(self):
        pass

    def close(self):
        pass

    def __exit__(self, *args):
        self.close()

    def sleep(self, duration):
        pass


class _AsyncTransport(_Recording, AsyncHttpTransport):
    async def send(self, request, **kwargs):
        return self.respond(request, _AsyncResponse)

    async def open(self):
        pass

    async def close(self):
        pass

    async def __aexit__(self, *args):
        await self.close()

    async def sleep(self, duration):
        pass


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def asynchronous(request, monkeypatch):
    monkeypatch.setattr(FineTuningSession, "_start_heartbeat", lambda *a, **kw: None)
    monkeypatch.setattr(async_patch, "_start_heartbeat", lambda *a, **kw: None)
    monkeypatch.setattr(sync_patch._time, "sleep", lambda *a: None)

    async def no_sleep(*args):
        pass

    monkeypatch.setattr(async_patch.asyncio, "sleep", no_sleep)
    return request.param


@asynccontextmanager
async def session(asynchronous, outcomes):
    transport = (_AsyncTransport if asynchronous else _SyncTransport)(outcomes)
    client = (AsyncClient if asynchronous else FineTuningSessionClient)(
        ENDPOINT, AzureKeyCredential("fixture-key"), transport=transport
    )
    obj = client if asynchronous else FineTuningSession(client, "session_test")
    try:
        yield obj, transport
    finally:
        result = client.close()
        if inspect.isawaitable(result):
            await result


async def invoke(obj, name, **kwargs):
    method = getattr(obj, name)
    result = method("session_test", **kwargs) if isinstance(obj, AsyncClient) else method(**kwargs)
    return await result if inspect.isawaitable(result) else result


def body(request):
    return json.loads(request.body)


@pytest.mark.asyncio
@pytest.mark.parametrize("text_only", [False, True])
async def test_create_opt_in_only(asynchronous, text_only):
    async with session(asynchronous, [ACCEPTED, completed({})]) as (obj, transport):
        kwargs = {
            "base_model": "Qwen/Qwen3.6-35B-A3B",
            "lora_config": LoRAConfig(rank=8),
            "user_metadata": {"flag": True},
            "text_only": text_only,
        }
        if asynchronous:
            assert await obj.create_session(**kwargs) == "session_test"
        else:
            FineTuningSession.create(obj._client, **kwargs)
        payload = body(transport.requests[0])
        assert payload.get("text_only", False) is text_only
        assert ("text_only" in payload) is text_only
        assert payload["user_metadata"] == {"flag": True}
        assert transport.requests[0].url == ENDPOINT + "/fine_tuning/sessions?api-version=v1"


@pytest.mark.asyncio
async def test_assistant_tool_call_history_can_omit_content(asynchronous):
    assert TextOnlyAssistantMessage.__required_keys__ == {"role"}
    history = deepcopy(HISTORY)
    del history["messages"][2]["content"]
    async with session(asynchronous, [ACCEPTED, completed(PUBLIC_RESULT)]) as (obj, transport):
        await invoke(
            obj,
            "sample",
            text_only_input=history,
            sampling_params=SamplingParams(max_tokens=32),
            checkpoint_id="ckpt_sampler",
        )
        assert body(transport.requests[0])["text_only_input"] == history


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "reason,finish",
    [
        ("output_token_limit", "length"),
        ("missing_private_boundary", "stop"),
        ("malformed_tool_call", "stop"),
        ("invalid_tool_arguments", "stop"),
        ("invalid_public_output", "stop"),
    ],
)
async def test_invalid_choices_are_typed_and_trainable_without_messages(asynchronous, reason, finish):
    invalid = {
        "index": 1,
        "sample_ref": "failed-generation-reference",
        "outcome": "invalid_model_output",
        "reason": reason,
        "finish_reason": finish,
    }
    result = {"choices": [PUBLIC_RESULT["choices"][0], invalid]}
    async with session(
        asynchronous,
        [
            ACCEPTED,
            completed(result),
            ACCEPTED,
            completed(SCALAR),
        ],
    ) as (obj, transport):
        sampled = await invoke(
            obj,
            "sample",
            text_only_input=HISTORY,
            sampling_params=SamplingParams(max_tokens=32),
            checkpoint_id="ckpt",
        )
        assert isinstance(sampled.choices[0], TextOnlySampleChoice)
        choice = sampled.choices[1]
        assert isinstance(choice, TextOnlyInvalidSampleChoice)
        assert choice.reason == reason and choice.as_dict() == invalid
        assert not hasattr(choice, "message")
        await invoke(
            obj,
            "forward_backward",
            text_only_input={
                "samples": [{"sample_ref": choice.sample_ref, "advantage": -0.5}],
            },
        )
        assert [request.method for request in transport.requests] == ["POST", "GET", "POST", "GET"]
        assert body(transport.requests[2])["text_only_input"]["samples"] == [
            {"sample_ref": "failed-generation-reference", "advantage": -0.5},
        ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "change",
    [
        {"message": None},
        {"message": {"role": "assistant", "content": "must not appear"}},
        {"reason": "private generated detail"},
        {"reason": "output_token_limit"},
        {"outcome": "success"},
        {"index": True},
        {"sample_ref": 7},
    ],
)
async def test_malformed_invalid_choice_never_retries_sampling(asynchronous, change):
    invalid = {
        "index": 0,
        "sample_ref": "failed-reference",
        "outcome": "invalid_model_output",
        "reason": "missing_private_boundary",
        "finish_reason": "stop",
        **change,
    }
    async with session(asynchronous, [ACCEPTED, completed({"choices": [invalid]})]) as (obj, transport):
        with pytest.raises(ValueError):
            await invoke(
                obj,
                "sample",
                text_only_input=HISTORY,
                sampling_params=SamplingParams(max_tokens=32),
                checkpoint_id="ckpt",
            )
        assert [request.method for request in transport.requests] == ["POST", "GET"]


@pytest.mark.asyncio
async def test_sample_public_choices_and_edited_history(asynchronous):
    history = deepcopy(HISTORY)
    async with session(asynchronous, [ACCEPTED, (200, {"status": "pending"}), completed(PUBLIC_RESULT)]) as (
        obj,
        transport,
    ):
        result = await invoke(
            obj,
            "sample",
            text_only_input=history,
            sampling_params=SamplingParams(max_tokens=32),
            checkpoint_id="ckpt_sampler",
            num_samples=2,
            sampling_session_id="sampling_test",
            seq_id=7,
        )
        assert isinstance(result, TextOnlySampleOperationResult)
        assert not isinstance(result, SampleOperationResult)
        assert all(isinstance(choice, TextOnlySampleChoice) for choice in result.choices)
        assert [choice.sample_ref for choice in result.choices] == [c["sample_ref"] for c in PUBLIC_RESULT["choices"]]
        assert result.choices[1].message == PUBLIC_RESULT["choices"][1]["message"]
        assert result.choices[1].finish_reason == "tool_calls"
        assert "sequences" not in result.as_dict()
        payload = body(transport.requests[0])
        assert payload["text_only_input"] == HISTORY
        assert "prompt" not in payload and "prompt_logprobs" not in payload and "topk_prompt_logprobs" not in payload
        assert payload["sampling_session_id"] == "sampling_test" and payload["seq_id"] == 7
        assert payload["num_samples"] == 2
        assert "checkpoint_id=ckpt_sampler" in transport.requests[0].url
        assert all(r.headers["api-key"] == "fixture-key" for r in transport.requests)
        assert all(r.headers["Foundry-Features"] == "FineTuningSessions=V1Preview" for r in transport.requests)
        assert (
            transport.requests[-1].url
            == ENDPOINT + "/fine_tuning/sessions/session_test/request/request_test?api-version=v1"
        )
    assert history == HISTORY


@pytest.mark.asyncio
async def test_compacted_orphan_tool_result_keeps_explicit_name(asynchronous):
    compacted = {"messages": [{"role": "tool", "tool_call_id": "old", "name": "weather", "content": "4°C"}]}
    async with session(asynchronous, [ACCEPTED, completed(PUBLIC_RESULT)]) as (obj, transport):
        await invoke(
            obj, "sample", text_only_input=compacted, sampling_params=SamplingParams(max_tokens=8), checkpoint_id="s"
        )
        assert body(transport.requests[0])["text_only_input"] == compacted


@pytest.mark.asyncio
@pytest.mark.parametrize("ref", [123, None, "", {"locator": "not-a-string"}])
async def test_malformed_response_ref_is_never_coerced_or_forged(asynchronous, ref):
    malformed = deepcopy(PUBLIC_RESULT)
    malformed["choices"][0]["sample_ref"] = ref
    async with session(asynchronous, [ACCEPTED, completed(malformed)]) as (obj, transport):
        with pytest.raises(ValueError, match="opaque string"):
            await invoke(
                obj,
                "sample",
                text_only_input=HISTORY,
                sampling_params=SamplingParams(max_tokens=8),
                checkpoint_id="s",
            )
        assert [r.method for r in transport.requests] == ["POST", "GET"]


@pytest.mark.asyncio
@pytest.mark.parametrize("loss_fn", [None, "importance_sampling", "ppo", "cispo", "sapo"])
async def test_scalar_reference_training(asynchronous, loss_fn):
    training = deepcopy(TRAINING)
    if loss_fn is not None:
        training.update(loss_fn=loss_fn, loss_fn_config={})
    async with session(asynchronous, [ACCEPTED, completed(SCALAR)]) as (obj, transport):
        result = await invoke(obj, "forward_backward", text_only_input=training)
        assert result.loss_fn_output_type == "scalar"
        assert result.loss_fn_outputs == []
        assert result.metrics == SCALAR["metrics"]
        payload = body(transport.requests[0])
        assert set(payload) == {"text_only_input"}
        assert payload["text_only_input"]["samples"] == TRAINING["samples"]
        assert payload["text_only_input"]["loss_fn"] == (loss_fn or "importance_sampling")
    assert TRAINING == {
        "samples": [{"sample_ref": c["sample_ref"], "advantage": 0.5} for c in PUBLIC_RESULT["choices"]]
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("surface", ["forward_backward", "forward_backward_post", "forward_backward_async"])
@pytest.mark.parametrize("should_retry", [False, True])
async def test_reference_completion_failure_never_reposts(asynchronous, surface, should_retry):
    if not asynchronous and surface != "forward_backward":
        pytest.skip("Pipelined handles are async-only")
    failure = (200, {"status": "failed", "error": "completion ambiguous", "should_retry": should_retry})
    async with session(asynchronous, [ACCEPTED, failure]) as (obj, transport):
        with pytest.raises((RuntimeError, HttpResponseError)):
            result = await invoke(obj, surface, text_only_input=TRAINING)
            if surface == "forward_backward_post":
                await result.poll_result()
            elif surface == "forward_backward_async":
                await result
        assert [r.method for r in transport.requests] == ["POST", "GET"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failure",
    [
        (503, {"error": "ambiguous", "should_retry": False}),
        (408, {}),
        ServiceRequestError("connection lost"),
        ServiceResponseError("response lost"),
    ],
)
async def test_reference_submit_ambiguity_never_reposts(asynchronous, failure):
    async with session(asynchronous, [failure]) as (obj, transport):
        with pytest.raises((HttpResponseError, ServiceRequestError, ServiceResponseError)):
            await invoke(obj, "forward_backward", text_only_input=TRAINING)
        assert len(transport.requests) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("poll_failure", [(503, {}), ServiceResponseError("status response lost")])
async def test_reference_status_retries_only_get(asynchronous, poll_failure):
    async with session(asynchronous, [ACCEPTED, poll_failure, completed(SCALAR)]) as (obj, transport):
        result = await invoke(obj, "forward_backward", text_only_input=TRAINING)
        assert result.loss_fn_output_type == "scalar"
        assert [r.method for r in transport.requests] == ["POST", "GET", "GET"]


@pytest.mark.asyncio
async def test_text_sampling_retains_429_backpressure(asynchronous):
    async with session(asynchronous, [(429, {}), ACCEPTED, completed(PUBLIC_RESULT)]) as (obj, transport):
        result = await invoke(
            obj,
            "sample",
            text_only_input=HISTORY,
            sampling_params=SamplingParams(max_tokens=8),
            checkpoint_id="s",
        )
        assert isinstance(result, TextOnlySampleOperationResult)
        assert [r.method for r in transport.requests] == ["POST", "POST", "GET"]
        assert body(transport.requests[0]) == body(transport.requests[1])


@pytest.mark.asyncio
@pytest.mark.parametrize("surface", ["forward_backward_post", "forward_backward_async"])
async def test_reference_pipelined_success(surface):
    async with session(True, [ACCEPTED, completed(SCALAR)]) as (obj, transport):
        result = await invoke(obj, surface, text_only_input=TRAINING)
        if surface == "forward_backward_post":
            result = await result.poll_result()
        else:
            result = await result
        assert result.loss_fn_outputs == []
        assert len(transport.requests) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "extra",
    [
        {"prompt_tokens": [1]},
        {"prompt_logprobs": True},
        {"topk_prompt_logprobs": 1},
        {"sampling_params": SamplingParams(max_tokens=8, response_format={"type": "json_object"})},
        {"sampling_params": SamplingParams(max_tokens=8, stop_criteria=["STOP"])},
        {"sampling_params": SamplingParams(max_tokens=8, stop_criteria=[1])},
    ],
)
async def test_text_sampling_rejects_incompatible_options(asynchronous, extra):
    async with session(asynchronous, []) as (obj, transport):
        kwargs = {"text_only_input": HISTORY, "sampling_params": SamplingParams(max_tokens=8), "checkpoint_id": "s"}
        kwargs.update(extra)
        with pytest.raises(ValueError):
            await invoke(obj, "sample", **kwargs)
        assert not transport.requests


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid",
    [
        {"messages": [{"role": "developer", "content": "no"}]},
        {"messages": [{"role": "user", "content": [{"type": "text", "text": "no"}]}]},
        {"messages": [{"role": "user", "content": "text", "tokens": [1]}]},
        {"messages": [{"role": "assistant", "content": "text", "thinking": "private"}]},
        {"messages": [{"role": "tool", "tool_call_id": "orphan", "content": "needs name"}]},
        {
            "messages": [
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{"id": "c", "type": "function", "function": {"name": "f", "arguments": "[]"}}],
                }
            ]
        },
        {"messages": [], "parent_sample_ref": "no"},
    ],
)
async def test_text_sampling_rejects_outside_public_subset(asynchronous, invalid):
    async with session(asynchronous, []) as (obj, transport):
        with pytest.raises(ValueError):
            await invoke(
                obj, "sample", text_only_input=invalid, sampling_params=SamplingParams(max_tokens=8), checkpoint_id="s"
            )
        assert not transport.requests


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "training,extra",
    [
        (TRAINING, {"batch": []}),
        (TRAINING, {"loss_fn": "ppo"}),
        ({"samples": []}, {}),
        ({"samples": [{"sample_ref": "opaque", "advantage": float("nan")}]}, {}),
        ({"samples": [{"sample_ref": "opaque", "advantage": float("inf")}]}, {}),
        ({"samples": [{"sample_ref": "opaque", "advantage": 10**400}]}, {}),
        ({"samples": [{"sample_ref": "opaque", "advantage": True}]}, {}),
        ({"samples": [{"sample_ref": "opaque", "advantage": [0.5]}]}, {}),
        ({"samples": [TRAINING["samples"][0]] * 2}, {}),
        ({"samples": TRAINING["samples"], "loss_fn": "cross_entropy"}, {}),
    ],
)
async def test_reference_training_rejects_invalid_or_mixed_inputs(asynchronous, training, extra):
    async with session(asynchronous, []) as (obj, transport):
        with pytest.raises(ValueError):
            await invoke(obj, "forward_backward", text_only_input=training, **extra)
        assert not transport.requests


@pytest.mark.asyncio
async def test_token_native_sample_unchanged(asynchronous):
    native = {"sequences": [{"tokens": [2, 3], "logprobs": [-0.1, -0.2]}], "prompt_tokens": 1}
    async with session(asynchronous, [ACCEPTED, completed(native)]) as (obj, transport):
        result = await invoke(
            obj, "sample", prompt_tokens=[1], sampling_params=SamplingParams(max_tokens=8), checkpoint_id="s"
        )
        assert isinstance(result, SampleOperationResult)
        assert result.sequences[0].tokens == [2, 3]
        assert "text_only_input" not in body(transport.requests[0])


@pytest.mark.asyncio
async def test_sampling_and_optimizer_need_no_lifetime_batch_identifiers(asynchronous):
    history = deepcopy(HISTORY)
    async with session(asynchronous, [ACCEPTED, completed(PUBLIC_RESULT), ACCEPTED, completed({"metrics": {}})]) as (
        obj,
        transport,
    ):
        await invoke(
            obj, "sample", text_only_input=history, sampling_params=SamplingParams(max_tokens=32), checkpoint_id="s"
        )
        await invoke(obj, "optim_step", adam_params=AdamParams(learning_rate=1e-5))
        assert body(transport.requests[0])["text_only_input"] == history
        assert body(transport.requests[2]) == {"adam_params": {"learning_rate": 1e-5}}


@pytest.mark.asyncio
async def test_removed_sampling_bucket_is_rejected_before_submission(asynchronous):
    async with session(asynchronous, []) as (obj, transport):
        with pytest.raises(ValueError):
            await invoke(
                obj,
                "sample",
                text_only_input={**HISTORY, "rollout_batch_id": "obsolete"},
                sampling_params=SamplingParams(max_tokens=8),
                checkpoint_id="s",
            )
        assert not transport.requests


@pytest.mark.asyncio
async def test_async_optimizer_post_and_task_keep_native_request_shape():
    for method in ("optim_step_post", "optim_step_async"):
        async with session(True, [ACCEPTED, completed({"metrics": {}})]) as (obj, transport):
            pending = await getattr(obj, method)(
                "session_test",
                AdamParams(learning_rate=1e-5),
            )
            if method == "optim_step_post":
                await pending.poll_result()
            else:
                await pending
            assert body(transport.requests[0]) == {"adam_params": {"learning_rate": 1e-5}}


def _reference_training(count):
    return {
        "samples": [{"sample_ref": f"opaque-reference-{index}", "advantage": 0.5} for index in range(count)],
        "loss_fn": "ppo",
        "loss_fn_config": {"clip_ratio": 0.2},
    }


def _chunk_accepted(index):
    return 200, {"request_id": f"chunk_{index}", "session_id": "session_test", "status": "pending"}


def _chunk_result(index):
    return completed(
        {
            "loss_fn_output_type": "scalar",
            "loss_fn_outputs": [],
            "metrics": {"loss:mean": float(index), "total_loss:sum": float(index), "diagnostic": float(index)},
        }
    )


async def _training_result(obj, surface, training, **kwargs):
    result = await invoke(obj, surface, text_only_input=training, **kwargs)
    if surface == "forward_backward_post":
        return await result.poll_result()
    if surface == "forward_backward_async":
        return await result
    return result


@pytest.mark.asyncio
@pytest.mark.parametrize("surface", ["forward_backward", "forward_backward_post", "forward_backward_async"])
@pytest.mark.parametrize("count", [1024, 1025])
async def test_reference_count_chunking_on_every_surface(asynchronous, surface, count, monkeypatch):
    if not asynchronous and surface != "forward_backward":
        pytest.skip("Pipelined handles are async-only")
    training = _reference_training(count)
    original = deepcopy(training)
    expected_sizes = [1024, 1] if count == 1025 else [1024]
    outcomes = (
        [_chunk_accepted(i) for i in range(len(expected_sizes))]
        + [_chunk_result(i + 1) for i in range(len(expected_sizes))]
        if asynchronous
        else [outcome for i in range(len(expected_sizes)) for outcome in (_chunk_accepted(i), _chunk_result(i + 1))]
    )

    def native_chunker_must_not_run(*args):
        raise AssertionError("Protected training must not change or use native chunking")

    monkeypatch.setattr(sync_patch, "_chunk_data", native_chunker_must_not_run)
    monkeypatch.setattr(async_patch, "_chunk_data", native_chunker_must_not_run)
    async with session(asynchronous, outcomes) as (obj, transport):
        result = await _training_result(obj, surface, training)
        posts = [r for r in transport.requests if r.method == "POST"]
        inputs = [body(r)["text_only_input"] for r in posts]
        assert [len(data["samples"]) for data in inputs] == expected_sizes
        assert [sample for data in inputs for sample in data["samples"]] == training["samples"]
        assert all(data["loss_fn"] == "ppo" and data["loss_fn_config"] == {"clip_ratio": 0.2} for data in inputs)
        assert result.loss_fn_output_type == "scalar"
        assert result.loss_fn_outputs == []
        if count == 1025:
            assert result.total_loss == 3.0
            assert result.metrics["loss:mean"] == pytest.approx((1024 + 2) / 1025)
            assert "diagnostic" not in result.metrics
            assert result.metrics["chunk_1/diagnostic"] == 1.0
            assert result.metrics["chunk_2/diagnostic"] == 2.0
    assert training == original


@pytest.mark.parametrize("budget_delta,expected_sizes", [(0, [2]), (-1, [1, 1])])
def test_reference_chunks_measure_actual_json_bytes_with_wrapper_and_unicode(
    monkeypatch,
    budget_delta,
    expected_sizes,
):
    training = _reference_training(2)
    training["samples"][0]["sample_ref"] = 'opaque-☃-"\\'
    full_body = sync_patch._text_training_body(training, None, "cross_entropy", None)

    def encode(value):
        return json.dumps(value, cls=sync_patch._SdkJSONEncoder, exclude_readonly=True).encode("utf-8")

    budget = len(encode(full_body)) + budget_delta
    monkeypatch.setattr(sync_patch, "_MAX_CHUNK_BYTES", budget)
    chunks = sync_patch._chunk_text_training_data(training, None, "cross_entropy", None)
    assert [len(chunk["text_only_input"]["samples"]) for chunk in chunks] == expected_sizes
    assert all(len(encode(chunk)) <= budget for chunk in chunks)


def test_reference_chunking_keeps_one_oversized_entry_intact(monkeypatch):
    monkeypatch.setattr(sync_patch, "_MAX_CHUNK_BYTES", 1)
    chunks = sync_patch._chunk_text_training_data(_reference_training(2), None, "cross_entropy", None)
    assert [len(chunk["text_only_input"]["samples"]) for chunk in chunks] == [1, 1]


def test_reference_metric_labels_do_not_overwrite_declared_reductions():
    results = [
        sync_patch.ForwardBackwardOperationResult(
            {
                "metrics": {"orphan:mean": 9.0, "chunk_1/orphan:mean": 3.0},
            }
        ),
        sync_patch.ForwardBackwardOperationResult({"metrics": {"chunk_1/orphan:mean": 7.0}}),
    ]
    combined = sync_patch._combine_text_training_results(results, [1, 1])
    assert combined.metrics == {"chunk_1/orphan:mean": 5.0, "chunk_1/chunk_1/orphan:mean": 9.0}
    assert combined.loss_fn_outputs == []


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid", ["duplicate", "nonfinite"])
@pytest.mark.parametrize("surface", ["forward_backward", "forward_backward_post", "forward_backward_async"])
async def test_validate_entire_reference_batch_before_any_post(asynchronous, invalid, surface, monkeypatch):
    if not asynchronous and surface != "forward_backward":
        pytest.skip("Pipelined handles are async-only")
    monkeypatch.setattr(sync_patch, "_MAX_CHUNK_LEN", 1)
    training = _reference_training(3)
    if invalid == "duplicate":
        training["samples"][-1] = dict(training["samples"][0])
    else:
        training["samples"][-1]["advantage"] = float("nan")
    async with session(asynchronous, []) as (obj, transport):
        with pytest.raises(ValueError):
            await _training_result(obj, surface, training)
        assert not transport.requests


@pytest.mark.asyncio
@pytest.mark.parametrize("surface", ["forward_backward", "forward_backward_post", "forward_backward_async"])
async def test_reference_byte_limit_matches_recorded_wire_bodies(asynchronous, surface, monkeypatch):
    if not asynchronous and surface != "forward_backward":
        pytest.skip("Pipelined handles are async-only")
    training = _reference_training(2)
    training["samples"][0]["sample_ref"] = 'opaque-☃-"\\'
    full_body = sync_patch._text_training_body(training, None, "cross_entropy", None)
    budget = len(json.dumps(full_body, cls=sync_patch._SdkJSONEncoder, exclude_readonly=True).encode("utf-8")) - 1
    monkeypatch.setattr(sync_patch, "_MAX_CHUNK_BYTES", budget)
    outcomes = (
        [_chunk_accepted(0), _chunk_accepted(1), _chunk_result(1), _chunk_result(2)]
        if asynchronous
        else [_chunk_accepted(0), _chunk_result(1), _chunk_accepted(1), _chunk_result(2)]
    )
    async with session(asynchronous, outcomes) as (obj, transport):
        await _training_result(obj, surface, training)
        posts = [r for r in transport.requests if r.method == "POST"]
        assert [len(body(r)["text_only_input"]["samples"]) for r in posts] == [1, 1]
        assert all(len(r.body.encode("utf-8") if isinstance(r.body, str) else r.body) <= budget for r in posts)


@pytest.mark.asyncio
@pytest.mark.parametrize("surface", ["forward_backward", "forward_backward_post", "forward_backward_async"])
async def test_reference_partial_submission_exposes_known_ids_without_replay(
    asynchronous,
    surface,
    monkeypatch,
):
    if not asynchronous and surface != "forward_backward":
        pytest.skip("Pipelined handles are async-only")
    monkeypatch.setattr(sync_patch, "_MAX_CHUNK_LEN", 1)
    failure = (503, {"error": "submission outcome ambiguous"})
    outcomes = [_chunk_accepted(0), failure] if asynchronous else [_chunk_accepted(0), _chunk_result(1), failure]
    async with session(asynchronous, outcomes) as (obj, transport):
        with pytest.raises(TextOnlyTrainingChunkError) as error:
            await _training_result(obj, surface, _reference_training(3))
        assert error.value.request_ids == ["chunk_0"]
        assert error.value.chunk_index == 1
        assert isinstance(error.value.__cause__, HttpResponseError)
        assert len([r for r in transport.requests if r.method == "POST"]) == 2
        assert all("/forward_backward?" in r.url for r in transport.requests if r.method == "POST")


@pytest.mark.asyncio
@pytest.mark.parametrize("surface", ["forward_backward", "forward_backward_post", "forward_backward_async"])
async def test_reference_multichunk_poll_failure_does_not_replay(
    asynchronous,
    surface,
    monkeypatch,
):
    if not asynchronous and surface != "forward_backward":
        pytest.skip("Pipelined handles are async-only")
    monkeypatch.setattr(sync_patch, "_MAX_CHUNK_LEN", 1)
    failure = (200, {"status": "failed", "error": "uncertain", "should_retry": True})
    outcomes = (
        [_chunk_accepted(0), _chunk_accepted(1), failure]
        if asynchronous
        else [_chunk_accepted(0), _chunk_result(1), _chunk_accepted(1), failure]
    )
    async with session(asynchronous, outcomes) as (obj, transport):
        with pytest.raises(TextOnlyTrainingChunkError) as error:
            await _training_result(obj, surface, _reference_training(2))
        assert error.value.request_ids == ["chunk_0", "chunk_1"]
        assert error.value.chunk_index == (0 if asynchronous else 1)
        assert isinstance(error.value.__cause__, (RuntimeError, HttpResponseError))
        assert [r.method for r in transport.requests].count("POST") == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("surface", ["forward_backward", "forward_backward_post", "forward_backward_async"])
@pytest.mark.parametrize(
    "malformed",
    [
        None,
        [],
        "PRIVATE_RESPONSE",
        {},
        {"request_id": ""},
        {"request_id": ["PRIVATE_ID"]},
        {"request_id": "valid", "session_id": []},
        _RawJson("{"),
    ],
)
async def test_reference_malformed_submission_preserves_accepted_ids(
    asynchronous,
    surface,
    malformed,
    monkeypatch,
):
    if not asynchronous and surface != "forward_backward":
        pytest.skip("Pipelined handles are async-only")
    monkeypatch.setattr(sync_patch, "_MAX_CHUNK_LEN", 1)
    failure = (200, malformed)
    outcomes = [_chunk_accepted(0), failure] if asynchronous else [_chunk_accepted(0), _chunk_result(1), failure]
    async with session(asynchronous, outcomes) as (obj, transport):
        with pytest.raises(TextOnlyTrainingChunkError) as error:
            await _training_result(obj, surface, _reference_training(3))
        expected_ids = (
            ["chunk_0", "valid"]
            if isinstance(malformed, dict) and malformed.get("request_id") == "valid"
            else ["chunk_0"]
        )
        assert error.value.request_ids == expected_ids
        assert error.value.chunk_index == 1
        assert isinstance(error.value.__cause__, MalformedResponseError)
        assert "PRIVATE" not in str(error.value.__cause__)
        assert [r.method for r in transport.requests].count("POST") == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("surface", ["forward_backward", "forward_backward_post", "forward_backward_async"])
@pytest.mark.parametrize("session_id", [None, "", [], {"private": "PRIVATE_RESPONSE"}])
async def test_single_reference_malformed_submission_retains_acknowledged_id(
    asynchronous,
    surface,
    session_id,
):
    if not asynchronous and surface != "forward_backward":
        pytest.skip("Pipelined handles are async-only")
    async with session(asynchronous, [(200, {"request_id": "valid", "session_id": session_id})]) as (obj, transport):
        with pytest.raises(MalformedResponseError) as error:
            await _training_result(obj, surface, _reference_training(1))
        assert error.value.request_id == "valid"
        assert "PRIVATE" not in str(error.value)
        assert [r.method for r in transport.requests] == ["POST"]


@pytest.mark.asyncio
@pytest.mark.parametrize("surface", ["forward_backward", "forward_backward_post", "forward_backward_async"])
@pytest.mark.parametrize(
    "malformed",
    [
        None,
        [],
        "PRIVATE_RESPONSE",
        {},
        {"status": []},
        {"status": "completed", "result": None},
        {"status": "completed", "result": []},
        {"status": "completed", "result": {**SCALAR, "metrics": []}},
        {"status": "completed", "result": {**SCALAR, "metrics": {"invalid": []}}},
        {"status": "completed", "result": {**SCALAR, "metrics": {"invalid": float("nan")}}},
        {"status": "completed", "result": {**SCALAR, "metrics": {"invalid": 10**400}}},
        {"status": "completed", "result": {**SCALAR, "loss_fn_outputs": [{"private": 123}]}},
        _RawJson("{"),
    ],
)
async def test_reference_malformed_poll_preserves_all_accepted_ids(
    asynchronous,
    surface,
    malformed,
    monkeypatch,
):
    if not asynchronous and surface != "forward_backward":
        pytest.skip("Pipelined handles are async-only")
    monkeypatch.setattr(sync_patch, "_MAX_CHUNK_LEN", 1)
    failure = (200, malformed)
    outcomes = (
        [_chunk_accepted(0), _chunk_accepted(1), failure]
        if asynchronous
        else [_chunk_accepted(0), _chunk_result(1), _chunk_accepted(1), failure]
    )
    async with session(asynchronous, outcomes) as (obj, transport):
        with pytest.raises(TextOnlyTrainingChunkError) as error:
            await _training_result(obj, surface, _reference_training(2))
        assert error.value.request_ids == ["chunk_0", "chunk_1"]
        assert error.value.chunk_index == (0 if asynchronous else 1)
        assert isinstance(error.value.__cause__, MalformedResponseError)
        assert "PRIVATE" not in str(error.value.__cause__)
        assert [r.method for r in transport.requests].count("POST") == 2


@pytest.mark.asyncio
async def test_reference_async_waves_finish_before_optimizer(monkeypatch):
    monkeypatch.setattr(sync_patch, "_MAX_CHUNK_LEN", 1)
    outcomes = [outcome for i in range(3) for outcome in (_chunk_accepted(i), _chunk_result(i + 1))] + [
        ACCEPTED,
        completed({"metrics": {}}),
    ]
    async with session(True, outcomes) as (obj, transport):
        task = await invoke(
            obj,
            "forward_backward_async",
            text_only_input=_reference_training(3),
            max_chunks_per_wave=1,
        )
        assert task.done()
        result = await task
        assert result.total_loss == 6.0
        assert result.metrics["loss:mean"] == 2.0
        assert result.metrics["chunk_3/diagnostic"] == 3.0
        assert [r.method for r in transport.requests] == ["POST", "GET"] * 3
        await invoke(obj, "optim_step", adam_params=AdamParams(learning_rate=1e-5))
        assert "/optim_step?" in transport.requests[-2].url


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("failure", "expected_ids"),
    [
        ((503, {}), ["chunk_0"]),
        ((200, {"request_id": "valid", "session_id": []}), ["chunk_0", "valid"]),
    ],
)
async def test_reference_wave_failure_keeps_prior_wave_ids(monkeypatch, failure, expected_ids):
    monkeypatch.setattr(sync_patch, "_MAX_CHUNK_LEN", 1)
    outcomes = [_chunk_accepted(0), _chunk_result(1), failure]
    async with session(True, outcomes) as (obj, transport):
        with pytest.raises(TextOnlyTrainingChunkError) as error:
            await invoke(
                obj,
                "forward_backward_async",
                text_only_input=_reference_training(3),
                max_chunks_per_wave=1,
            )
        assert error.value.request_ids == expected_ids
        assert error.value.chunk_index == 1
        assert [r.method for r in transport.requests] == ["POST", "GET", "POST"]


@pytest.mark.asyncio
async def test_reference_multichunk_async_waits_for_completion_before_return(monkeypatch):
    monkeypatch.setattr(sync_patch, "_MAX_CHUNK_LEN", 1)
    polling = asyncio.Event()
    release = asyncio.Event()
    submitted = []

    async def post(client, subpath, request_body, *, on_submit):
        submitted.append(request_body)
        request_id = f"chunk_{len(submitted)}"
        on_submit(request_id)
        return request_id, "forward_backward"

    async def poll(*args, **kwargs):
        polling.set()
        await release.wait()
        return sync_patch.ForwardBackwardOperationResult(
            {
                "loss_fn_output_type": "scalar",
                "loss_fn_outputs": [],
                "metrics": {"loss:mean": 1.0},
            }
        )

    monkeypatch.setattr(async_patch, "_post", post)
    monkeypatch.setattr(async_patch, "_poll_with_resubmit", poll)
    call = asyncio.create_task(
        async_patch.forward_backward_async(
            object(),
            "session_test",
            text_only_input=_reference_training(2),
        )
    )
    await polling.wait()
    assert len(submitted) == 2
    assert not call.done()
    release.set()
    result_task = await call
    assert result_task.done()
    assert (await result_task).loss_fn_outputs == []


@pytest.mark.asyncio
async def test_reference_cancelled_submission_stops_without_replay(monkeypatch, caplog):
    monkeypatch.setattr(sync_patch, "_MAX_CHUNK_LEN", 1)
    second_post = asyncio.Event()
    calls = []

    async def post(client, subpath, request_body, *, on_submit):
        calls.append(request_body)
        if len(calls) == 1:
            on_submit("accepted_before_cancel")
            return "accepted_before_cancel", "forward_backward"
        second_post.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(async_patch, "_post", post)
    task = asyncio.create_task(
        async_patch.forward_backward_post(
            object(),
            "session_test",
            text_only_input=_reference_training(3),
        )
    )
    await second_post.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert len(calls) == 2
    assert "accepted_before_cancel" in caplog.text

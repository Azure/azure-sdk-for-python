# ---------------------------------------------------------------------------
# Unit tests for FineTuningSession (_patch.py convenience wrapper).
# ---------------------------------------------------------------------------
import json

import pytest

from azure.ai.finetuning_sessions import FineTuningSession
from azure.ai.finetuning_sessions.aio import _patch as aio_patch
from azure.ai.finetuning_sessions._patch import _normalize_loom_result
from azure.ai.finetuning_sessions._utils.model_base import SdkJSONEncoder, _deserialize
from azure.ai.finetuning_sessions.models import (
    AdamParams,
    LoRAConfig,
    CreateSessionRequest,
    OperationResult,
    SampleOperationResult,
    SamplingParams,
)


class TestFineTuningSessionInstantiation:

    def test_session_id_stored(self, client):
        s = FineTuningSession(client, session_id="abc123")
        assert s.session_id == "abc123"

    def test_client_stored(self, client):
        s = FineTuningSession(client, session_id="abc123")
        assert s._client is client


class TestSubClients:

    def test_all_sub_clients_present(self, client):
        for name in ("sessions", "training", "checkpoints", "sampling", "operations"):
            assert hasattr(client, name), f"missing: client.{name}"


class TestForwardBackward:

    def test_returns_operation_result(self, session, batch):
        result = session.forward_backward(batch, loss_fn="cross_entropy")
        assert isinstance(result, OperationResult)

    def test_default_loss_fn_is_cross_entropy(self, session, batch, transport):
        session.forward_backward(batch)
        req = transport.requests[0]
        body = json.loads(req.body)
        assert body["forward_backward_input"]["loss_fn"] == "cross_entropy"

    def test_custom_loss_fn(self, session, batch, transport):
        session.forward_backward(batch, loss_fn="dpo")
        req = transport.requests[0]
        body = json.loads(req.body)
        assert body["forward_backward_input"]["loss_fn"] == "dpo"

    def test_request_targets_correct_session(self, session, batch, transport):
        session.forward_backward(batch)
        req = transport.requests[0]
        assert "session_test" in req.url

    def test_preview_header_sent(self, session, batch, transport):
        session.forward_backward(batch)
        req = transport.requests[0]
        assert req.headers.get("Foundry-Features") == "FineTuningSessions=V1Preview"


class TestOptimStep:

    def test_returns_operation_result(self, session):
        params = AdamParams(learning_rate=1e-4, beta1=0.9, beta2=0.95, eps=1e-12, weight_decay=0.0)
        result = session.optim_step(params)
        assert isinstance(result, OperationResult)

    def test_request_contains_adam_params(self, session, transport):
        params = AdamParams(learning_rate=2e-5, beta1=0.9, beta2=0.95, eps=1e-12, weight_decay=0.01)
        session.optim_step(params)
        req = transport.requests[0]
        body = json.loads(req.body)
        assert body["adam_params"]["learning_rate"] == pytest.approx(2e-5)

    def test_request_targets_correct_session(self, session, transport):
        session.optim_step(AdamParams(learning_rate=1e-4, beta1=0.9, beta2=0.95, eps=1e-12, weight_decay=0.0))
        assert "session_test" in transport.requests[0].url


class TestSaveWeights:

    def test_returns_operation_result(self, session):
        assert isinstance(session.save_weights("my_ckpt"), OperationResult)

    def test_request_contains_path(self, session, transport):
        session.save_weights("sft_piglatin_v1")
        body = json.loads(transport.requests[0].body)
        assert body["path"] == "sft_piglatin_v1"


class TestSaveWeightsForSampler:

    def test_returns_operation_result(self, session):
        assert isinstance(session.save_weights_for_sampler(seq_id=0), OperationResult)

    def test_request_contains_seq_id(self, session, transport):
        session.save_weights_for_sampler(seq_id=7)
        body = json.loads(transport.requests[0].body)
        assert body["seq_id"] == 7

    def test_optional_path(self, session, transport):
        session.save_weights_for_sampler(seq_id=0, path="explicit_path")
        body = json.loads(transport.requests[0].body)
        assert body["path"] == "explicit_path"


class TestSample:

    def test_returns_operation_result(self, session):
        result = session.sample(
            prompt_tokens=[1, 2, 3],
            sampling_params=SamplingParams(max_tokens=16, temperature=1.0, top_p=1.0, top_k=-1),
            num_samples=2,
        )
        assert isinstance(result, OperationResult)

    def test_request_contains_num_samples(self, session, transport):
        session.sample(
            prompt_tokens=[1, 2, 3],
            sampling_params=SamplingParams(max_tokens=16, temperature=1.0, top_p=1.0, top_k=-1),
            num_samples=4,
        )
        body = json.loads(transport.requests[0].body)
        assert body["num_samples"] == 4

    def test_request_contains_prompt_tokens(self, session, transport):
        session.sample(
            prompt_tokens=[10, 20, 30],
            sampling_params=SamplingParams(max_tokens=16, temperature=1.0, top_p=1.0, top_k=-1),
        )
        body = json.loads(transport.requests[0].body)
        tokens = body["prompt"]["chunks"][0]["tokens"]
        assert tokens == [10, 20, 30]

    def test_prompt_logprobs_default_false(self, session, transport):
        session.sample(
            prompt_tokens=[1, 2],
            sampling_params=SamplingParams(max_tokens=8, temperature=1.0, top_p=1.0, top_k=-1),
        )
        body = json.loads(transport.requests[0].body)
        assert body.get("promptLogprobs", False) is False

    def test_request_can_include_prompt_token_ids(self, session, monkeypatch):
        captured = {}

        def fake_post_and_poll(subpath, body, extra_params=None, extra_result_fields=None):
            captured["subpath"] = subpath
            captured["body"] = body
            captured["extra_params"] = extra_params
            captured["extra_result_fields"] = extra_result_fields
            return object()

        monkeypatch.setattr(session, "_post_and_poll", fake_post_and_poll)
        session.sample(
            prompt_tokens=[1, 2],
            sampling_params=SamplingParams(max_tokens=8, temperature=1.0, top_p=1.0, top_k=-1),
            checkpoint_id="checkpoint-1",
            prompt_token_ids=True,
        )
        assert captured["subpath"].endswith("/sample")
        assert captured["body"].prompt_token_ids is True
        body = json.loads(
            json.dumps(captured["body"], cls=SdkJSONEncoder, exclude_readonly=True)
        )
        assert body["prompt_token_ids"] is True

    def test_result_deserializes_prompt_token_ids(self):
        result = _deserialize(
            OperationResult,
            _normalize_loom_result(
                {
                    "sequences": [],
                    "prompt_token_ids": [1, 2, 3],
                },
                "sample",
                "request-1",
            ),
        )

        assert isinstance(result, SampleOperationResult)
        assert result.prompt_token_ids == [1, 2, 3]

        legacy_result = _deserialize(
            OperationResult,
            _normalize_loom_result(
                {"sequences": []},
                "sample",
                "request-2",
            ),
        )
        assert isinstance(legacy_result, SampleOperationResult)
        assert legacy_result.prompt_token_ids is None

    @pytest.mark.asyncio
    async def test_async_request_can_include_prompt_token_ids(self, monkeypatch):
        captured = {}

        async def fake_post_and_poll(client, session_id, subpath, body, extra_params=None):
            captured["client"] = client
            captured["session_id"] = session_id
            captured["subpath"] = subpath
            captured["body"] = body
            captured["extra_params"] = extra_params
            return object()

        monkeypatch.setattr(aio_patch, "_post_and_poll", fake_post_and_poll)
        client = object()
        await aio_patch.sample(
            client,
            "session_test",
            [1, 2],
            SamplingParams(max_tokens=8, temperature=1.0, top_p=1.0, top_k=-1),
            checkpoint_id="checkpoint-1",
            prompt_token_ids=True,
        )

        assert captured["client"] is client
        assert captured["session_id"] == "session_test"
        assert captured["subpath"].endswith("/sample")
        assert captured["body"].prompt_token_ids is True
        assert captured["extra_params"] == {"checkpoint_id": "checkpoint-1"}


class TestHeartbeat:

    def test_request_targets_correct_session(self, session, transport):
        # heartbeat is a synchronous POST — returns 200 with a HeartbeatResponse body
        transport._status_code = 200
        transport._response_body = b'{"session_id": "session_test"}'
        session.heartbeat()
        assert "session_test" in transport.requests[0].url


class TestClose:

    def test_returns_none(self, session):
        assert session.close() is None

    def test_request_targets_correct_session(self, session, transport):
        session.close()
        assert "session_test" in transport.requests[0].url


class TestCreateSessionRequest:

    def test_fields(self):
        req = CreateSessionRequest(
            type="training",
            base_model="Qwen/Qwen3-0.6B",
            lora_config=LoRAConfig(rank=16),
        )
        assert req.base_model == "Qwen/Qwen3-0.6B"
        assert req.lora_config.rank == 16

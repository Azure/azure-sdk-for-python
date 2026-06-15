# ---------------------------------------------------------------------------
# Unit tests for FineTuningSession (_patch.py convenience wrapper).
# ---------------------------------------------------------------------------
import json

import pytest

from azure.ai.finetuning_sessions import FineTuningSession
from azure.ai.finetuning_sessions.models import (
    AdamParams,
    LoRAConfig,
    CreateSessionRequest,
    OperationResult,
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

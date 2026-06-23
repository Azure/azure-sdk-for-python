"""
Offline smoke test for azure-ai-finetuning-sessions SDK.
Mirrors the hero code patterns from SPEC_FOUNDRY_AICLIENT.md.
Run: python test_smoke.py
No real endpoint or credentials required.
"""
import time
from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import HttpTransport, HttpResponse as _TransportHttpResponse
from azure.ai.finetuning_sessions import FineTuningSessionClient, FineTuningSession
from azure.ai.finetuning_sessions.models import (
    CreateSessionRequest,
    Datum,
    ModelInput,
    ModelInputChunk,
    LossFnInputs,
    TensorData,
    AdamParams,
    LoRAConfig,
    SamplingParams,
)


class _FakeCredential:
    def get_token(self, *scopes, **kwargs):
        return AccessToken("fake_token", int(time.time()) + 3600)

    def close(self):
        pass


class _FakeHttpResponse(_TransportHttpResponse):
    """Returns 200 OK with smart bodies: POST→pending, GET→succeeded."""

    def __init__(self, request):
        super().__init__(request, None)
        self.status_code = 200
        if getattr(request, 'method', 'POST') == "GET":
            self._body = b'{"type": "forward_backward", "operation_id": "op1", "status": "succeeded"}'
        else:
            self._body = b'{"request_id": "op1", "session_id": "session_xxx", "status": "pending"}'
        self.headers = {"content-type": "application/json"}
        self.content_type = "application/json"
        self.reason = "OK"

    def body(self):
        return self._body

    def text(self, encoding="utf-8"):
        return self._body.decode(encoding or "utf-8")

    def stream_download(self, pipeline, **kwargs):
        yield self._body

    def iter_bytes(self, **kwargs):
        yield self._body

    def iter_raw(self, **kwargs):
        yield self._body

    def read(self):
        return self._body

    def json(self):
        import json
        return json.loads(self._body)

    def close(self):
        pass

    def raise_for_status(self):
        pass


class _FakeTransport(HttpTransport):
    """Intercepts all HTTP calls and returns a fake 202 Accepted — no network needed."""

    def send(self, request, **kwargs):
        return _FakeHttpResponse(request)

    def open(self): pass
    def close(self): pass
    def __enter__(self): return self
    def __exit__(self, *args): self.close()


# ── Setup ─────────────────────────────────────────────────────────────────────
print("=== azure-ai-finetuning-sessions smoke test ===")
print("(Based on SPEC_FOUNDRY_AICLIENT.md hero code samples)\n")

client = FineTuningSessionClient(
    endpoint="https://fake",
    credential=_FakeCredential(),
    transport=_FakeTransport(),
)
session = FineTuningSession(client, session_id="session_xxx")
print(f"✓ FineTuningSession: session_id={session.session_id}")

assert hasattr(client, "sessions"),    "missing: client.sessions"
assert hasattr(client, "training"),    "missing: client.training"
assert hasattr(client, "checkpoints"), "missing: client.checkpoints"
assert hasattr(client, "sampling"),    "missing: client.sampling"
assert hasattr(client, "operations"),  "missing: client.operations"
print("✓ Sub-clients: sessions, training, checkpoints, sampling, operations")

# ── Build training data ────────────────────────────────────────────────────────
prompt_ids = [1, 2, 3, 4]
target_ids = [5, 6, 7]
all_ids = prompt_ids + target_ids
weights = [0.0] * len(prompt_ids) + [1.0] * len(target_ids)

batch = [
    Datum(
        model_input=ModelInput(chunks=[ModelInputChunk(tokens=all_ids[:-1])]),
        loss_fn_inputs=LossFnInputs(
            target_tokens=TensorData(data=[float(t) for t in all_ids[1:]]),
            weights=TensorData(data=weights[1:]),
        ),
    )
]
print(f"✓ Batch of {len(batch)} Datum built\n")

# ── Spec Scenario 1: SFT training loop ────────────────────────────────────────
fb_op = session.forward_backward(batch, loss_fn="cross_entropy")
print(f"✓ fb_op  = session.forward_backward(batch, loss_fn='cross_entropy')  → {type(fb_op).__name__}")

opt_op = session.optim_step(AdamParams(learning_rate=1e-4, beta1=0.9, beta2=0.95, eps=1e-12, weight_decay=0.0))
print(f"✓ opt_op = session.optim_step(AdamParams(learning_rate=1e-4))         → {type(opt_op).__name__}")

ckpt_op = session.save_weights("sft_piglatin_v1")
print(f"✓ ckpt_op = session.save_weights('sft_piglatin_v1')                   → {type(ckpt_op).__name__}")

# ── Spec Scenario 2: RFT sampling ─────────────────────────────────────────────
sampler_op = session.save_weights_for_sampler(seq_id=0)
print(f"✓ sampler_op = session.save_weights_for_sampler(seq_id=0)             → {type(sampler_op).__name__}")

sample_op = session.sample(
    prompt_tokens=prompt_ids,
    sampling_params=SamplingParams(max_tokens=32, temperature=1.0, top_p=1.0, top_k=-1),
    num_samples=4,
    sampling_session_id="sampling_abc123",
    seq_id=0,
    prompt_logprobs=True,
)
print(f"✓ sample_op = session.sample(prompt_tokens, params, num_samples=4)    → {type(sample_op).__name__}")

# ── Session creation body ──────────────────────────────────────────────────────
session_body = CreateSessionRequest(
    type="training",
    base_model="Qwen/Qwen3-0.6B",
    lora_config=LoRAConfig(rank=16),
)
print(f"✓ CreateSessionRequest: base_model={session_body.base_model}, lora_rank={session_body.lora_config.rank}")

print("\n=== All checks passed ✓ ===")

# ---------------------------------------------------------------------------
# Shared fixtures for azure-ai-finetuning-sessions unit tests.
# ---------------------------------------------------------------------------
import time

import pytest
from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import HttpTransport
from azure.core.pipeline.transport import HttpResponse as _TransportHttpResponse

from azure.ai.finetuning_sessions import FineTuningSessionClient, FineTuningSession
from azure.ai.finetuning_sessions.models import (
    Datum,
    ModelInput,
    ModelInputChunk,
    LossFnInputs,
    TensorData,
)


# ── Fake credential ──────────────────────────────────────────────────────────

class FakeCredential:
    def get_token(self, *scopes, **kwargs):
        return AccessToken("fake_token", int(time.time()) + 3600)

    def close(self):
        pass


# ── Fake HTTP transport ───────────────────────────────────────────────────────

class FakeHttpResponse(_TransportHttpResponse):
    """Returns 200 OK with smart request/result bodies for POST vs GET."""

    def __init__(self, request, body: bytes = None, status_code: int = 200):
        super().__init__(request, None)
        self.status_code = status_code
        if body is None:
            if getattr(request, 'method', 'POST') == "GET":
                body = b'{"type": "forward_backward", "operation_id": "req1", "status": "succeeded"}'
            else:
                body = b'{"request_id": "req1", "session_id": "session_test", "status": "pending"}'
        self.headers = {"content-type": "application/json"}
        self.content_type = "application/json"
        self.reason = "OK"
        self._body = body

    def body(self):
        return self._body

    def text(self, encoding=None):
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


class FakeTransport(HttpTransport):
    """Captures all outgoing requests and returns configurable fake responses."""

    def __init__(self, response_body: bytes = None, status_code: int = 200):
        self.requests: list = []
        self._response_body = response_body
        self._status_code = status_code

    def send(self, request, **kwargs):
        self.requests.append(request)
        return FakeHttpResponse(request, self._response_body, self._status_code)

    def open(self): pass
    def close(self): pass
    def __enter__(self): return self
    def __exit__(self, *args): self.close()


# ── Pytest fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def transport():
    return FakeTransport()


@pytest.fixture
def client(transport):
    return FineTuningSessionClient(
        endpoint="https://fake",
        credential=FakeCredential(),
        transport=transport,
    )


@pytest.fixture
def session(client):
    return FineTuningSession(client, session_id="session_test")


@pytest.fixture
def batch():
    """A minimal single-datum training batch."""
    prompt_ids = [1, 2, 3, 4]
    target_ids = [5, 6, 7]
    all_ids = prompt_ids + target_ids
    weights = [0.0] * len(prompt_ids) + [1.0] * len(target_ids)
    return [
        Datum(
            model_input=ModelInput(chunks=[ModelInputChunk(tokens=all_ids[:-1])]),
            loss_fn_inputs=LossFnInputs(
                target_tokens=TensorData(data=[float(t) for t in all_ids[1:]]),
                weights=TensorData(data=weights[1:]),
            ),
        )
    ]

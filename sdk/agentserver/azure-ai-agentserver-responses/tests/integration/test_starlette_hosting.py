"""Integration tests for Starlette host registration and wiring."""

from __future__ import annotations

from typing import Any

from starlette.applications import Starlette
from starlette.testclient import TestClient

from azure.ai.agentserver.responses._hosting import map_responses_server
from azure.ai.agentserver.responses._options import ResponsesServerOptions


class _NoopResponseHandler:
    """Minimal handler used to wire host integration tests."""

    def create_async(self, request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            if False:  # pragma: no cover - keep async generator shape.
                yield None

        return _events()


def _build_client(*, prefix: str = "", options: ResponsesServerOptions | None = None) -> TestClient:
    app = Starlette()
    map_responses_server(app, _NoopResponseHandler(), prefix=prefix, options=options)
    return TestClient(app)


def test_hosting__registers_create_get_cancel_routes_under_prefix() -> None:
    client = _build_client(prefix="/v1")

    create_response = client.post(
        "/v1/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": False,
            "store": True,
            "background": False,
        },
    )
    assert create_response.status_code == 200
    response_id = create_response.json()["id"]

    get_response = client.get(f"/v1/responses/{response_id}")
    assert get_response.status_code in {200, 404}

    cancel_response = client.post(f"/v1/responses/{response_id}/cancel")
    assert cancel_response.status_code in {200, 400, 404}


def test_hosting__options_are_applied_to_runtime_behavior() -> None:
    options = ResponsesServerOptions(
        additional_server_identity="integration-suite",
        default_model="gpt-4o-mini",
        sse_keep_alive_interval_seconds=5,
    )
    client = _build_client(options=options)

    response = client.post(
        "/responses",
        json={
            "input": "hello",
            "stream": False,
            "store": True,
            "background": False,
        },
    )

    assert response.status_code == 200
    assert "x-platform-server" in response.headers
    assert "integration-suite" in response.headers["x-platform-server"]


def test_hosting__client_disconnect_behavior_remains_contract_compliant() -> None:
    client = _build_client()

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": True,
            "store": True,
            "background": False,
        },
    ) as response:
        assert response.status_code == 200
        first_line = next(response.iter_lines(), "")
        assert first_line.startswith("event:") or first_line.startswith("data:")

    # Post-disconnect visibility and state should remain contract-compliant.
    # This call should not raise and should return a defined protocol outcome.
    follow_up = client.get("/responses/resp_disconnect_probe")
    assert follow_up.status_code in {200, 400, 404}

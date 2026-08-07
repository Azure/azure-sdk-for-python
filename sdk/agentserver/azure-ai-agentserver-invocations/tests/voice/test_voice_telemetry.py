# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Regression tests for best-effort voice telemetry."""

from starlette.testclient import TestClient

from azure.ai.agentserver.invocations.voice import VoiceAgentServerHost
from azure.ai.agentserver.invocations.voice import _host as voice_host


_TS = "2026-07-23T12:00:00.000Z"


class _FailingInstrument:
    def add(self, _value, _attributes=None) -> None:
        raise RuntimeError("counter failed")

    def record(self, _value, _attributes=None) -> None:
        raise RuntimeError("histogram failed")


def test_counter_failure_is_isolated() -> None:
    voice_host._metric_add(_FailingInstrument(), 1, {"kind": "test"})  # pylint: disable=protected-access


def test_histogram_failure_is_isolated() -> None:
    voice_host._metric_record(  # pylint: disable=protected-access
        _FailingInstrument(),
        1.0,
        {"kind": "test"},
    )


def test_telemetry_failures_do_not_change_protocol_outcome(monkeypatch) -> None:
    instrument = _FailingInstrument()
    for name in (
        "_ACTIVATION_COUNTER",
        "_CALLBACK_DURATION",
        "_FIRST_OUTPUT_DURATION",
        "_TERMINAL_COUNTER",
        "_ACTIVE_CONNECTIONS",
        "_CLOSE_CODE_COUNTER",
    ):
        monkeypatch.setattr(voice_host, name, instrument)

    app = VoiceAgentServerHost(configure_observability=None)

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.send_text("still works")

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        websocket.send_json(
            {
                "type": "session.start",
                "id": "m_start",
                "ts": _TS,
                "protocol_version": "1.0",
                "reconnect": False,
                "response_timeouts": {
                    "first_output_ms": 15_000,
                    "idle_ms": 30_000,
                    "max_duration_ms": 120_000,
                },
            }
        )
        assert websocket.receive_json()["type"] == "session.ready"
        websocket.send_json(
            {
                "type": "user.message",
                "id": "m_user",
                "ts": _TS,
                "item_id": "in_1",
                "content": [{"type": "input_text", "text": "hello"}],
            }
        )
        created = websocket.receive_json()
        output = websocket.receive_json()
        done = websocket.receive_json()

    assert created["type"] == "response.created"
    assert output["type"] == "response.output_text.done"
    assert done["type"] == "response.done"

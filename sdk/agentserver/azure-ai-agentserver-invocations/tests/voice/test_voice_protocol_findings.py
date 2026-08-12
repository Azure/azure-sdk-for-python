# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Regression tests for reviewed Voice protocol findings."""

import json
import logging

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from azure.ai.agentserver.invocations.voice import ResponseCreated, VoiceAgentServerHost
from azure.ai.agentserver.invocations.voice._codec import MAX_FRAME_BYTES, encode_outbound_message

from conftest import _records_with_ws_extras


@pytest.mark.parametrize(
    ("frame_kind", "frame", "expected_code"),
    [
        ("text", "not-json", 1002),
        ("bytes", b"binary", 1003),
        ("text", "x" * (MAX_FRAME_BYTES + 1), 1009),
    ],
)
def test_voice_sdk_close_code_matches_structured_telemetry(caplog, frame_kind, frame, expected_code):
    app = VoiceAgentServerHost(configure_observability=None)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with pytest.raises(WebSocketDisconnect) as raised:
            with TestClient(app).websocket_connect("/invocations_ws") as websocket:
                if frame_kind == "text":
                    websocket.send_text(frame)
                else:
                    websocket.send_bytes(frame)
                websocket.receive_text()

    assert raised.value.code == expected_code
    records = _records_with_ws_extras(caplog.records)
    assert records
    assert getattr(records[-1], "azure.ai.agentserver.invocations_ws.close_code") == expected_code


def test_proactive_admission_timeout_enforces_protocol_maximum():
    frame = json.loads(
        encode_outbound_message(
            ResponseCreated(
                response_id="r_boundary",
                admission_timeout_ms=60_000,
            )
        )
    )
    assert frame["admission_timeout_ms"] == 60_000

    with pytest.raises(ValueError, match="at most 60000"):
        encode_outbound_message(
            ResponseCreated(
                response_id="r_too_late",
                admission_timeout_ms=60_001,
            )
        )

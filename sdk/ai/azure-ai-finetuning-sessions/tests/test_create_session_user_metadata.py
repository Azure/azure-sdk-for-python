# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Regression tests: ``user_metadata`` JSON types survive end-to-end.

User metadata forwarded by the cookbook can include boolean values such as
``customBoolean`` / ``customFalseBoolean``. Earlier the
generated ``CreateSessionRequest.user_metadata`` was typed ``dict[str, str]``,
so constructing the request coerced ``True`` -> ``"True"`` before the body was
serialized -- silently corrupting the caller's JSON types on the wire.

These tests pin the contract at two layers:
* the generated model preserves boolean values, and
* the serialized ``create_session`` POST payload carries real JSON booleans.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

from azure.ai.finetuning_sessions.aio import _patch as _aio_mod
from azure.ai.finetuning_sessions.models._models import CreateSessionRequest


def test_model_preserves_boolean_user_metadata():
    """The generated model must not stringify boolean metadata values."""
    req = CreateSessionRequest(
        type="training",
        base_model="Qwen/Qwen3-14B",
        user_metadata={
            "customBoolean": True,
            "customFalseBoolean": False,
            "experimentName": "modelcopy",
        },
    )
    assert req.user_metadata["customBoolean"] is True
    assert req.user_metadata["customFalseBoolean"] is False
    assert req.user_metadata["experimentName"] == "modelcopy"
    # And the serialized form carries JSON booleans, not the strings "True"/"False".
    serialized = req.as_dict()["user_metadata"]
    assert serialized == {
        "customBoolean": True,
        "customFalseBoolean": False,
        "experimentName": "modelcopy",
    }


class _FakeResponse:
    def __init__(self, status_code: int, body: dict | None = None):
        self.status_code = status_code
        self._body = body or {}
        self.headers: dict[str, str] = {}

    def json(self) -> dict:
        return self._body

    def raise_for_status(self) -> None:  # pragma: no cover - not hit here
        raise AssertionError(f"unexpected raise_for_status on {self.status_code}")


class _RecordingAsyncClient:
    """Capture outbound requests and return scripted responses in order."""

    def __init__(self, responses: list[_FakeResponse]):
        self.requests: list[Any] = []
        self._responses = iter(responses)

    async def send_request(self, req):
        self.requests.append(req)
        return next(self._responses)


def test_create_session_payload_preserves_boolean_metadata(monkeypatch):
    """The serialized POST body must carry boolean metadata unchanged.

    Regression guard for the ``dict[str, str]`` coercion: drive the real async
    ``create_session`` with a fake transport, then parse the captured POST body
    and assert ``user_metadata`` contains JSON booleans (not ``"True"``).
    """
    # Avoid spawning a background heartbeat task against the fake client.
    monkeypatch.setattr(_aio_mod, "_start_heartbeat", lambda *a, **k: None)

    client = _RecordingAsyncClient(
        [
            _FakeResponse(200, {"session_id": "sess123", "request_id": "req1"}),
            _FakeResponse(200, {"status": "completed"}),
        ]
    )

    session_id = asyncio.run(
        _aio_mod.create_session(
            client,
            base_model="Qwen/Qwen3-14B",
            user_metadata={
                "customBoolean": True,
                "customFalseBoolean": False,
                "experimentName": "modelcopy",
            },
        )
    )
    assert session_id == "session_sess123"

    # First captured request is the POST /fine_tuning_sessions.
    post_req = client.requests[0]
    body = json.loads(post_req.content)
    assert body["user_metadata"] == {
        "customBoolean": True,
        "customFalseBoolean": False,
        "experimentName": "modelcopy",
    }
    # Guard against True == 1 == "1" traps: assert the JSON type is bool.
    assert isinstance(body["user_metadata"]["customBoolean"], bool)
    assert isinstance(body["user_metadata"]["customFalseBoolean"], bool)

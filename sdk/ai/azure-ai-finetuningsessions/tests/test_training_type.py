# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""The additive training-tier enum preserves the existing string wire contract."""

import inspect
import json
from typing import get_args, get_type_hints

import pytest

from azure.ai.finetuningsessions import FineTuningSession
from azure.ai.finetuningsessions.aio import FineTuningSessionClient as AsyncClient
from azure.ai.finetuningsessions.aio import _patch as aio
from azure.ai.finetuningsessions.models import CreateSessionRequest, FromCheckpoint, LoRAConfig, TrainingType
from azure.ai.finetuningsessions._utils.model_base import SdkJSONEncoder


MEMBERS = {
    "GLOBAL_STANDARD": "GlobalStandard",
    "DATAZONE_STANDARD": "DatazoneStandard",
    "DEVELOPER_TIER": "DeveloperTier",
}
VALUES = [*TrainingType, *MEMBERS.values(), "FutureTier", ""]


def wire(model):
    return json.loads(json.dumps(model, cls=SdkJSONEncoder, exclude_readonly=True))


def test_training_type_members_and_string_behavior():
    assert {name: member.value for name, member in TrainingType.__members__.items()} == MEMBERS
    assert issubclass(TrainingType, str)
    for name, value in MEMBERS.items():
        member = getattr(TrainingType, name)
        assert member == value
        assert TrainingType(value) is member
        assert json.loads(json.dumps(member)) == value


@pytest.mark.parametrize("mapping", [False, True])
@pytest.mark.parametrize("value", VALUES)
def test_model_accepts_enum_and_existing_or_future_strings(mapping, value):
    data = {"type": "training", "base_model": "test-model", "training_type": value}
    model = CreateSessionRequest(data) if mapping else CreateSessionRequest(**data)
    assert wire(model) == data
    model.training_type = "AnotherFutureTier"
    assert wire(model)["training_type"] == "AnotherFutureTier"


@pytest.mark.parametrize("explicit_none", [False, True])
@pytest.mark.parametrize("metadata", [None, {"DeveloperTier": True}, {"DeveloperTier": "true"}])
def test_omission_does_not_inject_a_training_tier(explicit_none, metadata):
    data = {"type": "training", "base_model": "test-model", "user_metadata": metadata}
    if explicit_none:
        data["training_type"] = None
    body = wire(CreateSessionRequest(**data))
    assert "training_type" not in body
    if metadata is not None:
        assert body["user_metadata"] == metadata


def test_convenience_annotations_remain_optional_and_accept_strings():
    for method in (FineTuningSession.create, AsyncClient.create_session):
        assert set(get_args(get_type_hints(method)["training_type"])) == {str, TrainingType, type(None)}
        parameter = inspect.signature(method).parameters["training_type"]
        assert parameter.default is None
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY


class Response:
    status_code = 200
    headers = {}

    def __init__(self, body):
        self.body = body

    def json(self):
        return self.body


class RecordingClient:
    def __init__(self):
        self.requests = []

    def send_request(self, request):
        self.requests.append(request)
        if request.method == "POST":
            return Response({"session_id": "session_abc12345", "request_id": "request_test"})
        return Response({"status": "completed", "result": {}})


class AsyncRecordingClient(RecordingClient):
    async def send_request(self, request):
        return super().send_request(request)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("value", [*VALUES, None])
async def test_create_and_resume_preserve_exact_tier_payload(monkeypatch, asynchronous, value):
    monkeypatch.setattr(FineTuningSession, "_start_heartbeat", lambda *_: None)
    monkeypatch.setattr(aio, "_start_heartbeat", lambda *_: None)
    client = AsyncRecordingClient() if asynchronous else RecordingClient()
    metadata = {"DeveloperTier": True, "nested": {"values": [1, None, False]}}
    checkpoint = FromCheckpoint(source_session_id="session_1234abcd", checkpoint_id="checkpoint_1")
    options = {
        "base_model": "test-model",
        "lora_config": LoRAConfig(rank=16),
        "from_checkpoint": checkpoint,
        "training_type": value,
        "user_metadata": metadata,
        "timeout_sec": 1,
    }
    if asynchronous:
        assert await aio.create_session(client, **options) == "session_abc12345"
    else:
        assert FineTuningSession.create(client, **options).session_id == "session_abc12345"
    assert len(client.requests) == 2
    post, poll = client.requests
    assert post.method == "POST"
    assert "/fine_tuning/sessions" in post.url
    expected = {
        "type": "training",
        "base_model": "test-model",
        "lora_config": {"rank": 16},
        "from_checkpoint": {"source_session_id": "session_1234abcd", "checkpoint_id": "checkpoint_1"},
        "user_metadata": metadata,
    }
    if value is not None:
        expected["training_type"] = value
    assert json.loads(post.content) == expected
    assert poll.method == "GET"
    assert "/fine_tuning/sessions/session_abc12345/request/request_test" in poll.url

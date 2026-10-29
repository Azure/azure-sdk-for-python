# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import ast
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from azure.core import MatchConditions
from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient, models
from azure.messaging.webpubsubchatservice.aio import WebPubSubChatServiceClient as AsyncClient

PACKAGE = Path(__file__).resolve().parents[1]
SAMPLES = PACKAGE / "samples"
IDENTIFIERS = {
    "role": ("room.sample",),
    "room": ("sample-room",),
    "room_member": ("sample-room", "sample-user"),
    "user": ("sample-user",),
    "topic": ("sample-room", "sample-topic"),
    "message": ("c.sample-room.sample-topic", "123456789"),
}
REQUESTS = {
    "create_or_replace_role": (
        models.ChatRoleCreateOrReplace,
        {"permissions": ["room.history", "room.publish_message"]},
    ),
    "create_or_replace_room": (models.ChatRoomCreateOrReplace, {"title": "Sample room"}),
    "create_or_replace_room_member": (models.ChatRoomMemberCreateOrReplace, {"roleName": "room.member"}),
    "create_or_replace_user": (
        models.HumanChatUserCreateOrReplace,
        {"kind": "Human", "nickname": "Sample user", "roleName": "user.member"},
    ),
    "create_or_replace_topic": (models.ChatTopicCreateOrReplace, {"title": "Sample topic"}),
    "update_topic": (models.ChatTopicUpdate, {"state": "Archived"}),
    "update_message": (models.ChatMessageUpdate, {"content": {"text": "Updated sample message"}}),
}


def _load_sample(name):
    path = SAMPLES / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def _client():
    client = Mock(spec=WebPubSubChatServiceClient)
    response = SimpleNamespace(
        id="result",
        name="room.sample",
        permissions=[],
        title="Title",
        default_conversation="conversation",
        user_id="sample-user",
        role_name="room.member",
        kind="Human",
        conversation_id="conversation",
        etag='"sample-etag"',
        state="Archived",
        room_id="sample-room",
        created_by="sample-user",
        content=None,
    )
    for operation in (*REQUESTS, "get_topic"):
        getattr(client, operation).return_value = response
    return client


@pytest.mark.parametrize("operation", REQUESTS)
def test_operation_sample_uses_matching_method_and_models(operation):
    module = _load_sample(f"sample_{operation}")
    client = _client()
    module.sample(client)
    expected_calls = ["get_topic", operation] if operation == "update_topic" else [operation]
    assert [call[0] for call in client.method_calls] == expected_calls
    method = getattr(client, operation)
    method.assert_called_once()
    args = method.call_args.args
    entity = operation.removeprefix("create_or_replace_").removeprefix("update_")
    expected_ids = IDENTIFIERS[entity]
    assert args[: len(expected_ids)] == expected_ids
    request_type, expected_json = REQUESTS[operation]
    assert isinstance(args[-1], request_type)
    assert args[-1].as_dict() == expected_json
    if operation == "update_topic":
        client.get_topic.assert_called_once_with(*expected_ids)
        assert method.call_args.kwargs == {
            "etag": '"sample-etag"',
            "match_condition": MatchConditions.IfNotModified,
        }


def test_operation_sample_coverage():
    body_operations = {
        name for name in dir(WebPubSubChatServiceClient) if name.startswith(("create_or_replace_", "update_"))
    }
    assert set(REQUESTS) == body_operations
    assert all((SAMPLES / f"sample_{operation}.py").is_file() for operation in body_operations)


@pytest.mark.parametrize("style", ["model_based", "typed_dictionary", "plain_dictionary"])
def test_request_body_styles_are_equivalent(style):
    module = _load_sample("sample_request_body_styles")
    client = _client()
    getattr(module, style)(client)
    client.create_or_replace_room_member.assert_called_once()
    room_id, user_id, body = client.create_or_replace_room_member.call_args.args
    assert (room_id, user_id) == ("sample-room", "sample-user")
    if style == "model_based":
        assert isinstance(body, models.ChatRoomMemberCreateOrReplace)
        body = body.as_dict()
    else:
        assert isinstance(body, dict)
    assert body == {"roleName": "room.member"}


def test_typed_dictionary_topic_put_example_serializes_replace_state():
    module = _load_sample("sample_request_body_styles")
    client = _client()
    module.replace_topic_with_typed_dictionary(client)
    client.create_or_replace_topic.assert_called_once()
    request = client.create_or_replace_topic.call_args.kwargs["topic"]
    assert request["state"] == models.ChatTopicState.NORMAL
    assert models.ChatTopicCreateOrReplace(request).as_dict() == request


def test_handwritten_examples_cover_all_service_operations():
    operations = {
        name
        for name in dir(WebPubSubChatServiceClient)
        if name.startswith(("create_or_replace_", "update_", "get_", "list_", "delete_"))
        and name != "get_client_access_token"
    }
    covered = set()
    for path in SAMPLES.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in operations:
                covered.add(node.func.attr)
    assert covered == operations


def test_standalone_generated_samples_are_not_delivered():
    assert not list((PACKAGE / "generated_samples").glob("*.py"))
    for path in (PACKAGE / "README.md", SAMPLES / "README.md"):
        assert "generated_samples/" not in path.read_text()


@pytest.mark.parametrize("client_type", [WebPubSubChatServiceClient, AsyncClient])
@pytest.mark.parametrize("operation", REQUESTS)
def test_retained_method_documentation_describes_resource_body(client_type, operation):
    parameter = operation.removeprefix("create_or_replace_").removeprefix("update_")
    if parameter == "room_member":
        parameter = "member"
    doc = getattr(client_type, operation).__doc__
    assert f":param {parameter}:" in doc
    assert ":param resource:" not in doc
    assert "JSON input template" not in doc


@pytest.mark.parametrize(
    "operation",
    [
        "get_role",
        "get_room",
        "get_user",
        "get_topic",
        "get_conversation",
        "list_roles",
        "list_rooms",
        "list_room_members",
        "list_users",
        "list_topics",
        "list_rooms_for_user",
        "list_messages",
    ],
)
def test_read_operation_samples(operation):
    module = _load_sample("sample_read_operations")
    client = _client()
    method = getattr(client, operation)
    method.return_value = [] if operation.startswith("list_") else client.get_topic.return_value
    getattr(module, operation)(client)
    method.assert_called_once()
    assert [call[0] for call in client.method_calls] == [operation]


@pytest.mark.parametrize("entity", ["role", "room", "room_member", "user", "topic", "message"])
def test_delete_operation_samples(entity):
    module = _load_sample("sample_delete_operations")
    client = _client()
    operation = f"delete_{entity}"
    getattr(module, operation)(client)
    getattr(client, operation).assert_called_once_with(*IDENTIFIERS[entity])
    assert [call[0] for call in client.method_calls] == [operation]

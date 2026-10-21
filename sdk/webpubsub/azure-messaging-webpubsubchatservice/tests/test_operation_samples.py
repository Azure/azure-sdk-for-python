# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import ast
import importlib.util
import os
from pathlib import Path
import runpy
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from azure.core import MatchConditions
from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient, models


PACKAGE = Path(__file__).resolve().parents[1]
SAMPLES = PACKAGE / "samples"
OPERATIONS = sorted(path.stem for path in (PACKAGE / "generated_samples").glob("*.py"))
ENVIRONMENT = {
    "WPS_CHAT_ROLE_NAME": "room.sample",
    "WPS_CHAT_ROOM_ID": "sample-room",
    "WPS_CHAT_USER_ID": "sample-user",
    "WPS_CHAT_USER_ROLE_NAME": "user.member",
    "WPS_CHAT_ROOM_ROLE_NAME": "room.member",
    "WPS_CHAT_TOPIC_ID": "sample-topic",
    "WPS_CHAT_TOPIC_ETAG": '"sample-etag"',
    "WPS_CHAT_CONVERSATION_ID": "c.sample-room.sample-topic",
    "WPS_CHAT_MESSAGE_ID": "sample-message",
}
IDENTIFIERS = {
    "role": ("room.sample",),
    "room": ("sample-room",),
    "room_member": ("sample-room", "sample-user"),
    "user": ("sample-user",),
    "topic": ("sample-room", "sample-topic"),
    "conversation": ("c.sample-room.sample-topic",),
    "message": ("c.sample-room.sample-topic", "sample-message"),
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


@pytest.fixture
def sample_imports(monkeypatch):
    monkeypatch.syspath_prepend(str(SAMPLES))


@pytest.mark.parametrize("operation", OPERATIONS)
def test_operation_sample_uses_matching_method_and_models(operation, monkeypatch, sample_imports):
    for name, value in ENVIRONMENT.items():
        monkeypatch.setenv(name, value)
    path = SAMPLES / f"sample_{operation}.py"
    spec = importlib.util.spec_from_file_location(f"operation_sample_{operation}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

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
        etag='"etag"',
        state="Archived",
        parent_room="sample-room",
        created_by="sample-user",
        content=None,
    )
    method = getattr(client, operation)
    method.return_value = [response] if operation.startswith("list_") else response
    module.sample(client)
    assert len(client.method_calls) == 1
    method.assert_called_once()
    args = method.call_args.args
    if operation == "list_rooms_for_user":
        assert args == ("sample-user",)
    elif operation == "list_room_members":
        assert args == ("sample-room",)
    elif operation in ("list_topics", "list_messages"):
        assert args == (ENVIRONMENT["WPS_CHAT_ROOM_ID" if operation == "list_topics" else "WPS_CHAT_CONVERSATION_ID"],)
    elif operation.startswith("list_"):
        assert args == ()
    else:
        entity = (
            operation.removeprefix("create_or_replace_")
            .removeprefix("get_")
            .removeprefix("delete_")
            .removeprefix("update_")
        )
        expected_ids = IDENTIFIERS[entity]
        assert args[: len(expected_ids)] == expected_ids
    if operation in REQUESTS:
        request_type, expected_json = REQUESTS[operation]
        assert isinstance(args[-1], request_type)
        assert args[-1].as_dict() == expected_json
    if operation in ("update_topic", "delete_topic"):
        assert method.call_args.kwargs == {
            "etag": '"sample-etag"',
            "match_condition": MatchConditions.IfNotModified,
        }


@pytest.mark.parametrize("operation", OPERATIONS)
def test_operation_sample_skips_without_configuration(operation, monkeypatch, sample_imports, capsys):
    for name in list(os.environ):
        if name.startswith("WPS_CHAT_"):
            monkeypatch.delenv(name)
    create = Mock(side_effect=AssertionError("Samples without configuration must not create a client"))
    monkeypatch.setattr(WebPubSubChatServiceClient, "from_connection_string", create)
    runpy.run_path(str(SAMPLES / f"sample_{operation}.py"), run_name="__main__")
    create.assert_not_called()
    assert "WPS_CHAT_CONNECTION_STRING" in capsys.readouterr().out


def test_operation_sample_coverage():
    assert len(OPERATIONS) == 25
    assert all((SAMPLES / f"sample_{operation}.py").is_file() for operation in OPERATIONS)


def test_sample_runner_validates_resource_ids(monkeypatch, sample_imports, capsys):
    from _shared import run_sample

    monkeypatch.setenv("WPS_CHAT_CONNECTION_STRING", "not-used")
    monkeypatch.delenv("WPS_CHAT_ROOM_ID", raising=False)
    create = Mock(side_effect=AssertionError("Missing identifiers must not create a client"))
    monkeypatch.setattr(WebPubSubChatServiceClient, "from_connection_string", create)
    run_sample(Mock(), ("WPS_CHAT_ROOM_ID",))
    create.assert_not_called()
    assert "WPS_CHAT_ROOM_ID" in capsys.readouterr().out


def test_sample_runner_closes_client_and_propagates_errors(monkeypatch, sample_imports):
    from _shared import run_sample

    monkeypatch.setenv("WPS_CHAT_CONNECTION_STRING", "not-a-real-connection-string")
    monkeypatch.delenv("WPS_CHAT_HUB", raising=False)
    manager = Mock()
    manager.__enter__ = Mock(return_value=Mock(spec=WebPubSubChatServiceClient))
    manager.__exit__ = Mock(return_value=False)
    create = Mock(return_value=manager)
    monkeypatch.setattr(WebPubSubChatServiceClient, "from_connection_string", create)
    callback = Mock(side_effect=ValueError("Sample error"))
    with pytest.raises(ValueError, match="Sample error"):
        run_sample(callback)
    create.assert_called_once_with("not-a-real-connection-string", "test_hub")
    callback.assert_called_once_with(manager.__enter__.return_value)
    manager.__exit__.assert_called_once()


def test_generated_topic_create_example_contains_only_title():
    tree = ast.parse((PACKAGE / "generated_samples" / "create_or_replace_topic.py").read_text())
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "create_or_replace_topic"
    ]
    assert len(calls) == 1
    body = next(keyword.value for keyword in calls[0].keywords if keyword.arg == "resource")
    assert ast.literal_eval(body) == {"title": "Product updates"}

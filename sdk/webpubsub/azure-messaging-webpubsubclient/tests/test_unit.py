# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import json
from azure.messaging.webpubsubclient.models._models import (
    JoinGroupMessage,
    LeaveGroupMessage,
    SendToGroupMessage,
    SendEventMessage,
    SequenceAckMessage,
    WebPubSubJsonReliableProtocol,
)
from testcase import WebpubsubClientPowerShellPreparer


def compare_dict(dict1, dict2):
    assert json.dumps(dict1, sort_keys=True) == json.dumps(dict2, sort_keys=True)


@pytest.mark.parametrize(
    "testname, message, expect",
    [
        (
            "JoinGroup1",
            JoinGroupMessage(group="group"),
            {
                "type": "joinGroup",
                "group": "group",
            },
        ),
        (
            "JoinGroup2",
            JoinGroupMessage(group="group", ack_id=44133),
            {
                "type": "joinGroup",
                "group": "group",
                "ackId": 44133,
            },
        ),
        (
            "LeaveGroup1",
            LeaveGroupMessage(group="group"),
            {
                "type": "leaveGroup",
                "group": "group",
            },
        ),
        (
            "LeaveGroup2",
            LeaveGroupMessage(group="group", ack_id=12345),
            {
                "type": "leaveGroup",
                "group": "group",
                "ackId": 12345,
            },
        ),
        (
            "sendToGroup1",
            SendToGroupMessage(group="group", data="xyz", data_type="text", no_echo=True),
            {
                "type": "sendToGroup",
                "group": "group",
                "dataType": "text",
                "data": "xyz",
                "noEcho": True,
            },
        ),
        (
            "sendToGroup2",
            SendToGroupMessage(group="group", data={"value": "xyz"}, data_type="json", ack_id=12345, no_echo=True),
            {
                "type": "sendToGroup",
                "group": "group",
                "dataType": "json",
                "data": {"value": "xyz"},
                "ackId": 12345,
                "noEcho": True,
            },
        ),
        (
            "sendToGroup3",
            SendToGroupMessage(
                group="group", data=memoryview("xyz".encode()), data_type="binary", ack_id=12345, no_echo=True
            ),
            {
                "type": "sendToGroup",
                "group": "group",
                "dataType": "binary",
                "data": "eHl6",
                "ackId": 12345,
                "noEcho": True,
            },
        ),
        (
            "sendToGroup4",
            SendToGroupMessage(
                group="group", data=memoryview("xyz".encode()), data_type="protobuf", ack_id=12345, no_echo=True
            ),
            {
                "type": "sendToGroup",
                "group": "group",
                "dataType": "protobuf",
                "data": "eHl6",
                "ackId": 12345,
                "noEcho": True,
            },
        ),
        (
            "sendEvent1",
            SendEventMessage(event="event", data="xyz", data_type="text"),
            {
                "type": "event",
                "event": "event",
                "dataType": "text",
                "data": "xyz",
            },
        ),
        (
            "sendEvent2",
            SendEventMessage(event="event", data={"value": "xyz"}, data_type="json", ack_id=12345),
            {
                "type": "event",
                "event": "event",
                "dataType": "json",
                "data": {"value": "xyz"},
                "ackId": 12345,
            },
        ),
        (
            "sendEvent3",
            SendEventMessage(event="event", data=memoryview("xyz".encode()), data_type="binary", ack_id=12345),
            {
                "type": "event",
                "event": "event",
                "dataType": "binary",
                "data": "eHl6",
                "ackId": 12345,
            },
        ),
        (
            "sendEvent4",
            SendEventMessage(event="event", data=memoryview("xyz".encode()), data_type="protobuf", ack_id=12345),
            {
                "type": "event",
                "event": "event",
                "dataType": "protobuf",
                "data": "eHl6",
                "ackId": 12345,
            },
        ),
        (
            "seqAck1",
            SequenceAckMessage(sequence_id=123456),
            {
                "type": "sequenceAck",
                "sequenceId": 123456,
            },
        ),
    ],
)
def test_write_message(testname, message, expect):
    print(testname)
    protocol = WebPubSubJsonReliableProtocol()
    result = protocol.write_message(message)
    compare_dict(json.loads(result), expect)


@pytest.mark.parametrize(
    "testname, message, assert_func",
    [
        (
            "ack1",
            {
                "type": "ack",
                "ackId": 123,
                "success": True,
            },
            lambda msg: msg.kind == "ack" and msg.ack_id == 123 and msg.success == True and msg.error is None,
        ),
        (
            "ack2",
            {
                "type": "ack",
                "ackId": 123,
                "success": False,
                "error": {
                    "name": "Forbidden",
                    "message": "message",
                },
            },
            lambda msg: msg.kind == "ack"
            and msg.ack_id == 123
            and msg.success == False
            and msg.error.name == "Forbidden"
            and msg.error.message == "message",
        ),
        (
            "group1",
            {
                "sequenceId": 12345,
                "type": "message",
                "from": "group",
                "group": "groupName",
                "dataType": "text",
                "data": "xyz",
                "fromUserId": "user",
            },
            lambda msg: msg.kind == "groupData"
            and msg.group == "groupName"
            and msg.sequence_id == 12345
            and msg.data_type == "text"
            and msg.data == "xyz"
            and msg.from_user_id == "user",
        ),
        (
            "group2",
            {
                "type": "message",
                "from": "group",
                "group": "groupName",
                "dataType": "json",
                "data": {"value": "xyz"},
                "fromUserId": "user",
            },
            lambda msg: msg.kind == "groupData"
            and msg.group == "groupName"
            and msg.data_type == "json"
            and msg.data == {"value": "xyz"}
            and msg.from_user_id == "user",
        ),
        (
            "group3",
            {
                "type": "message",
                "from": "group",
                "group": "groupName",
                "dataType": "binary",
                "data": "eHl6",
                "fromUserId": "user",
            },
            lambda msg: msg.kind == "groupData"
            and msg.group == "groupName"
            and msg.data_type == "binary"
            and bytes(msg.data) == "xyz".encode()
            and msg.from_user_id == "user",
        ),
        (
            "group4",
            {
                "type": "message",
                "from": "group",
                "group": "groupName",
                "dataType": "protobuf",
                "data": "eHl6",
                "fromUserId": "user",
            },
            lambda msg: msg.kind == "groupData"
            and msg.group == "groupName"
            and msg.data_type == "protobuf"
            and bytes(msg.data) == "xyz".encode()
            and msg.from_user_id == "user",
        ),
        (
            "event1",
            {
                "sequenceId": 12345,
                "type": "message",
                "from": "server",
                "dataType": "text",
                "data": "xyz",
            },
            lambda msg: msg.kind == "serverData"
            and msg.sequence_id == 12345
            and msg.data_type == "text"
            and msg.data == "xyz",
        ),
        (
            "event2",
            {
                "sequenceId": 12345,
                "type": "message",
                "from": "server",
                "dataType": "json",
                "data": {"value": "xyz"},
            },
            lambda msg: msg.kind == "serverData"
            and msg.sequence_id == 12345
            and msg.data_type == "json"
            and msg.data == {"value": "xyz"},
        ),
        (
            "event3",
            {
                "sequenceId": 12345,
                "type": "message",
                "from": "server",
                "dataType": "binary",
                "data": "eHl6",
            },
            lambda msg: msg.kind == "serverData"
            and msg.sequence_id == 12345
            and msg.data_type == "binary"
            and bytes(msg.data) == "xyz".encode(),
        ),
        (
            "event4",
            {
                "sequenceId": 12345,
                "type": "message",
                "from": "server",
                "dataType": "protobuf",
                "data": "eHl6",
            },
            lambda msg: msg.kind == "serverData"
            and msg.sequence_id == 12345
            and msg.data_type == "protobuf"
            and bytes(msg.data) == "xyz".encode(),
        ),
        (
            "system1",
            {
                "type": "system",
                "event": "connected",
                "userId": "user",
                "connectionId": "connection",
            },
            lambda msg: msg.kind == "connected"
            and msg.connection_id == "connection"
            and msg.user_id == "user"
            and msg.reconnection_token is None,
        ),
        (
            "system2",
            {
                "type": "system",
                "event": "connected",
                "userId": "user",
                "connectionId": "connection",
                "reconnectionToken": "reconnectionToken",
            },
            lambda msg: msg.kind == "connected"
            and msg.connection_id == "connection"
            and msg.user_id == "user"
            and msg.reconnection_token == "reconnectionToken",
        ),
        (
            "system3",
            {
                "type": "system",
                "event": "disconnected",
                "message": "message",
            },
            lambda msg: msg.kind == "disconnected" and msg.message == "message",
        ),
    ],
)
def test_parse_message(testname, message, assert_func):
    print(testname)
    protocol = WebPubSubJsonReliableProtocol()
    result = protocol.parse_messages(json.dumps(message))
    assert assert_func(result)

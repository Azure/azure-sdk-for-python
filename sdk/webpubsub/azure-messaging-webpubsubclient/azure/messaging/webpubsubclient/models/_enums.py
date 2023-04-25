# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class WebPubSubClientState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    STOPPED = "Stopped"
    DISCONNECTED = "Disconnected"
    CONNECTING = "Connecting"
    CONNECTED = "Connected"
    RECOVERING = "Recovering"


class UpstreamMessageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    JOIN_GROUP = "joinGroup"
    LEAVE_GROUP = "leaveGroup"
    SEND_TO_GROUP = "sendToGroup"
    SEND_EVENT = "sendEvent"
    SEQUENCE_ACK = "sequenceAck"


class WebPubSubDataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    BINARY = "binary"
    JSON = "json"
    TEXT = "text"
    PROTOBUF = "protobuf"


class CallbackType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    STOPPED = "stopped"
    SERVER_MESSAGE = "server-message"
    GROUP_MESSAGE = "group-message"
    REJOIN_GROUP_FAILED = "rejoin-group-failed"


class WebPubSubProtocolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    JSON = "json.webpubsub.azure.v1"
    JSON_RELIABLE = "json.reliable.webpubsub.azure.v1"

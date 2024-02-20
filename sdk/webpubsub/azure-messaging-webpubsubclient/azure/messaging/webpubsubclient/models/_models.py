# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import sys
import logging
from typing import Any, Mapping, overload, Union, Optional, TypeVar, Tuple, Dict
import json
import math
import threading
import base64
from azure.core.pipeline.policies import RetryMode
from .. import _model_base
from .._model_base import rest_field, AzureJSONEncoder
from ._enums import WebPubSubDataType, UpstreamMessageType

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
if sys.version_info >= (3, 8):
    from typing import Literal  # pylint: disable=no-name-in-module, ungrouped-imports
else:
    from typing_extensions import Literal  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object

_LOGGER = logging.getLogger(__name__)


class JoinGroupMessage:
    def __init__(self, group: str, ack_id: Optional[int] = None) -> None:
        self.kind: Literal["joinGroup"] = "joinGroup"
        self.group = group
        self.ack_id = ack_id


class LeaveGroupMessage:
    def __init__(self, group: str, ack_id: Optional[int] = None) -> None:
        self.kind: Literal["leaveGroup"] = "leaveGroup"
        self.group = group
        self.ack_id = ack_id


class AckMessageError:
    def __init__(self, *, name: str, message: str):
        self.name = name
        self.message = message


class AckMessage:
    def __init__(
        self,
        ack_id: int,
        success: bool,
        error: Optional[AckMessageError] = None,
    ) -> None:
        self.kind: Literal["ack"] = "ack"
        self.ack_id = ack_id
        self.success = success
        self.error = error


class SendEventMessage:
    def __init__(
        self,
        data_type: Union[WebPubSubDataType, str],
        data: Any,
        event: str,
        ack_id: Optional[int] = None,
    ) -> None:
        self.kind: Literal["sendEvent"] = "sendEvent"
        self.data_type = data_type
        self.data = data
        self.event = event
        self.ack_id = ack_id


class JoinGroupData(_model_base.Model):
    type: Literal["joinGroup"] = rest_field(default="joinGroup")
    group: str = rest_field()
    ack_id: Optional[int] = rest_field(name="ackId")

    @overload
    def __init__(
        self,
        *,
        type: Literal["joinGroup"] = "joinGroup",  # pylint: disable=redefined-builtin
        group: str,
        ack_id: Optional[int] = None,
    ) -> None:
        ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        ...

    def __init__(self, *args, **kwargs):  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class LeaveGroupData(_model_base.Model):
    type: Literal["leaveGroup"] = rest_field(default="leaveGroup")
    group: str = rest_field()
    ack_id: Optional[int] = rest_field(name="ackId")

    @overload
    def __init__(
        self,
        *,
        type: Literal["leaveGroup"] = "leaveGroup",  # pylint: disable=redefined-builtin
        group: str,
        ack_id: Optional[int] = None,
    ) -> None:
        ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        ...

    def __init__(self, *args, **kwargs):  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class SendEventData(_model_base.Model):
    type: Literal["event"] = rest_field(default="event")
    data_type: Union[WebPubSubDataType, str] = rest_field(name="dataType")
    data: Any = rest_field()
    event: str = rest_field()
    ack_id: Optional[int] = rest_field(name="ackId")

    @overload
    def __init__(
        self,
        *,
        type: Literal["event"] = "event",  # pylint: disable=redefined-builtin
        data_type: Union[WebPubSubDataType, str],
        data: Any,
        event: str,
        ack_id: Optional[int] = None,
    ) -> None:
        ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        ...

    def __init__(self, *args, **kwargs):  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class SendToGroupData(_model_base.Model):
    type: Literal["sendToGroup"] = rest_field(default="sendToGroup")
    group: str = rest_field()
    data_type: Union[WebPubSubDataType, str] = rest_field(name="dataType")
    data: Any = rest_field()
    no_echo: bool = rest_field(name="noEcho")
    ack_id: Optional[int] = rest_field(name="ackId")

    @overload
    def __init__(
        self,
        *,
        type: Literal["sendToGroup"] = "sendToGroup",  # pylint: disable=redefined-builtin
        group: str,
        data_type: Union[WebPubSubDataType, str],
        data: Any,
        no_echo: bool,
        ack_id: Optional[int] = None,
    ) -> None:
        ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        ...

    def __init__(self, *args, **kwargs):  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class SequenceAckData(_model_base.Model):
    type: Literal["sequenceAck"] = rest_field(default="sequenceAck")
    sequence_id: int = rest_field(name="sequenceId")

    @overload
    def __init__(
        self,
        *,
        type: Literal["sequenceAck"] = "sequenceAck",  # pylint: disable=redefined-builtin
        sequence_id: int,
    ) -> None:
        ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        ...

    def __init__(self, *args, **kwargs):  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class SequenceAckMessage:
    def __init__(
        self,
        sequence_id: int,
    ) -> None:
        self.kind: Literal["sequenceAck"] = "sequenceAck"
        self.sequence_id = sequence_id


class ConnectedMessage:
    def __init__(
        self, connection_id: str, user_id: Optional[str] = None, reconnection_token: Optional[str] = None
    ) -> None:
        self.kind: Literal["connected"] = "connected"
        self.connection_id = connection_id
        self.user_id = user_id
        self.reconnection_token = reconnection_token


class DisconnectedMessage:
    def __init__(self, message: Optional[str] = None) -> None:
        self.kind: Literal["disconnected"] = "disconnected"
        self.message = message


class GroupDataMessage:
    def __init__(
        self,
        *,
        data_type: Union[WebPubSubDataType, str],
        data: Any,
        group: str,
        from_user_id: Optional[str] = None,
        sequence_id: Optional[int] = None,
    ) -> None:
        self.kind: Literal["groupData"] = "groupData"
        self.data_type = data_type
        self.data = data
        self.group = group
        self.from_user_id = from_user_id
        self.sequence_id = sequence_id


class ServerDataMessage:
    def __init__(self, data_type: Union[WebPubSubDataType, str], data: Any, sequence_id: Optional[int] = None) -> None:
        self.kind: Literal["serverData"] = "serverData"
        self.data_type = data_type
        self.data = data
        self.sequence_id = sequence_id


class SendToGroupMessage:
    def __init__(
        self,
        data_type: Union[WebPubSubDataType, str],
        data: Any,
        group: str,
        no_echo: bool,
        ack_id: Optional[int] = None,
    ) -> None:
        self.kind: Literal["sendToGroup"] = "sendToGroup"
        self.data_type = data_type
        self.data = data
        self.group = group
        self.no_echo = no_echo
        self.ack_id = ack_id


WebPubSubMessage = TypeVar(
    "WebPubSubMessage",
    GroupDataMessage,
    ServerDataMessage,
    JoinGroupMessage,
    LeaveGroupMessage,
    ConnectedMessage,
    DisconnectedMessage,
    SendToGroupMessage,
    SendEventMessage,
    SequenceAckMessage,
    AckMessage,
)


def get_pay_load(data: Any, data_type: Union[WebPubSubDataType, str]) -> Any:
    if data_type == WebPubSubDataType.TEXT:
        if not isinstance(data, str):
            raise TypeError("Message must be a string.")
        return data
    if data_type == WebPubSubDataType.JSON:
        return data
    if data_type in (WebPubSubDataType.BINARY, WebPubSubDataType.PROTOBUF):
        if isinstance(data, memoryview):
            return base64.b64encode(bytes(data)).decode()
        raise Exception("data must be memoryview when dataType is binary or protobuf")
    raise TypeError(f"Unsupported dataType: {data_type}")


def parse_payload(data: Any, data_type: Union[WebPubSubDataType, str]) -> Any:
    if data_type == WebPubSubDataType.TEXT:
        if not isinstance(data, str):
            raise TypeError("Message must be a string when dataType is text")
        return data
    if data_type == WebPubSubDataType.JSON:
        return data
    if data_type in (WebPubSubDataType.BINARY, WebPubSubDataType.PROTOBUF):
        if not isinstance(data, (bytes, bytearray)):
            data = bytes(base64.b64decode(data))
        return memoryview(data)

    # Forward compatible
    return None


class WebPubSubClientProtocol:
    def __init__(self) -> None:
        self.is_reliable_sub_protocol = False
        self.name = ""

    # pylint: disable=too-many-return-statements
    @staticmethod
    def parse_messages(
        raw_message: str,
    ) -> Union[ConnectedMessage, DisconnectedMessage, GroupDataMessage, ServerDataMessage, AckMessage, None]:
        if raw_message is None:
            raise Exception("No input")
        if not isinstance(raw_message, str):
            raise Exception("Invalid input for JSON hub protocol. Expected a string.")

        message = json.loads(raw_message)
        if message["type"] == "system":
            if message["event"] == "connected":
                return ConnectedMessage(
                    connection_id=message["connectionId"],
                    user_id=message.get("userId"),
                    reconnection_token=message.get("reconnectionToken"),
                )
            if message["event"] == "disconnected":
                return DisconnectedMessage(message=message.get("message"))
            _LOGGER.error("wrong message event type: %s", message["event"])
            return None
        if message["type"] == "message":
            if message["from"] == "group":
                data = parse_payload(message["data"], message["dataType"])
                return GroupDataMessage(
                    data_type=message["dataType"],
                    data=data,
                    group=message["group"],
                    from_user_id=message.get("fromUserId"),
                    sequence_id=message.get("sequenceId"),
                )
            if message["from"] == "server":
                data = parse_payload(message["data"], message["dataType"])
                return ServerDataMessage(
                    data=data, data_type=message["dataType"], sequence_id=message.get("sequenceId")
                )
            _LOGGER.error("wrong message from type: %s", message["from"])
            return None
        if message["type"] == "ack":
            error = message.get("error")
            return AckMessage(
                ack_id=message["ackId"],
                success=message["success"],
                error=AckMessageError(name=error["name"], message=error["message"])
                if isinstance(error, dict)
                else None,
            )
        _LOGGER.error("wrong message type: %s", message["type"])
        return None

    @staticmethod
    def write_message(message: WebPubSubMessage) -> str:
        if message.kind == UpstreamMessageType.JOIN_GROUP:
            data = JoinGroupData(group=message.group, ack_id=message.ack_id)
        elif message.kind == UpstreamMessageType.LEAVE_GROUP:
            data = LeaveGroupData(group=message.group, ack_id=message.ack_id)
        elif message.kind == UpstreamMessageType.SEND_EVENT:
            data = SendEventData(
                event=message.event,
                ack_id=message.ack_id,
                data_type=message.data_type,
                data=get_pay_load(message.data, message.data_type),
            )
        elif message.kind == UpstreamMessageType.SEND_TO_GROUP:
            data = SendToGroupData(
                group=message.group,
                ack_id=message.ack_id,
                data_type=message.data_type,
                data=get_pay_load(message.data, message.data_type),
                no_echo=message.no_echo,
            )
        elif message.kind == UpstreamMessageType.SEQUENCE_ACK:
            data = SequenceAckData(sequence_id=message.sequence_id)
        else:
            raise Exception(f"Unsupported type: {message.kind}")

        for k in list(data.keys()):
            if data[k] is None:
                data.pop(k)

        return json.dumps(data, cls=AzureJSONEncoder)


class WebPubSubJsonProtocol(WebPubSubClientProtocol):
    def __init__(self) -> None:
        super().__init__()
        self.is_reliable_sub_protocol = False
        self.name = "json.webpubsub.azure.v1"


class WebPubSubJsonReliableProtocol(WebPubSubClientProtocol):
    def __init__(self) -> None:
        super().__init__()
        self.is_reliable_sub_protocol = True
        self.name = "json.reliable.webpubsub.azure.v1"


class SendMessageErrorOptions:
    def __init__(self, ack_id: Optional[int] = None, error_detail: Optional[AckMessageError] = None) -> None:
        self.ack_id = ack_id
        self.error_detail = error_detail
        self.cv = threading.Condition()


class SendMessageError(Exception):
    def __init__(
        self, message: str, ack_id: Optional[int] = None, error_detail: Optional[AckMessageError] = None
    ) -> None:
        super().__init__(message)
        self.name = "SendMessageError"
        self.ack_id = ack_id
        self.error_detail = error_detail


class OnGroupDataMessageArgs:
    def __init__(
        self,
        *,
        data_type: Union[WebPubSubDataType, str],
        data: Any,
        group: str,
        from_user_id: Optional[str] = None,
        sequence_id: Optional[int] = None,
    ) -> None:
        self.data_type = data_type
        self.data = data
        self.group = group
        self.from_user_id = from_user_id
        self.sequence_id = sequence_id


class OnServerDataMessageArgs:
    def __init__(self, data_type: Union[WebPubSubDataType, str], data: Any, sequence_id: Optional[int] = None) -> None:
        self.data_type = data_type
        self.data = data
        self.sequence_id = sequence_id


class OnDisconnectedArgs:
    def __init__(self, connection_id: Optional[str] = None, message: Optional[str] = None) -> None:
        self.connection_id = connection_id
        self.message = message


class OnRejoinGroupFailedArgs:
    def __init__(self, group: str, error: Exception) -> None:
        self.group = group
        self.error = error


class OnConnectedArgs:
    def __init__(self, connection_id: str, user_id: Optional[str] = None) -> None:
        self.connection_id = connection_id
        self.user_id = user_id


class CloseEvent:
    def __init__(self, close_status_code: Optional[int] = None, close_reason: Optional[str] = None) -> None:
        self.close_status_code = close_status_code
        self.close_reason = close_reason


class RetryPolicy:
    def __init__(
        self,
        retry_total: int,
        retry_backoff_factor: float,
        retry_backoff_max: float,
        mode: RetryMode,
    ) -> None:
        self.retry_total = retry_total
        self.retry_backoff_factor = retry_backoff_factor
        self.retry_backoff_max = retry_backoff_max
        self.mode = mode
        self.max_retries_to_get_max_delay = math.ceil(
            math.log2(self.retry_backoff_max) - math.log2(self.retry_backoff_factor) + 1
        )

    def next_retry_delay(self, retry_attempt: int) -> Union[float, None]:
        if retry_attempt > self.retry_total:
            return None
        if self.mode == RetryMode.Fixed:
            return self.retry_backoff_factor
        return self.calculate_exponential_delay(retry_attempt)

    def calculate_exponential_delay(self, attempt: int) -> float:
        if attempt >= self.max_retries_to_get_max_delay:
            return self.retry_backoff_max
        return (1 << (attempt - 1)) * self.retry_backoff_factor


class WebPubSubGroup:
    def __init__(self, name: str) -> None:
        self.name = name
        self.is_joined = False


class SequenceId:
    def __init__(self) -> None:
        self.sequence_id = 0
        self.is_update = False

    def try_update(self, sequence_id: int) -> bool:
        self.is_update = True
        if sequence_id > self.sequence_id:
            self.sequence_id = sequence_id
            return True
        return False

    def try_get_sequence_id(self) -> Tuple[bool, Union[int, None]]:
        if self.is_update:
            self.is_update = False
            return (True, self.sequence_id)
        return (False, None)

    def reset(self):
        self.sequence_id = 0
        self.is_update = False


class AckMap:
    def __init__(self) -> None:
        self.ack_map: Dict[int, SendMessageErrorOptions] = {}
        self.lock = threading.Lock()

    def add(self, ack_id: int, options: SendMessageErrorOptions) -> None:
        with self.lock:
            self.ack_map[ack_id] = options

    def pop(self, ack_id: int) -> None:
        with self.lock:
            self.ack_map.pop(ack_id, None)

    def get(self, ack_id: int) -> Optional[SendMessageErrorOptions]:
        with self.lock:
            return self.ack_map.get(ack_id)

    def clear(self) -> None:
        with self.lock:
            for key in list(self.ack_map.keys()):
                _LOGGER.debug("clear ack map with ack id: %s", key)
                with self.ack_map[key].cv:
                    self.ack_map[key].cv.notify()
            self.ack_map.clear()


class StartStoppingClientError(Exception):
    """Exception raised when the client is stopping but users want to start it again"""


class StartNotStoppedClientError(Exception):
    """Exception raised when the client is not stopped completely"""


class StartClientError(Exception):
    """Exception raised when fail to start the client"""


class OpenWebSocketError(Exception):
    """Exception raised when fail to open the websocket"""


class DisconnectedError(Exception):
    """Exception raised when the client is not connected to the service."""

# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines
import sys
import asyncio
import logging
from typing import Any, Mapping, overload, Union, Optional, TypeVar, Tuple, Dict, Literal
import json
import math
import threading
import base64
from azure.core.pipeline.policies import RetryMode
from azure.core.exceptions import AzureError
from .. import _model_base
from .._model_base import rest_field, AzureJSONEncoder
from ._enums import WebPubSubDataType, UpstreamMessageType

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object

_LOGGER = logging.getLogger(__name__)


class JoinGroupMessage:
    """Message to join a group

    :ivar group: The group name to join. Required.
    :vartype group: str
    :ivar ack_id: The ack id of the message.
    :vartype ack_id: int
    """

    def __init__(self, group: str, ack_id: Optional[int] = None) -> None:
        self.kind: Literal["joinGroup"] = "joinGroup"
        self.group = group
        self.ack_id = ack_id


class LeaveGroupMessage:
    """Message to leave a group

    :ivar group: The group name to leave. Required.
    :vartype group: str
    :ivar ack_id: The ack id of the message.
    :vartype ack_id: int
    """

    def __init__(self, group: str, ack_id: Optional[int] = None) -> None:
        self.kind: Literal["leaveGroup"] = "leaveGroup"
        self.group = group
        self.ack_id = ack_id


class AckMessageError:
    """Error details of an ack message
    :ivar name: The error name. Required.
    :vartype name: str
    :ivar message: The error message. Required.
    :vartype message: str
    """

    def __init__(self, *, name: str, message: str):
        self.name = name
        self.message = message


class AckMessage:
    """Ack message

    :ivar ack_id: The ack id of the message. Required.
    :vartype ack_id: int
    :ivar success: Whether the message is successfully processed. Required.
    :vartype success: bool
    :ivar error: The error details of the message.
    :vartype error: ~azure.messaging.webpubsubclient.models.AckMessageError
    """

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
    """Message to send an event

    :ivar data_type: The data type of the message. Required.
    :vartype data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType or str
    :ivar data: The data of the message. Required.
    :vartype data: Any
    :ivar event: The event name. Required.
    :vartype event: str
    :ivar ack_id: The ack id of the message.
    :vartype ack_id: int
    """

    def __init__(
        self,
        data_type: WebPubSubDataType,
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
    """Data to join a group

    :ivar type: The type of the message. Required. Default value is "joinGroup".
    :vartype type: str
    :ivar group: The group name to join. Required.
    :vartype group: str
    :ivar ack_id: The ack id of the message.
    :vartype ack_id: int
    """

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
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]): ...

    def __init__(self, *args, **kwargs):  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class LeaveGroupData(_model_base.Model):
    """Data to leave a group

    :ivar type: The type of the message. Required. Default value is "leaveGroup".
    :vartype type: str
    :ivar group: The group name to join. Required.
    :vartype group: str
    :ivar ack_id: The ack id of the message.
    :vartype ack_id: int
    """

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
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]): ...

    def __init__(self, *args, **kwargs):  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class SendEventData(_model_base.Model):
    """Data to send an event

    :ivar type: The type of the message. Required. Default value is "event".
    :vartype type: str
    :ivar data_type: The data type of the message. Required.
    :vartype data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType or str
    :ivar data: The data of the message. Required.
    :vartype data: Any
    :ivar event: The event name. Required.
    :vartype event: str
    :ivar ack_id: The ack id of the message.
    :vartype ack_id: int
    """

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
        data_type: WebPubSubDataType,
        data: Any,
        event: str,
        ack_id: Optional[int] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]): ...

    def __init__(self, *args, **kwargs):  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class SendToGroupData(_model_base.Model):
    """Data for send to group

    :ivar type: The type of the message. Required. Default value is "sendToGroup".
    :vartype type: str
    :ivar group: The group name to send. Required.
    :vartype group: str
    :ivar data_type: The data type of the message. Required.
    :vartype data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType or str
    :ivar data: The data of the message. Required.
    :vartype data: Any
    :ivar no_echo: Whether to send message to the sender. Required.
    :vartype no_echo: bool
    :ivar ack_id: The ack id of the message.
    :vartype ack_id: int
    """

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
        data_type: WebPubSubDataType,
        data: Any,
        no_echo: bool,
        ack_id: Optional[int] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]): ...

    def __init__(self, *args, **kwargs):  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class SequenceAckData(_model_base.Model):
    """Data for sequence ack

    :ivar type: The type of the message. Required. Default value is "sequenceAck".
    :vartype type: str
    :ivar sequence_id: The sequence id. Required.
    :vartype sequence_id: int
    """

    type: Literal["sequenceAck"] = rest_field(default="sequenceAck")
    sequence_id: int = rest_field(name="sequenceId")

    @overload
    def __init__(
        self,
        *,
        type: Literal["sequenceAck"] = "sequenceAck",  # pylint: disable=redefined-builtin
        sequence_id: int,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]): ...

    def __init__(self, *args, **kwargs):  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class SequenceAckMessage:
    """Message for sequence ack

    :ivar sequence_id: The sequence id. Required.
    :vartype sequence_id: int
    """

    def __init__(
        self,
        sequence_id: int,
    ) -> None:
        self.kind: Literal["sequenceAck"] = "sequenceAck"
        self.sequence_id = sequence_id


class ConnectedMessage:
    """Message for connected event

    :ivar connection_id: The connection id. Required.
    :vartype connection_id: str
    :ivar user_id: The user id.
    :vartype user_id: str
    :ivar reconnection_token: The reconnection token.
    :vartype reconnection_token: str
    """

    def __init__(
        self,
        connection_id: str,
        user_id: Optional[str] = None,
        reconnection_token: Optional[str] = None,
    ) -> None:
        self.kind: Literal["connected"] = "connected"
        self.connection_id = connection_id
        self.user_id = user_id
        self.reconnection_token = reconnection_token


class DisconnectedMessage:
    """Message for disconnected event

    :ivar message: The message. Optional.
    :vartype message: str
    """

    def __init__(self, message: Optional[str] = None) -> None:
        self.kind: Literal["disconnected"] = "disconnected"
        self.message = message


class GroupDataMessage:
    """Message for group data

    :ivar data_type: The data type of the message. Required.
    :vartype data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType or str
    :ivar data: The data of the message. Required.
    :vartype data: Any
    :ivar group: The group name. Required.
    :vartype group: str
    :ivar from_user_id: The user id of the sender.
    :vartype from_user_id: str
    :ivar sequence_id: The sequence id.
    :vartype sequence_id: int
    """

    def __init__(
        self,
        *,
        data_type: WebPubSubDataType,
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
    """Message for server data

    :ivar data_type: The data type of the message. Required.
    :vartype data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType or str
    :ivar data: The data of the message. Required.
    :vartype data: Any
    :ivar sequence_id: The sequence id.
    :vartype sequence_id: int
    """

    def __init__(
        self,
        data_type: WebPubSubDataType,
        data: Any,
        sequence_id: Optional[int] = None,
    ) -> None:
        self.kind: Literal["serverData"] = "serverData"
        self.data_type = data_type
        self.data = data
        self.sequence_id = sequence_id


class SendToGroupMessage:
    """Message for send to group

    :ivar data_type: The data type of the message. Required.
    :vartype data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType or str
    :ivar data: The data of the message. Required.
    :vartype data: Any
    :ivar group: The group name. Required.
    :vartype group: str
    :ivar no_echo: Whether to send message to the sender. Required.
    :vartype no_echo: bool
    :ivar ack_id: The ack id of the message.
    :vartype ack_id: int
    """

    def __init__(
        self,
        data_type: WebPubSubDataType,
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

SendMessageType = TypeVar(
    "SendMessageType",
    SendToGroupMessage,
    SendEventMessage,
    JoinGroupMessage,
    LeaveGroupMessage,
)


def get_pay_load(data: Any, data_type: Union[WebPubSubDataType, str]) -> Any:
    """Get payload from data with data_type

    :param data: The data of pay load. Required.
    :type data: Any
    :param data_type: The data type of the data. Required.
    :type data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType or str
    :return: The payload.
    :rtype: Any
    :raises TypeError: If data_type is not supported.
    """

    if data_type == WebPubSubDataType.TEXT:
        if not isinstance(data, str):
            raise TypeError("Message must be a string.")
        return data
    if data_type == WebPubSubDataType.JSON:
        return data
    if data_type in (WebPubSubDataType.BINARY, WebPubSubDataType.PROTOBUF):
        if isinstance(data, memoryview):
            return base64.b64encode(bytes(data)).decode()
        raise TypeError("data must be memoryview when dataType is binary or protobuf")
    raise TypeError(f"Unsupported dataType: {data_type}")


def parse_payload(data: Any, data_type: Union[WebPubSubDataType, str]) -> Any:
    """Parse payload from data with data_type

    :param data: The data of pay load. Required.
    :type data: Any
    :param data_type: The data type of the data. Required.
    :type data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType or str
    :return: The payload.
    :rtype: Any
    """

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
    """WebPubSub client protocol"""

    def __init__(self) -> None:
        self.is_reliable_sub_protocol = False
        self.name = ""

    # pylint: disable=too-many-return-statements
    @staticmethod
    def parse_messages(
        raw_message: str,
    ) -> Union[
        ConnectedMessage,
        DisconnectedMessage,
        GroupDataMessage,
        ServerDataMessage,
        AckMessage,
        None,
    ]:
        """Parse messages from raw message

        :param raw_message: The raw message. Required.
        :type raw_message: str
        :return: The parsed message.
        :rtype: Union[ConnectedMessage, DisconnectedMessage, GroupDataMessage, ServerDataMessage, AckMessage, None]
        :raises ValueError: If raw_message is None or raw_message type is not string.
        """
        if raw_message is None:
            raise ValueError("No input")
        if not isinstance(raw_message, str):
            raise ValueError("Invalid input for JSON hub protocol. Expected a string.")

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
                    data=data,
                    data_type=message["dataType"],
                    sequence_id=message.get("sequenceId"),
                )
            _LOGGER.error("wrong message from type: %s", message["from"])
            return None
        if message["type"] == "ack":
            error = message.get("error")
            return AckMessage(
                ack_id=message["ackId"],
                success=message["success"],
                error=(
                    AckMessageError(name=error["name"], message=error["message"]) if isinstance(error, dict) else None
                ),
            )
        _LOGGER.error("wrong message type: %s", message["type"])
        return None

    @staticmethod
    def write_message(message: WebPubSubMessage) -> str:
        """Convert write message to string

        :param message: The message to write. Required.
        :type message: WebPubSubMessage
        :return: The converted message.
        :rtype: str
        :raises TypeError: If message is None.
        """
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
            raise TypeError(f"Unsupported type: {message.kind}")

        for k in list(data.keys()):
            if data[k] is None:
                data.pop(k)

        return json.dumps(data, cls=AzureJSONEncoder)


class WebPubSubJsonProtocol(WebPubSubClientProtocol):
    """WebPubSub json protocol"""

    def __init__(self) -> None:
        super().__init__()
        self.is_reliable_sub_protocol = False
        self.name = "json.webpubsub.azure.v1"


class WebPubSubJsonReliableProtocol(WebPubSubClientProtocol):
    """WebPubSub json reliable protocol"""

    def __init__(self) -> None:
        super().__init__()
        self.is_reliable_sub_protocol = True
        self.name = "json.reliable.webpubsub.azure.v1"


class _SendMessageErrorOptions:
    """Options for send message error
    :ivar ack_id: The ack id of the message.
    :vartype ack_id: int
    :ivar error_detail: The error details of the message.
    :vartype error_detail: ~azure.messaging.webpubsubclient.models.AckMessageError
    """

    def __init__(
        self,
        ack_id: Optional[int] = None,
        error_detail: Optional[AckMessageError] = None,
    ) -> None:
        self.ack_id = ack_id
        self.error_detail = error_detail


class SendMessageErrorOptions(_SendMessageErrorOptions):
    """Options for send message error
    :ivar ack_id: The ack id of the message.
    :vartype ack_id: int
    :ivar error_detail: The error details of the message.
    :vartype error_detail: ~azure.messaging.webpubsubclient.models.AckMessageError
    """

    def __init__(
        self,
        ack_id: Optional[int] = None,
        error_detail: Optional[AckMessageError] = None,
    ) -> None:
        super().__init__(ack_id, error_detail)
        self.cv = threading.Condition()


class SendMessageErrorOptionsAsync(_SendMessageErrorOptions):
    """Async Options for send message error
    :ivar ack_id: The ack id of the message.
    :vartype ack_id: int
    :ivar error_detail: The error details of the message.
    :vartype error_detail: ~azure.messaging.webpubsubclient.models.AckMessageError
    """

    def __init__(
        self,
        ack_id: Optional[int] = None,
        error_detail: Optional[AckMessageError] = None,
    ) -> None:
        super().__init__(ack_id, error_detail)
        self.event = asyncio.Event()


class SendMessageError(AzureError):
    """Exception raised when fail to send message

    :ivar message: The error message. Required.
    :vartype message: str
    :ivar ack_id: The ack id of the message.
    :vartype ack_id: int
    :ivar error_detail: The error details of the message.
    :vartype error_detail: ~azure.messaging.webpubsubclient.models.AckMessageError
    """

    def __init__(
        self,
        message: str,
        ack_id: Optional[int] = None,
        error_detail: Optional[AckMessageError] = None,
    ) -> None:
        super().__init__(message)
        self.name = "SendMessageError"
        self.ack_id = ack_id
        self.error_detail = error_detail


class OnGroupDataMessageArgs:
    """Arguments for group data message

    :ivar data_type: The data type of the message. Required.
    :vartype data_type: WebPubSubDataType or str
    :ivar data: The data of the message. Required.
    :vartype data: Any
    :ivar group: The group name. Required.
    :vartype group: str
    :ivar from_user_id: The user id of the sender.
    :vartype from_user_id: str
    :ivar sequence_id: The sequence id.
    :vartype sequence_id: int
    """

    def __init__(
        self,
        *,
        data_type: WebPubSubDataType,
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
    """Arguments for server data message

    :ivar data_type: The data type of the message. Required.
    :vartype data_type: WebPubSubDataType or str
    :ivar data: The data of the message. Required.
    :vartype data: Any
    :ivar sequence_id: The sequence id.
    :vartype sequence_id: int
    """

    def __init__(
        self,
        data_type: WebPubSubDataType,
        data: Any,
        sequence_id: Optional[int] = None,
    ) -> None:
        self.data_type = data_type
        self.data = data
        self.sequence_id = sequence_id


class OnDisconnectedArgs:
    """Arguments for disconnected message

    :ivar connection_id: The connection id.
    :vartype connection_id: str
    :ivar message: The message.
    :vartype message: str
    """

    def __init__(self, connection_id: Optional[str] = None, message: Optional[str] = None) -> None:
        self.connection_id = connection_id
        self.message = message


class OnRejoinGroupFailedArgs:
    """Arguments for rejoin group failed message
    :ivar group: The group name.
    :vartype group: str
    :ivar error: The error.
    :vartype error: Exception
    """

    def __init__(self, group: str, error: Exception) -> None:
        self.group = group
        self.error = error


class OnConnectedArgs:
    """Arguments for connected message

    :ivar connection_id: The connection id.
    :vartype connection_id: str
    :ivar user_id: The user id.
    :vartype user_id: str
    """

    def __init__(self, connection_id: str, user_id: Optional[str] = None) -> None:
        self.connection_id = connection_id
        self.user_id = user_id


class CloseEvent:
    """Close event

    :ivar close_status_code: The close status code.
    :vartype close_status_code: int
    :ivar close_reason: The close reason.
    :vartype close_reason: str
    """

    def __init__(
        self,
        close_status_code: Optional[int] = None,
        close_reason: Optional[str] = None,
    ) -> None:
        self.close_status_code = close_status_code
        self.close_reason = close_reason


class RetryPolicy:
    """Retry policy

    :ivar retry_total: The total number of retries. Required.
    :vartype retry_total: int
    :ivar retry_backoff_factor: The backoff factor. Required.
    :vartype retry_backoff_factor: float
    :ivar retry_backoff_max: The max backoff. Required.
    :vartype retry_backoff_max: float
    :ivar mode: The retry mode. Required.
    :vartype mode: ~azure.core.pipeline.policies.RetryMode
    """

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
        """Get next retry delay
        :param retry_attempt: The number that client has already retried. Required.
        :type retry_attempt: int
        :return: The next retry delay.
        :rtype: float or None
        """
        if retry_attempt > self.retry_total:
            return None
        if self.mode == RetryMode.Fixed:
            return self.retry_backoff_factor
        return self.calculate_exponential_delay(retry_attempt)

    def calculate_exponential_delay(self, attempt: int) -> float:
        """Calculate exponential delay
        :param attempt: The number to retry. Required.
        :type attempt: int
        :return: The exponential delay.
        :rtype: float
        """
        if attempt >= self.max_retries_to_get_max_delay:
            return self.retry_backoff_max
        return (1 << (attempt - 1)) * self.retry_backoff_factor


class WebPubSubGroup:
    """WebPubSub group
    :ivar name: The group name. Required.
    :vartype name: str
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.is_joined = False


class SequenceId:
    """Sequence id"""

    def __init__(self) -> None:
        self.sequence_id = 0
        self.is_update = False

    def try_update(self, sequence_id: int) -> bool:
        """Try to update sequence id

        :param sequence_id: The sequence id. Required.
        :type sequence_id: int
        :return: Whether sequence id is updated.
        :rtype: bool
        """
        self.is_update = True
        if sequence_id > self.sequence_id:
            self.sequence_id = sequence_id
            return True
        return False

    def try_get_sequence_id(self) -> Tuple[bool, Union[int, None]]:
        """Try to get sequence id
        :return: Whether sequence id is updated and sequence id.
        :rtype: Tuple[bool, Union[int, None]]
        """
        if self.is_update:
            self.is_update = False
            return (True, self.sequence_id)
        return (False, None)

    def reset(self):
        """Reset sequence id"""
        self.sequence_id = 0
        self.is_update = False


class AckMap:
    """Ack map"""

    def __init__(self) -> None:
        self.ack_map: Dict[int, SendMessageErrorOptions] = {}
        self.lock = threading.Lock()

    def add(self, ack_id: int, options: SendMessageErrorOptions) -> None:
        """Add ack id to ack map

        :param ack_id: The ack id. Required.
        :type ack_id: int
        :param options: The options. Required.
        :type options: SendMessageErrorOptions
        """
        with self.lock:
            self.ack_map[ack_id] = options

    def pop(self, ack_id: int) -> Optional[SendMessageErrorOptions]:
        """Pop ack id from ack map

        :param ack_id: The ack id. Required.
        :type ack_id: int
        :return: The options.
        :rtype: SendMessageErrorOptions or None
        """
        with self.lock:
            return self.ack_map.pop(ack_id, None)

    def get(self, ack_id: int) -> Optional[SendMessageErrorOptions]:
        """Get ack id from ack map

        :param ack_id: The ack id. Required.
        :type ack_id: int
        :return: The options.
        :rtype: SendMessageErrorOptions or None
        """
        with self.lock:
            return self.ack_map.get(ack_id)

    def clear(self) -> None:
        """Clear ack map"""
        with self.lock:
            for key in list(self.ack_map.keys()):
                _LOGGER.debug("clear ack map with ack id: %s", key)
                with self.ack_map[key].cv:
                    self.ack_map[key].cv.notify()
            self.ack_map.clear()


class AckMapAsync:
    """Async Ack map"""

    def __init__(self) -> None:
        self.ack_map: Dict[int, SendMessageErrorOptionsAsync] = {}

    def add(self, ack_id: int, options: SendMessageErrorOptionsAsync) -> None:
        """Add ack id to ack map

        :param ack_id: The ack id. Required.
        :type ack_id: int
        :param options: The options. Required.
        :type options: SendMessageErrorOptions
        """
        self.ack_map[ack_id] = options

    def pop(self, ack_id: int) -> Optional[SendMessageErrorOptionsAsync]:
        """Pop ack id from ack map

        :param ack_id: The ack id. Required.
        :type ack_id: int
        :return: The options.
        :rtype: SendMessageErrorOptions or None
        """
        return self.ack_map.pop(ack_id, None)

    def get(self, ack_id: int) -> Optional[SendMessageErrorOptionsAsync]:
        """Get ack id from ack map

        :param ack_id: The ack id. Required.
        :type ack_id: int
        :return: The options.
        :rtype: SendMessageErrorOptions or None
        """
        return self.ack_map.get(ack_id)

    def clear(self) -> None:
        """Clear ack map"""
        for key, value in self.ack_map.items():
            _LOGGER.debug("clear ack map with ack id: %s", key)
            value.event.set()
        self.ack_map.clear()


class OpenClientError(AzureError):
    """Exception raised when fail to start the client"""


class ReconnectError(AzureError):
    """Exception raised when fail to reconnect"""


class RecoverError(AzureError):
    """Exception raised when fail to reconnect or recover the client"""

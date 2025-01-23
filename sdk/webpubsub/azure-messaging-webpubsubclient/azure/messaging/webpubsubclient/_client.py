# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
# pylint: disable=client-method-missing-tracing-decorator,too-many-lines
from typing import Any, overload, Callable, Union, Optional, Dict, List, Literal
import sys
import time
import logging
import threading
import urllib.parse
import websocket  # pylint: disable=import-error
from azure.core.pipeline.policies import RetryMode

from .models._models import (
    OnConnectedArgs,
    OnDisconnectedArgs,
    OnServerDataMessageArgs,
    OnGroupDataMessageArgs,
    WebPubSubJsonProtocol,
    WebPubSubJsonReliableProtocol,
    SequenceId,
    RetryPolicy,
    WebPubSubGroup,
    SendMessageErrorOptions,
    WebPubSubMessage,
    SendMessageType,
    SendMessageError,
    SendEventMessage,
    SendToGroupMessage,
    AckMessage,
    ConnectedMessage,
    SequenceAckMessage,
    CloseEvent,
    OnRejoinGroupFailedArgs,
    DisconnectedMessage,
    GroupDataMessage,
    ServerDataMessage,
    JoinGroupMessage,
    LeaveGroupMessage,
    AckMessageError,
    AckMap,
    OpenClientError,
    ReconnectError,
    RecoverError,
)
from .models._enums import (
    WebPubSubDataType,
    WebPubSubClientState,
    CallbackType,
    WebPubSubProtocolType,
)
from ._util import format_user_agent, raise_for_empty_message_ack

_THREAD_JOIN_TIME_OUT = 0.1
_QUEUE_MAX_SIZE = 100

_LOGGER = logging.getLogger(__name__)


class WebSocketAppBase:
    def __init__(
        self,
        reconnect_tried_times: Optional[int] = None,
        recover_start_time: Optional[float] = None,
    ) -> None:

        self.close_event: Optional[CloseEvent] = None
        self.error_happened: Optional[Exception] = None
        self.reconnect_tried_times = reconnect_tried_times
        self.recover_start_time = recover_start_time

    def clear_reconnect_recover(self):
        self.reconnect_tried_times = None
        self.recover_start_time = None


class WebSocketAppSync(websocket.WebSocketApp, WebSocketAppBase):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        url,
        on_open=None,
        on_message=None,
        on_close=None,
        on_error=None,
        subprotocols: Optional[List[str]] = None,
        header: Optional[Dict[str, str]] = None,
        reconnect_tried_times: Optional[int] = None,
        recover_start_time: Optional[float] = None,
    ) -> None:
        websocket.WebSocketApp.__init__(
            self,
            url,
            on_open=on_open,
            on_message=on_message,
            on_close=on_close,
            on_error=on_error,
            subprotocols=subprotocols,
            header=header,
        )
        WebSocketAppBase.__init__(self, reconnect_tried_times, recover_start_time)
        self.cv = threading.Condition()


class WebPubSubClientCredential:
    def __init__(self, client_access_url_provider: Union[str, Callable]) -> None:
        """
        Webpubsub client credential.

        :param client_access_url_provider: Client access url. If it's callable, it will be called to
         get the url. If it's str, it will be used directly. Please note that if you provide str, the
         connection will be closed and can't be reconnected once it is expired.
        :type client_access_url_provider: str or Callable
        """
        if isinstance(client_access_url_provider, str):
            self._client_access_url_provider = lambda: client_access_url_provider
        else:
            self._client_access_url_provider = client_access_url_provider

    def get_client_access_url(self) -> str:
        """Get client access url.
        :return: Client access url.
        :rtype: str
        """
        return self._client_access_url_provider()


_RETRY_RECONNECT_TOTAL = sys.maxsize
_RETRY_TOTAL = 3
_RETRY_BACKOFF_FACTOR = 0.8
_RETRY_BACKOFF_MAX = 120.0
_RECOVERY_TIMEOUT = 30.0
_RECOVERY_RETRY_INTERVAL = 1.0
_USER_AGENT = "User-Agent"
_ACK_TIMEOUT = 30.0
_START_TIMEOUT = 30.0


class WebPubSubClientBase:  # pylint: disable=client-accepts-api-version-keyword,too-many-instance-attributes
    """WebPubSubClientBase

    :keyword bool auto_rejoin_groups: Whether to enable restoring group after reconnecting
    :keyword ~azure.messaging.webpubsubclient.models.WebPubSubProtocolType protocol_type: Subprotocol type
    :keyword int reconnect_retry_total: total number of retries to allow for reconnect. If 0, it means disable
     reconnect. Default is 3.
    :keyword float reconnect_retry_backoff_factor: A backoff factor to apply between attempts after the second try
     (most errors are resolved immediately by a second try without a delay). In fixed mode, retry policy will always
     sleep for {backoff factor}. In 'exponential' mode, retry policy will sleep for:
     "{backoff factor} * (2 ** ({number of retries} - 1))" seconds. If the backoff_factor is 0.1, then the
     retry will sleep for [0.0s, 0.2s, 0.4s, ...] between retries. The default value is 0.8.
    :keyword float reconnect_retry_backoff_max: The maximum back off time. Default value is 120.0 seconds
    :keyword ~azure.messaging.webpubsubclient.RetryMode reconnect_retry_mode: Fixed or exponential delay
     between attemps, default is exponential.
    :keyword int message_retry_total: total number of retries to allow for sending message. Default is 3.
    :keyword float message_retry_backoff_factor: A backoff factor to apply between attempts after the second try
     (most errors are resolved immediately by a second try without a delay). In fixed mode, retry policy will always
     sleep for {backoff factor}. In 'exponential' mode, retry policy will sleep for:
     "{backoff factor} * (2 ** ({number of retries} - 1))" seconds. If the backoff_factor is 0.1, then the
     retry will sleep for [0.0s, 0.2s, 0.4s, ...] between retries. The default value is 0.8.
    :keyword float message_retry_backoff_max: The maximum back off time. Default value is 120.0 seconds
    :keyword RetryMode message_retry_mode: Fixed or exponential delay between attemps, default is exponential.
    :keyword bool auto_rejoin_groups: auto_rejoin_groups, default is True
    :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
    :keyword float ack_timeout: Time limit to wait for ack message from server. The default value is 30.0 seconds.
    :keyword float start_timeout: Time limit to wait for successful client open. The default value is 30.0 seconds.
    :keyword str user_agent: The user agent to be used for the request. If specified, this will be added in front of
     the default user agent string.
    """

    # pylint: disable=unused-argument
    def __init__(
        self,
        *,
        message_retry_backoff_factor: float = _RETRY_BACKOFF_FACTOR,
        message_retry_backoff_max: float = _RETRY_BACKOFF_MAX,
        message_retry_mode: RetryMode = RetryMode.Exponential,
        message_retry_total: int = _RETRY_TOTAL,
        protocol_type: WebPubSubProtocolType = WebPubSubProtocolType.JSON_RELIABLE,
        reconnect_retry_backoff_factor: float = _RETRY_BACKOFF_FACTOR,
        reconnect_retry_backoff_max: float = _RETRY_BACKOFF_MAX,
        reconnect_retry_mode: RetryMode = RetryMode.Exponential,
        reconnect_retry_total: int = _RETRY_RECONNECT_TOTAL,
        auto_rejoin_groups: bool = True,
        logging_enable: bool = False,
        ack_timeout: float = _ACK_TIMEOUT,
        start_timeout: float = _START_TIMEOUT,
        user_agent: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self._auto_reconnect = reconnect_retry_total > 0
        self._auto_rejoin_groups = auto_rejoin_groups
        protocol_map = {
            WebPubSubProtocolType.JSON: WebPubSubJsonProtocol,
            WebPubSubProtocolType.JSON_RELIABLE: WebPubSubJsonReliableProtocol,
        }
        if protocol_type in protocol_map:
            self._protocol = protocol_map[protocol_type]()
        else:
            self._protocol = WebPubSubJsonReliableProtocol()

        self._reconnect_retry_policy = RetryPolicy(
            retry_total=reconnect_retry_total,
            retry_backoff_factor=reconnect_retry_backoff_factor,
            retry_backoff_max=reconnect_retry_backoff_max,
            mode=reconnect_retry_mode,
        )
        self._message_retry_policy = RetryPolicy(
            retry_total=message_retry_total,
            retry_backoff_factor=message_retry_backoff_factor,
            retry_backoff_max=message_retry_backoff_max,
            mode=message_retry_mode,
        )
        self._sequence_id = SequenceId()
        self._state = WebPubSubClientState.STOPPED
        self._ack_id = 0
        self._url: str = ""
        self._handler: Dict[str, List[Callable]] = {
            CallbackType.CONNECTED: [],
            CallbackType.DISCONNECTED: [],
            CallbackType.REJOIN_GROUP_FAILED: [],
            CallbackType.GROUP_MESSAGE: [],
            CallbackType.SERVER_MESSAGE: [],
            CallbackType.STOPPED: [],
        }
        self._last_disconnected_message: Optional[DisconnectedMessage] = None
        self._connection_id: Optional[str] = None
        self._is_initial_connected = False
        self._is_stopping = False
        self._last_close_event: Optional[CloseEvent] = None
        self._reconnection_token: Optional[str] = None
        self._ack_timeout: float = ack_timeout
        self._start_timeout: float = start_timeout
        self._user_agent: Optional[str] = user_agent
        self._logging_enable: bool = logging_enable
        self._group_map: Dict[str, WebPubSubGroup] = {}

    def _build_recovery_url(self) -> Union[str, None]:
        if self._connection_id and self._reconnection_token and self._url:
            params = {
                "awps_connection_id": self._connection_id,
                "awps_reconnection_token": self._reconnection_token,
            }
            url_parse = urllib.parse.urlparse(self._url)
            url_dict = dict(urllib.parse.parse_qsl(url_parse.query))
            url_dict.update(params)
            new_query = urllib.parse.urlencode(url_dict)
            url_parse = url_parse._replace(query=new_query)
            new_url = urllib.parse.urlunparse(url_parse)
            return str(new_url)
        return None

    def _error_info(
        self,
        cost_time: float,
        error: Optional[Exception] = None,
        close_event: Optional[CloseEvent] = None,
    ) -> List[str]:
        # pylint: disable=line-too-long
        return [
            "Failed to open client.",
            (
                f"It costed {int(cost_time)} seconds to open client but still failed."
                if cost_time > self._start_timeout
                else ""
            ),
            f"During the process, an error occurred: {error}." if error else "",
            (
                f"Server sent close event, close code: {close_event.close_status_code}, reason: {close_event.close_reason}."
                if close_event
                else ""
            ),
        ]


class WebPubSubClient(
    WebPubSubClientBase
):  # pylint: disable=client-accepts-api-version-keyword,too-many-instance-attributes
    """WebPubSubClient

    :param credential: The url to connect or credential to use when connecting. Required.
    :type credential: str or WebPubSubClientCredential
    :keyword bool auto_rejoin_groups: Whether to enable restoring group after reconnecting
    :keyword ~azure.messaging.webpubsubclient.models.WebPubSubProtocolType protocol_type: Subprotocol type
    :keyword int reconnect_retry_total: total number of retries to allow for reconnect. If 0, it means disable
     reconnect. Default is 3.
    :keyword float reconnect_retry_backoff_factor: A backoff factor to apply between attempts after the second try
     (most errors are resolved immediately by a second try without a delay). In fixed mode, retry policy will always
     sleep for {backoff factor}. In 'exponential' mode, retry policy will sleep for:
     "{backoff factor} * (2 ** ({number of retries} - 1))" seconds. If the backoff_factor is 0.1, then the
     retry will sleep for [0.0s, 0.2s, 0.4s, ...] between retries. The default value is 0.8.
    :keyword float reconnect_retry_backoff_max: The maximum back off time. Default value is 120.0 seconds
    :keyword ~azure.messaging.webpubsubclient.RetryMode reconnect_retry_mode: Fixed or exponential delay
     between attemps, default is exponential.
    :keyword int message_retry_total: total number of retries to allow for sending message. Default is 3.
    :keyword float message_retry_backoff_factor: A backoff factor to apply between attempts after the second try
     (most errors are resolved immediately by a second try without a delay). In fixed mode, retry policy will always
     sleep for {backoff factor}. In 'exponential' mode, retry policy will sleep for:
     "{backoff factor} * (2 ** ({number of retries} - 1))" seconds. If the backoff_factor is 0.1, then the
     retry will sleep for [0.0s, 0.2s, 0.4s, ...] between retries. The default value is 0.8.
    :keyword float message_retry_backoff_max: The maximum back off time. Default value is 120.0 seconds
    :keyword RetryMode message_retry_mode: Fixed or exponential delay between attemps, default is exponential.
    :keyword bool auto_rejoin_groups: auto_rejoin_groups, default is True
    :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
    :keyword float ack_timeout: Time limit to wait for ack message from server. The default value is 30.0 seconds.
    :keyword float start_timeout: Time limit to wait for successful client open. The default value is 30.0 seconds.
    :keyword str user_agent: The user agent to be used for the request. If specified, this will be added in front of
     the default user agent string.
    """

    # pylint: disable=unused-argument
    def __init__(
        self,
        credential: Union[WebPubSubClientCredential, str],
        *,
        message_retry_backoff_factor: float = _RETRY_BACKOFF_FACTOR,
        message_retry_backoff_max: float = _RETRY_BACKOFF_MAX,
        message_retry_mode: RetryMode = RetryMode.Exponential,
        message_retry_total: int = _RETRY_TOTAL,
        protocol_type: WebPubSubProtocolType = WebPubSubProtocolType.JSON_RELIABLE,
        reconnect_retry_backoff_factor: float = _RETRY_BACKOFF_FACTOR,
        reconnect_retry_backoff_max: float = _RETRY_BACKOFF_MAX,
        reconnect_retry_mode: RetryMode = RetryMode.Exponential,
        reconnect_retry_total: int = _RETRY_TOTAL,
        auto_rejoin_groups: bool = True,
        logging_enable: bool = False,
        ack_timeout: float = _ACK_TIMEOUT,
        start_timeout: float = _START_TIMEOUT,
        user_agent: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if isinstance(credential, WebPubSubClientCredential):
            self._credential = credential
        elif isinstance(credential, str):
            self._credential = WebPubSubClientCredential(credential)
        else:
            raise TypeError("type of credential must be str or WebPubSubClientCredential")
        super().__init__(
            credential=credential,
            message_retry_backoff_factor=message_retry_backoff_factor,
            message_retry_backoff_max=message_retry_backoff_max,
            message_retry_mode=message_retry_mode,
            message_retry_total=message_retry_total,
            protocol_type=protocol_type,
            reconnect_retry_backoff_factor=reconnect_retry_backoff_factor,
            reconnect_retry_backoff_max=reconnect_retry_backoff_max,
            reconnect_retry_mode=reconnect_retry_mode,
            reconnect_retry_total=reconnect_retry_total,
            auto_rejoin_groups=auto_rejoin_groups,
            logging_enable=logging_enable,
            ack_timeout=ack_timeout,
            start_timeout=start_timeout,
            user_agent=user_agent,
            **kwargs,
        )
        self._group_map_lock = threading.Lock()
        self._ack_map: AckMap = AckMap()
        self._ws: Optional[WebSocketAppSync] = None
        self._thread_seq_ack: Optional[threading.Thread] = None
        self._thread: Optional[threading.Thread] = None
        self._ack_id_lock = threading.Lock()
        self._threads: List[threading.Thread] = []

    def _record_thread(self, thread: threading.Thread) -> None:
        if len(self._threads) > _QUEUE_MAX_SIZE:
            self._threads = [t for t in self._threads if t.is_alive()]
        self._threads.append(thread)
        thread.start()

    def _next_ack_id(self) -> int:
        with self._ack_id_lock:
            self._ack_id = self._ack_id + 1
        return self._ack_id

    def _send_message(self, message: WebPubSubMessage, **kwargs: Any) -> None:
        pay_load = self._protocol.write_message(message)
        if not self._ws or not self._ws.sock:
            raise SendMessageError("The websocket connection is not connected.")

        self._ws.send(pay_load)
        if kwargs.pop("logging_enable", False) or self._logging_enable:
            _LOGGER.debug("\nconnection_id: %s\npay_load: %s", self._connection_id, pay_load)

    def _send_message_with_ack_id(
        self,
        message: SendMessageType,
        **kwargs: Any,
    ) -> None:
        if message.ack_id is None:
            message.ack_id = self._next_ack_id()
        ack_id = message.ack_id

        # Unless receive ack message, we assume the message is not sent successfully.
        if not self._ack_map.get(ack_id):
            self._ack_map.add(
                ack_id,
                SendMessageErrorOptions(
                    error_detail=AckMessageError(name="", message="Timeout while waiting for ack message.")
                ),
            )
        try:
            self._send_message(message, **kwargs)
        except Exception as e:
            self._ack_map.pop(ack_id)
            raise e

        message_ack = self._ack_map.get(ack_id)
        raise_for_empty_message_ack(message_ack, ack_id)

        if message_ack is not None:
            with message_ack.cv:
                _LOGGER.debug("wait for ack message with ackId: %s", ack_id)
                message_ack.cv.wait(self._ack_timeout)
                raise_for_empty_message_ack(self._ack_map.pop(ack_id))
                if message_ack.error_detail is not None:
                    raise SendMessageError(
                        message="Failed to send message.",
                        ack_id=message_ack.ack_id,
                        error_detail=message_ack.error_detail,
                    )

    def _get_or_add_group(self, name: str) -> WebPubSubGroup:
        with self._group_map_lock:
            if name not in self._group_map:
                self._group_map[name] = WebPubSubGroup(name=name)
            return self._group_map[name]

    def join_group(self, group_name: str, **kwargs: Any) -> None:
        """Join the client to group.

        :param group_name: The group name. Required.
        :type group_name: str.
        :keyword int ack_id: The optional ackId. If not specified, client will generate one.
        """

        def join_group_attempt():
            group = self._get_or_add_group(group_name)
            self._join_group_core(group_name, **kwargs)
            group.is_joined = True

        self._retry(join_group_attempt)

    def _join_group_core(self, group_name: str, **kwargs: Any) -> None:
        ack_id = kwargs.pop("ack_id", None)
        self._send_message_with_ack_id(
            message=JoinGroupMessage(group=group_name, ack_id=ack_id),
            **kwargs,
        )

    def leave_group(self, group_name: str, **kwargs: Any) -> None:
        """Leave the client from group
        :param group_name: The group name. Required.
        :type group_name: str.
        :keyword int ack_id: The optional ackId. If not specified, client will generate one.
        """

        def leave_group_attempt():
            group = self._get_or_add_group(group_name)
            ack_id = kwargs.pop("ack_id", None)
            self._send_message_with_ack_id(
                message=LeaveGroupMessage(group=group_name, ack_id=ack_id),
                **kwargs,
            )
            group.is_joined = False

        self._retry(leave_group_attempt)

    @overload
    def send_event(
        self,
        event_name: str,
        content: str,
        data_type: Literal[WebPubSubDataType.TEXT],
        **kwargs: Any,
    ) -> None:
        """Send custom event to server. For more info about event handler in web pubsub, please refer
        to https://learn.microsoft.com/azure/azure-web-pubsub/howto-develop-eventhandler

        :param event_name: The event name. Required.
        :type event_name: str.
        :param content: The data content that you want to send to event handler that registered in web
         pubsub. Required.
        :type content: str.
        :param data_type: The data type. Required.
        :type data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType.TEXT
        :keyword int ack_id: The optional ackId. If not specified, client will generate one.
        :keyword bool ack: If False, the message won't contains ackId and no AckMessage
         will be returned from the service. Default is True.
        """

    @overload
    def send_event(
        self,
        event_name: str,
        content: memoryview,
        data_type: Literal[WebPubSubDataType.BINARY, WebPubSubDataType.PROTOBUF],
        **kwargs: Any,
    ) -> None:
        """Send custom event to server. For more info about event handler in web pubsub, please refer
        to https://learn.microsoft.com/azure/azure-web-pubsub/howto-develop-eventhandler

        :param event_name: The event name. Required.
        :type event_name: str.
        :param content: The data content that you want to send to event handler that registered in web
         pubsub. Required.
        :type content: memoryview.
        :param data_type: The data type. Required.
        :type data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType.BINARY or
         ~azure.messaging.webpubsubclient.models.WebPubSubDataType.PROTOBUF
        :keyword int ack_id: The optional ackId. If not specified, client will generate one.
        :keyword bool ack: If False, the message won't contains ackId and no AckMessage
         will be returned from the service. Default is True.
        """

    @overload
    def send_event(
        self,
        event_name: str,
        content: Dict[str, Any],
        data_type: Literal[WebPubSubDataType.JSON],
        **kwargs: Any,
    ) -> None:
        """Send custom event to server. For more info about event handler in web pubsub, please refer
        to https://learn.microsoft.com/azure/azure-web-pubsub/howto-develop-eventhandler

        :param event_name: The event name. Required.
        :type event_name: str.
        :param content: The data content that you want to send to event handler that registered in web
         pubsub. Required.
        :type content: Dict[str, Any].
        :param data_type: The data type. Required.
        :type data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType.JSON
        :keyword int ack_id: The optional ackId. If not specified, client will generate one.
        :keyword bool ack: If False, the message won't contains ackId and no AckMessage
         will be returned from the service. Default is True.
        """

    def send_event(
        self,
        event_name: str,
        content: Union[str, memoryview, Dict[str, Any]],
        data_type: WebPubSubDataType,
        **kwargs: Any,
    ) -> None:
        """Send custom event to server. For more info about event handler in web pubsub, please refer
        to https://learn.microsoft.com/azure/azure-web-pubsub/howto-develop-eventhandler

        :param event_name: The event name. Required.
        :type event_name: str.
        :param content: The data content that you want to send to event handler that registered in web
         pubsub. Required.
        :type content: Union[str, memoryview, Dict[str, Any]].
        :param data_type: The data type. Required.
        :type data_type: Union[~azure.messaging.webpubsubclient.models.WebPubSubDataType, str].
        :keyword int ack_id: The optional ackId. If not specified, client will generate one.
        :keyword bool ack: If False, the message won't contains ackId and no AckMessage
         will be returned from the service. Default is True.
        """

        def send_event_attempt():
            ack = kwargs.pop("ack", True)
            ack_id = kwargs.pop("ack_id", None)
            if ack:
                self._send_message_with_ack_id(
                    message=SendEventMessage(data_type=data_type, data=content, ack_id=ack_id, event=event_name),
                    ack_id=ack_id,
                    **kwargs,
                )
            else:
                self._send_message(
                    message=SendEventMessage(data_type=data_type, data=content, event=event_name),
                    **kwargs,
                )

        self._retry(send_event_attempt)

    @overload
    def send_to_group(
        self,
        group_name: str,
        content: str,
        data_type: Literal[WebPubSubDataType.TEXT],
        **kwargs: Any,
    ) -> None:
        """Send message to group.

        :param group_name: The group name. Required.
        :type group_name: str.
        :param content: The data content. Required.
        :type content: str.
        :param data_type: The data type. Required.
        :type data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType.TEXT
        :keyword int ack_id: The optional ackId. If not specified, client will generate one.
        :keyword bool ack: If False, the message won't contains ackId and no AckMessage
         will be returned from the service. Default is True.
        :keyword bool no_echo: Whether the message needs to echo to sender. Default is False.
        """

    @overload
    def send_to_group(
        self,
        group_name: str,
        content: Dict[str, Any],
        data_type: Literal[WebPubSubDataType.JSON],
        **kwargs: Any,
    ) -> None:
        """Send message to group.

        :param group_name: The group name. Required.
        :type group_name: str.
        :param content: The data content. Required.
        :type content: Dict[str, Any].
        :param data_type: The data type. Required.
        :type data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType.JSON
        :keyword int ack_id: The optional ackId. If not specified, client will generate one.
        :keyword bool ack: If False, the message won't contains ackId and no AckMessage
         will be returned from the service. Default is True.
        :keyword bool no_echo: Whether the message needs to echo to sender. Default is False.
        """

    @overload
    def send_to_group(
        self,
        group_name: str,
        content: memoryview,
        data_type: Literal[WebPubSubDataType.BINARY, WebPubSubDataType.PROTOBUF],
        **kwargs: Any,
    ) -> None:
        """Send message to group.

        :param group_name: The group name. Required.
        :type group_name: str.
        :param content: The data content. Required.
        :type content: memoryview.
        :param data_type: The data type. Required.
        :type data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType.BINARY or
         ~azure.messaging.webpubsubclient.models.WebPubSubDataType.PROTOBUF
        :keyword int ack_id: The optional ackId. If not specified, client will generate one.
        :keyword bool ack: If False, the message won't contains ackId and no AckMessage
         will be returned from the service. Default is True.
        :keyword bool no_echo: Whether the message needs to echo to sender. Default is False.
        """

    def send_to_group(
        self,
        group_name: str,
        content: Union[str, memoryview, Dict[str, Any]],
        data_type: WebPubSubDataType,
        **kwargs: Any,
    ) -> None:
        """Send message to group.

        :param group_name: The group name. Required.
        :type group_name: str.
        :param content: The data content. Required.
        :type content: Union[str, memoryview, Dict[str, Any]].
        :param data_type: The data type. Required.
        :type data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType or str.
        :keyword int ack_id: The optional ackId. If not specified, client will generate one.
        :keyword bool ack: If False, the message won't contains ackId and no AckMessage
         will be returned from the service. Default is True.
        :keyword bool no_echo: Whether the message needs to echo to sender. Default is False.
        """

        def send_to_group_attempt():
            ack = kwargs.pop("ack", True)
            no_echo = kwargs.pop("no_echo", False)
            ack_id = kwargs.pop("ack_id", None)
            if ack:
                self._send_message_with_ack_id(
                    message=SendToGroupMessage(
                        group=group_name,
                        data_type=data_type,
                        data=content,
                        ack_id=ack_id,
                        no_echo=no_echo,
                    ),
                    **kwargs,
                )
            else:
                self._send_message(
                    message=SendToGroupMessage(
                        group=group_name,
                        data_type=data_type,
                        data=content,
                        no_echo=no_echo,
                    ),
                    **kwargs,
                )

        self._retry(send_to_group_attempt)

    def _retry(self, func: Callable[[], None]):
        retry_attempt = 0
        while True:
            try:
                func()
                return
            except Exception as e:  # pylint: disable=broad-except
                retry_attempt = retry_attempt + 1
                delay_seconds = self._message_retry_policy.next_retry_delay(retry_attempt)
                if delay_seconds is None:
                    raise e
                _LOGGER.debug(
                    "will retry %sth times after %s seconds",
                    retry_attempt,
                    delay_seconds,
                )
                time.sleep(delay_seconds)

    def _call_back(self, callback_type: CallbackType, *args):
        for func in self._handler[callback_type]:
            # _call_back works in listener thread which must not be blocked so we have to execute the func
            # in new thread to avoid dead lock
            self._record_thread(threading.Thread(target=func, args=args, daemon=True))

    def _start_from_restarting(self, reconnect_tried_times: Optional[int] = None):
        if self._state != WebPubSubClientState.DISCONNECTED:
            _LOGGER.warning("Client can be only restarted when it's Disconnected")
            return

        try:
            self._start_core(reconnect_tried_times)
        except Exception as e:
            self._state = WebPubSubClientState.DISCONNECTED
            raise e

    def _handle_auto_reconnect(self, reconnect_tried_times: Optional[int] = None):
        _LOGGER.debug("start auto reconnect")
        success = False
        attempt = -1 if reconnect_tried_times is None else reconnect_tried_times
        while not self._is_stopping:
            try:
                attempt = attempt + 1
                if attempt > 0:
                    delay_seconds = self._reconnect_retry_policy.next_retry_delay(attempt)
                    if not delay_seconds:
                        break
                    _LOGGER.debug(
                        "Delay time for reconnect attempt %d: %ds",
                        attempt,
                        delay_seconds,
                    )
                    time.sleep(delay_seconds)
                self._start_from_restarting(reconnect_tried_times)
                if self._ws:
                    self._ws.clear_reconnect_recover()
                success = True
                break
            except ReconnectError:
                _LOGGER.debug("Failed to reconnect, and will retry in another thread.")
                break
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.warning("An attempt to reconnect connection failed %s", e)
        if not success:
            self._handle_connection_stopped()
        else:
            _LOGGER.debug("reconnect successfully")

    def _handle_connection_stopped(self):
        _LOGGER.debug("Connection stopped")
        self._is_stopping = False
        self._state = WebPubSubClientState.STOPPED
        self._call_back(CallbackType.STOPPED)

    def _handle_connection_close_and_no_recovery(self, reconnect_tried_times: Optional[int] = None):
        _LOGGER.debug("Connection closed and no recovery")
        self._state = WebPubSubClientState.DISCONNECTED
        self._call_back(
            CallbackType.DISCONNECTED,
            OnDisconnectedArgs(
                connection_id=self._connection_id,
                message=(self._last_disconnected_message.message if self._last_disconnected_message else None),
            ),
        )
        if self._auto_reconnect:
            self._handle_auto_reconnect(reconnect_tried_times)
        else:
            self._handle_connection_stopped()

    def is_connected(self) -> bool:
        """check whether the client is still connected to server after open

        :return: True if the client is connected to server, otherwise False
        :rtype: bool
        """
        return bool(
            self._state == WebPubSubClientState.CONNECTED
            and self._thread
            and self._thread.is_alive()
            and self._ws
            and self._ws.sock
        )

    def _rejoin_group(self, group_name: str):
        def _rejoin_group_func():
            try:
                self._join_group_core(group_name)
                _LOGGER.debug("rejoin group %s successfully", group_name)
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.debug("fail to rejoin group %s", group_name)
                self._call_back(
                    CallbackType.REJOIN_GROUP_FAILED,
                    OnRejoinGroupFailedArgs(group=group_name, error=e),
                )

        self._record_thread(threading.Thread(target=_rejoin_group_func, daemon=True))

    def _connect(
        self,
        url: str,
        reconnect_tried_times: Optional[int] = None,
        recover_start_time: Optional[float] = None,
    ):  # pylint: disable=too-many-statements
        def on_open(ws_instance: WebSocketAppSync):
            if self._is_stopping:
                try:
                    if self._ws:
                        self._ws.close()
                finally:
                    raise OpenClientError("Can't open a client during stopping")

            _LOGGER.debug("WebSocket connection has opened")
            self._state = WebPubSubClientState.CONNECTED
            with ws_instance.cv:
                ws_instance.cv.notify()

        def on_message(_: Any, data: str):
            message = self._protocol.parse_messages(data)
            if message is None:
                #  None means the message is not recognized.
                return
            if message.kind == "connected":
                _LOGGER.debug("WebSocket is connected with id: %s", message.connection_id)
                self._connection_id = message.connection_id
                self._reconnection_token = message.reconnection_token

                if not self._is_initial_connected:
                    self._is_initial_connected = True
                    if self._auto_rejoin_groups:
                        with self._group_map_lock:
                            for group_name, group in self._group_map.items():
                                if group.is_joined:
                                    self._rejoin_group(group_name)

                    self._call_back(
                        CallbackType.CONNECTED,
                        OnConnectedArgs(connection_id=message.connection_id, user_id=message.user_id),
                    )
            elif message.kind == "disconnected":
                self._last_disconnected_message = message
            elif message.kind == "ack":
                ack_option = self._ack_map.get(message.ack_id)
                if ack_option:
                    if not (message.success or (message.error and message.error.name == "Duplicate")):
                        ack_option.error_detail = message.error
                    else:
                        ack_option.error_detail = None
                    ack_option.ack_id = message.ack_id
                    _LOGGER.debug("Ack message received. Ack id is : %d", message.ack_id)
                    with ack_option.cv:
                        ack_option.cv.notify()
            elif message.kind == "groupData":
                if message.sequence_id:
                    if not self._sequence_id.try_update(message.sequence_id):
                        # drop duplicated message
                        return

                self._call_back(
                    CallbackType.GROUP_MESSAGE,
                    OnGroupDataMessageArgs(
                        data_type=message.data_type,
                        data=message.data,
                        group=message.group,
                        from_user_id=message.from_user_id,
                        sequence_id=message.sequence_id,
                    ),
                )
            elif message.kind == "serverData":
                if message.sequence_id:
                    if not self._sequence_id.try_update(message.sequence_id):
                        # drop duplicated message
                        return

                self._call_back(
                    CallbackType.SERVER_MESSAGE,
                    OnServerDataMessageArgs(
                        data_type=message.data_type,
                        data=message.data,
                        sequence_id=message.sequence_id,
                    ),
                )
            else:
                _LOGGER.warning("unknown message type: %s", message.kind)

        def on_close(
            ws_instance: WebSocketAppSync,
            close_status_code: Optional[int] = None,
            close_msg: Optional[str] = None,
        ):
            if self._state == WebPubSubClientState.CONNECTED:
                _LOGGER.info(
                    "WebSocket connection closed. Code: %s, Reason: %s",
                    close_status_code,
                    close_msg,
                )

                self._last_close_event = CloseEvent(close_status_code=close_status_code, close_reason=close_msg)
                # clean ack cache
                self._ack_map.clear()

                if self._is_stopping:
                    _LOGGER.info("The client is stopping state. Stop recovery.")
                    self._handle_connection_close_and_no_recovery(ws_instance.reconnect_tried_times)
                    return

                if self._last_close_event and self._last_close_event.close_status_code == 1008:
                    _LOGGER.warning("The websocket close with status code 1008. Stop recovery.")
                    self._handle_connection_close_and_no_recovery(ws_instance.reconnect_tried_times)
                    return

                if not self._protocol.is_reliable_sub_protocol:
                    _LOGGER.warning("The protocol is not reliable, recovery is not applicable")
                    self._handle_connection_close_and_no_recovery(ws_instance.reconnect_tried_times)
                    return

                recovery_url = self._build_recovery_url()
                if not recovery_url:
                    _LOGGER.warning("Connection id or reconnection token is not available")
                    self._handle_connection_close_and_no_recovery(ws_instance.reconnect_tried_times)
                    return

                self._state = WebPubSubClientState.RECOVERING
                recovery_start = (
                    time.time() if ws_instance.recover_start_time is None else ws_instance.recover_start_time
                )
                first_time = True
                while (time.time() - recovery_start < _RECOVERY_TIMEOUT) and not self._is_stopping:
                    try:
                        if ws_instance.recover_start_time is not None or not first_time:
                            time.sleep(_RECOVERY_RETRY_INTERVAL)
                        self._connect(recovery_url, None, recovery_start)
                        if self._ws:
                            self._ws.clear_reconnect_recover()
                        _LOGGER.debug("Recovery succeeded")
                        return
                    except RecoverError:
                        _LOGGER.debug("Failed to recover, and will try in another thread")
                        return
                    except Exception as e:  # pylint: disable=broad-except
                        first_time = False
                        _LOGGER.debug("Fail to recover: %s", e)
                        _LOGGER.debug("Try to recover after %d seconds", _RECOVERY_RETRY_INTERVAL)

                _LOGGER.warning("Recovery attempts failed after 30 seconds or the client is stopping")
                self._handle_connection_close_and_no_recovery(ws_instance.reconnect_tried_times)
            else:
                with ws_instance.cv:
                    if close_status_code or close_msg:
                        ws_instance.close_event = CloseEvent(
                            close_status_code=close_status_code, close_reason=close_msg
                        )
                    ws_instance.cv.notify()

        def on_error(ws_instance: WebSocketAppSync, error: Exception):
            _LOGGER.warning("An error occurred when trying to connect: %s", error)
            ws_instance.error_happened = error

        if self._is_stopping:
            raise OpenClientError("Can't open a client during closing")

        # when reconnect or recovery, _thread will come here then stop by itself so don't join it
        self._threads_join([self._thread_seq_ack])

        self._ws = WebSocketAppSync(
            url=url,
            on_open=on_open,
            on_message=on_message,
            on_close=on_close,
            on_error=on_error,
            subprotocols=[self._protocol.name] if self._protocol else [],
            header={_USER_AGENT: format_user_agent(self._user_agent)},
            reconnect_tried_times=reconnect_tried_times,
            recover_start_time=recover_start_time,
        )

        # set thread to start listen to server
        self._thread = threading.Thread(target=self._ws.run_forever, daemon=True)
        self._thread.start()
        start_time = time.time()
        with self._ws.cv:
            self._ws.cv.wait(timeout=self._start_timeout)
        cost_time = time.time() - start_time
        if not self.is_connected():
            if self._thread.is_alive():
                if reconnect_tried_times is not None:
                    raise ReconnectError("Failed to reconnect after waiting")
                if recover_start_time is not None:
                    raise RecoverError("Failed to recover after waiting")
            raise OpenClientError(" ".join(self._error_info(cost_time, self._ws.error_happened, self._ws.close_event)))

        # set thread to check sequence id if needed
        if self._protocol.is_reliable_sub_protocol:

            def sequence_id_ack_periodically():
                while self.is_connected():
                    try:
                        is_updated, seq_id = self._sequence_id.try_get_sequence_id()
                        if is_updated and seq_id is not None:
                            self._send_message(SequenceAckMessage(sequence_id=seq_id))
                    finally:
                        time.sleep(1.0)

            self._thread_seq_ack = threading.Thread(target=sequence_id_ack_periodically, daemon=True)
            self._thread_seq_ack.start()

        _LOGGER.info("connected successfully")

    def _start_core(self, reconnect_tried_times: Optional[int] = None):
        self._state = WebPubSubClientState.CONNECTING
        _LOGGER.info("Staring a new connection")

        # Reset before a pure new connection
        self._sequence_id.reset()
        self._is_initial_connected = False
        self._last_close_event = None
        self._last_disconnected_message = None
        self._connection_id = None
        self._reconnection_token = None
        self._url = ""
        self._threads.clear()

        self._url = self._credential.get_client_access_url()
        self._connect(self._url, reconnect_tried_times)

    def open(self) -> None:
        """open the client and connect to service"""

        if self._is_stopping:
            raise OpenClientError("Can't open a client during stopping")
        if self._state != WebPubSubClientState.STOPPED:
            raise OpenClientError("Client can be only started when it's Stopped")

        try:
            self._start_core()
        except Exception as e:
            self._state = WebPubSubClientState.STOPPED
            self._is_stopping = False
            raise e

    def close(self) -> None:
        """close the client"""

        if self._state == WebPubSubClientState.STOPPED or self._is_stopping:
            _LOGGER.info("client has been closed or is stopping")
            return
        self._is_stopping = True
        old_threads = [self._thread, self._thread_seq_ack] + self._threads

        if self._ws:
            _LOGGER.info("send close code to drop connection")
            self._ws.close()

        _LOGGER.info("waiting for close")
        self._threads_join(old_threads)

        if self._is_stopping and self._ws and self._ws.on_close:
            # have to manually trigger on_close
            _LOGGER.debug("manually trigger on_close")
            self._ws.on_close(self._ws, None, None)  # type: ignore

        _LOGGER.info("close client successfully")

    @staticmethod
    def _threads_join(old_threads: List[Optional[threading.Thread]]):
        for t in old_threads:
            if t and t.is_alive():
                t.join(_THREAD_JOIN_TIME_OUT)

    @overload
    def subscribe(
        self,
        event: Literal[CallbackType.CONNECTED],
        listener: Callable[[OnConnectedArgs], None],
    ) -> None:
        """Add handler for connected event.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.CONNECTED
        :param listener: The handler
        :type listener: callable.
        """

    @overload
    def subscribe(
        self,
        event: Literal[CallbackType.DISCONNECTED],
        listener: Callable[[OnDisconnectedArgs], None],
    ) -> None:
        """Add handler for disconnected event.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.DISCONNECTED
        :param listener: The handler
        :type listener: callable.
        """

    @overload
    def subscribe(
        self,
        event: Literal[CallbackType.STOPPED],
        listener: Callable[[], None],
    ) -> None:
        """Add handler for stopped event.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.STOPPED
        :param listener: The handler
        :type listener: callable.
        """

    @overload
    def subscribe(
        self,
        event: Literal[CallbackType.SERVER_MESSAGE],
        listener: Callable[[OnServerDataMessageArgs], None],
    ) -> None:
        """Add handler for server messages.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.SERVER_MESSAGE
        :param listener: The handler
        :type listener: callable.
        """

    @overload
    def subscribe(
        self,
        event: Literal[CallbackType.GROUP_MESSAGE],
        listener: Callable[[OnGroupDataMessageArgs], None],
    ) -> None:
        """Add handler for group messages.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.GROUP_MESSAGE
        :param listener: The handler
        :type listener: callable.
        """

    @overload
    def subscribe(
        self,
        event: Literal[CallbackType.REJOIN_GROUP_FAILED],
        listener: Callable[[OnRejoinGroupFailedArgs], None],
    ) -> None:
        """Add handler for rejoining group failed.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.REJOIN_GROUP_FAILED
         or Literal["rejoin-group-failed"]
        :param listener: The handler
        :type listener: callable.
        """

    def subscribe(
        self,
        event: CallbackType,
        listener: Callable,
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Add handler.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType
        :param listener: The handler
        :type listener: callable.
        """
        if event in self._handler:
            self._handler[event].append(listener)
        else:
            _LOGGER.error("wrong event type: %s", event)

    @overload
    def unsubscribe(
        self,
        event: Literal[CallbackType.CONNECTED],
        listener: Callable[[OnConnectedArgs], None],
    ) -> None:
        """Remove handler for connected event.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.CONNECTED
        :param listener: The handler
        :type listener: callable.
        """

    @overload
    def unsubscribe(
        self,
        event: Literal[CallbackType.DISCONNECTED],
        listener: Callable[[OnDisconnectedArgs], None],
    ) -> None:
        """Remove handler for connected event.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.DISCONNECTED
        :param listener: The handler
        :type listener: callable.
        """

    @overload
    def unsubscribe(
        self,
        event: Literal[CallbackType.STOPPED],
        listener: Callable[[], None],
    ) -> None:
        """Remove handler for stopped event.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.STOPPED
        :param listener: The handler
        :type listener: callable.
        """

    @overload
    def unsubscribe(
        self,
        event: Literal[CallbackType.SERVER_MESSAGE],
        listener: Callable[[OnServerDataMessageArgs], None],
    ) -> None:
        """Remove handler for server message.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.SERVER_MESSAGE
        :param listener: The handler
        :type listener: callable.
        """

    @overload
    def unsubscribe(
        self,
        event: Literal[CallbackType.GROUP_MESSAGE],
        listener: Callable[[OnGroupDataMessageArgs], None],
    ) -> None:
        """Remove handler for group message.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.GROUP_MESSAGE
        :param listener: The handler
        :type listener: callable.
        """

    @overload
    def unsubscribe(
        self,
        event: Literal[CallbackType.REJOIN_GROUP_FAILED],
        listener: Callable[[OnRejoinGroupFailedArgs], None],
    ) -> None:
        """Remove handler for rejoining group failed.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.REJOIN_GROUP_FAILED
         or Literal["rejoin-group-failed"]
        :param listener: The handler
        :type listener: callable.
        """

    def unsubscribe(
        self,
        event: CallbackType,
        listener: Callable,
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Remove handler for rejoining group failed.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType
        :param listener: The handler
        :type listener: callable.
        """
        if event in self._handler:
            if listener in self._handler[event]:
                self._handler[event].remove(listener)
            else:
                _LOGGER.info("target listener does not exist")
        else:
            _LOGGER.error("wrong event type: %s", event)

    def __enter__(self):
        self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):  # pylint: disable=unused-argument
        self.close()

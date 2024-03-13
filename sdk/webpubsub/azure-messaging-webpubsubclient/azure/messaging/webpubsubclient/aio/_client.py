# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import asyncio
import inspect
from typing import Any, overload, Callable, Union, Optional, Dict, List, Literal, Awaitable
import time
import logging
import urllib.parse
import aiohttp
from azure.core.pipeline.policies import RetryMode

from ..models._models import (
    OnConnectedArgs,
    OnDisconnectedArgs,
    OnServerDataMessageArgs,
    OnGroupDataMessageArgs,
    WebPubSubJsonProtocol,
    WebPubSubJsonReliableProtocol,
    SequenceId,
    RetryPolicy,
    WebPubSubGroup,
    SendMessageErrorOptionsAsync,
    WebPubSubMessage,
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
    AckMapAsync,
    OpenClientError,
)
from ..models._enums import (
    WebPubSubDataType,
    WebPubSubClientState,
    CallbackType,
    WebPubSubProtocolType,
)
from .._client import WebPubSubClientCredential, _RETRY_TOTAL, _RETRY_BACKOFF_FACTOR, _RETRY_BACKOFF_MAX, _RECOVERY_TIMEOUT, _RECOVERY_RETRY_INTERVAL, _USER_AGENT, _ACK_TIMEOUT, _START_TIMEOUT
from .._util import format_user_agent

_LOGGER = logging.getLogger(__name__)

class WebSocketAppAsync:

    def __init__(self, url, on_open=None, on_message=None,on_close=None,subprotocols: Optional[List[str]]=None,header: Optional[Dict[str, str]]=None) -> None:
        self.url = url
        self.on_open = on_open
        self.on_message = on_message
        self.on_close = on_close
        self.subprotocols = subprotocols
        self.header = header
        self._session: Optional[aiohttp.ClientSession] = None
        self._sock: Optional[aiohttp.client._WSRequestContextManager] = None

    async def receive(self) -> aiohttp.WSMessage:
        return await self._sock.receive()

    async def send(self, message: str) -> None:
        await self._sock.send_str(message)

    async def run_forever(self):
        await self.on_open()

    async def connect(self):
        self._session = aiohttp.ClientSession()
        self._sock = await self._session.ws_connect(self.url, protocols=self.subprotocols, headers=self.header)

    async def close(self):
        await self._sock.close()
        await self._session.close()
    
    @property
    def closed(self):
        return self._sock.closed

class WebPubSubClient:  # pylint: disable=client-accepts-api-version-keyword,too-many-instance-attributes
    """WebPubSubClient

    :param credential: The url to connect or credential to use when connecting. Required.
    :type credential: str or WebPubSubClientCredential
    :keyword bool auto_rejoin_groups: Whether to enable restoring group after reconnecting
    :keyword azure.messaging.webpubsubclient.models.WebPubSubProtocolType protocol_type: Subprotocol type
    :keyword int reconnect_retry_total: total number of retries to allow for reconnect. If 0, it means disable
     reconnect. Default is 3.
    :keyword float reconnect_retry_backoff_factor: A backoff factor to apply between attempts after the second try
     (most errors are resolved immediately by a second try without a delay). In fixed mode, retry policy will always
     sleep for {backoff factor}. In 'exponential' mode, retry policy will sleep for:
     "{backoff factor} * (2 ** ({number of retries} - 1))" seconds. If the backoff_factor is 0.1, then the
     retry will sleep for [0.0s, 0.2s, 0.4s, ...] between retries. The default value is 0.8.
    :keyword float reconnect_retry_backoff_max: The maximum back off time. Default value is 120.0 seconds
    :keyword RetryMode reconnect_retry_mode: Fixed or exponential delay between attemps, default is exponential.
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
        self._group_map: Dict[str, WebPubSubGroup] = {}
        self._group_map_lock = asyncio.Lock()
        self._ack_map: AckMapAsync = AckMapAsync()
        self._sequence_id = SequenceId()
        self._state = WebPubSubClientState.STOPPED
        self._ack_id = 0
        self._ack_id_lock = asyncio.Lock()
        self._url = None
        self._ws: Optional[WebSocketAppAsync] = None
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
        self._task_seq_ack: Optional[asyncio.Task] = None
        self._task_listen: Optional[asyncio.Task] = None
        self._ack_timeout: float = ack_timeout
        self._start_timeout: float = start_timeout
        self._user_agent: Optional[str] = user_agent
        self._logging_enable: bool = logging_enable

    async def _next_ack_id(self) -> int:
        async with self._ack_id_lock:
            self._ack_id = self._ack_id + 1
        return self._ack_id

    async def _send_message(self, message: WebPubSubMessage, **kwargs: Any) -> None:
        pay_load = self._protocol.write_message(message)
        if self._ws.closed:
            raise SendMessageError("The websocket connection is not connected.")

        await self._ws.send(pay_load)
        if kwargs.pop("logging_enable", False) or self._logging_enable:
            _LOGGER.debug("\nconnection_id: %s\npay_load: %s", self._connection_id, pay_load)

    async def _send_message_with_ack_id(
        self,
        message_provider: Callable[[int], WebPubSubMessage],
        ack_id: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        if ack_id is None:
            ack_id = await self._next_ack_id()

        message = message_provider(ack_id)
        # Unless receive ack message, we assume the message is not sent successfully.
        if not (await self._ack_map.get(ack_id)):
            await self._ack_map.add(
                ack_id,
                SendMessageErrorOptionsAsync(
                    error_detail=AckMessageError(name="", message="Timeout while waiting for ack message.")
                ),
            )
        try:
            await self._send_message(message, **kwargs)
        except Exception as e:
            await self._ack_map.pop(ack_id)
            raise e

        message_ack = await self._ack_map.get(ack_id)
        if not message_ack:
            raise SendMessageError(
                message="Failed to send message.",
                ack_id=ack_id,
                error_detail=AckMessageError(
                    name="NoAckMessageReceivedFromServer",
                    message="The connection may have been lost during message sending or service don't send ack message.",
                ),
            )
        _LOGGER.debug("wait for ack message with ackId: %s", ack_id)
        await asyncio.wait_for(message_ack.event.wait(), timeout=self._ack_timeout)
        await self._ack_map.pop(ack_id)
        if message_ack.error_detail is not None:
            raise SendMessageError(
                message="Failed to send message.",
                ack_id=message_ack.ack_id,
                error_detail=message_ack.error_detail,
            )

    async def _get_or_add_group(self, name: str) -> WebPubSubGroup:
        async with self._group_map_lock:
            if name not in self._group_map:
                self._group_map[name] = WebPubSubGroup(name=name)
            return self._group_map[name]

    async def join_group(self, group_name: str, **kwargs: Any) -> None:
        """Join the client to group.

        :param group_name: The group name. Required.
        :type group_name: str.
        :keyword int ack_id: The optional ackId. If not specified, client will generate one.
        """

        async def join_group_attempt():
            group = await self._get_or_add_group(group_name)
            await self._join_group_core(group_name, **kwargs)
            group.is_joined = True

        await self._retry(join_group_attempt)

    async def _join_group_core(self, group_name: str, **kwargs: Any) -> None:
        ack_id = kwargs.pop("ack_id", None)
        await self._send_message_with_ack_id(
            message_provider=lambda id: JoinGroupMessage(group=group_name, ack_id=id),
            ack_id=ack_id,
            **kwargs,
        )

    async def leave_group(self, group_name: str, **kwargs: Any) -> None:
        """Leave the client from group
        :param group_name: The group name. Required.
        :type group_name: str.
        :keyword int ack_id: The optional ackId. If not specified, client will generate one.
        """
        async def leave_group_attempt():
            group = await self._get_or_add_group(group_name)
            ack_id = kwargs.pop("ack_id", None)
            await self._send_message_with_ack_id(
                message_provider=lambda id: LeaveGroupMessage(group=group_name, ack_id=id),
                ack_id=ack_id,
                **kwargs,
            )
            group.is_joined = False

        await self._retry(leave_group_attempt)

    @overload
    async def send_event(
        self,
        event_name: str,
        content: str,
        data_type: Union[Literal[WebPubSubDataType.TEXT], Literal["text"]],
        **kwargs: Any,
    ) -> None:
        """Send custom event to server. For more info about event handler in web pubsub, please refer
        to https://learn.microsoft.com/en-us/azure/azure-web-pubsub/howto-develop-eventhandler

        :param event_name: The event name. Required.
        :type event_name: str.
        :param content: The data content that you want to send to event handler that registered in web
         pubsub. Required.
        :type content: str.
        :param data_type: The data type. Required.
        :type data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType.TEXT or Literal["text"].
        :keyword int ack_id: The optional ackId. If not specified, client will generate one.
        :keyword bool ack: If False, the message won't contains ackId and no AckMessage
         will be returned from the service. Default is True.
        """

    @overload
    async def send_event(
        self,
        event_name: str,
        content: memoryview,
        data_type: Union[
            Literal[WebPubSubDataType.BINARY],
            Literal[WebPubSubDataType.PROTOBUF],
            Literal["binary"],
            Literal["protobuf"],
        ],
        **kwargs: Any,
    ) -> None:
        """Send custom event to server. For more info about event handler in web pubsub, please refer
        to https://learn.microsoft.com/en-us/azure/azure-web-pubsub/howto-develop-eventhandler

        :param event_name: The event name. Required.
        :type event_name: str.
        :param content: The data content that you want to send to event handler that registered in web
         pubsub. Required.
        :type content: memoryview.
        :param data_type: The data type. Required.
        :type data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType.BINARY or
         ~azure.messaging.webpubsubclient.models.WebPubSubDataType.PROTOBUF or
         Literal["binary"] or Literal["protobuf"].
        :keyword int ack_id: The optional ackId. If not specified, client will generate one.
        :keyword bool ack: If False, the message won't contains ackId and no AckMessage
         will be returned from the service. Default is True.
        """

    @overload
    async def send_event(
        self,
        event_name: str,
        content: Dict[str, Any],
        data_type: Union[Literal[WebPubSubDataType.JSON], Literal["json"]],
        **kwargs: Any,
    ) -> None:
        """Send custom event to server. For more info about event handler in web pubsub, please refer
        to https://learn.microsoft.com/en-us/azure/azure-web-pubsub/howto-develop-eventhandler

        :param event_name: The event name. Required.
        :type event_name: str.
        :param content: The data content that you want to send to event handler that registered in web
         pubsub. Required.
        :type content: Dict[str, Any].
        :param data_type: The data type. Required.
        :type data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType.JSON or Literal["json"].
        :keyword int ack_id: The optional ackId. If not specified, client will generate one.
        :keyword bool ack: If False, the message won't contains ackId and no AckMessage
         will be returned from the service. Default is True.
        """

    async def send_event(
        self,
        event_name: str,
        content: Union[str, memoryview, Dict[str, Any]],
        data_type: Union[WebPubSubDataType, str],
        **kwargs: Any,
    ) -> None:
        """Send custom event to server. For more info about event handler in web pubsub, please refer
        to https://learn.microsoft.com/en-us/azure/azure-web-pubsub/howto-develop-eventhandler

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
        async def send_event_attempt():
            ack = kwargs.pop("ack", True)
            ack_id = kwargs.pop("ack_id", None)
            if ack:
                await self._send_message_with_ack_id(
                    message_provider=lambda id: SendEventMessage(
                        data_type=data_type, data=content, ack_id=id, event=event_name
                    ),
                    ack_id=ack_id,
                    **kwargs,
                )
            else:
                await self._send_message(
                    message=SendEventMessage(data_type=data_type, data=content, event=event_name),
                    **kwargs,
                )

        await self._retry(send_event_attempt)

    @overload
    async def send_to_group(
        self,
        group_name: str,
        content: str,
        data_type: Union[Literal[WebPubSubDataType.TEXT], Literal["text"]],
        **kwargs: Any,
    ) -> None:
        """Send message to group.
        :param group_name: The group name. Required.
        :type group_name: str.
        :param content: The data content. Required.
        :type content: str.
        :param data_type: The data type. Required.
        :type data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType.TEXT or Literal["text"].
        :keyword bool ack: If False, the message won't contains ackId and no AckMessage
         will be returned from the service. Default is True.
        :keyword bool no_echo: Whether the message needs to echo to sender. Default is False.
        """

    @overload
    async def send_to_group(
        self,
        group_name: str,
        content: Dict[str, Any],
        data_type: Union[Literal[WebPubSubDataType.JSON], Literal["json"]],
        **kwargs: Any,
    ) -> None:
        """Send message to group.
        :param group_name: The group name. Required.
        :type group_name: str.
        :param content: The data content. Required.
        :type content: Dict[str, Any].
        :param data_type: The data type. Required.
        :type data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType.JSON or Literal["json"].
        :keyword bool ack: If False, the message won't contains ackId and no AckMessage
         will be returned from the service. Default is True.
        :keyword bool no_echo: Whether the message needs to echo to sender. Default is False.
        """

    @overload
    async def send_to_group(
        self,
        group_name: str,
        content: memoryview,
        data_type: Union[
            Literal[WebPubSubDataType.BINARY],
            Literal[WebPubSubDataType.PROTOBUF],
            Literal["binary"],
            Literal["protobuf"],
        ],
        **kwargs: Any,
    ) -> None:
        """Send message to group.
        :param group_name: The group name. Required.
        :type group_name: str.
        :param content: The data content. Required.
        :type content: memoryview.
        :param data_type: The data type. Required.
        :type data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType.BINARY or
         ~azure.messaging.webpubsubclient.models.WebPubSubDataType.PROTOBUF or
         Literal["binary"] or Literal["protobuf"].
        :keyword bool ack: If False, the message won't contains ackId and no AckMessage
         will be returned from the service. Default is True.
        :keyword bool no_echo: Whether the message needs to echo to sender. Default is False.
        """

    async def send_to_group(
        self,
        group_name: str,
        content: Union[str, memoryview, Dict[str, Any]],
        data_type: Union[WebPubSubDataType, str],
        **kwargs: Any,
    ) -> None:
        """Send message to group.
        :param group_name: The group name. Required.
        :type group_name: str.
        :param content: The data content. Required.
        :type content: Union[str, memoryview, Dict[str, Any]].
        :param data_type: The data type. Required.
        :type data_type: ~azure.messaging.webpubsubclient.models.WebPubSubDataType or str.
        :keyword bool ack: If False, the message won't contains ackId and no AckMessage
         will be returned from the service. Default is True.
        :keyword bool no_echo: Whether the message needs to echo to sender. Default is False.
        """

        async def send_to_group_attempt():
            ack = kwargs.pop("ack", True)
            no_echo = kwargs.pop("no_echo", False)
            if ack:
                await self._send_message_with_ack_id(
                    message_provider=lambda id: SendToGroupMessage(
                        group=group_name,
                        data_type=data_type,
                        data=content,
                        ack_id=id,
                        no_echo=no_echo,
                    ),
                    **kwargs,
                )
            else:
                await self._send_message(
                    message=SendToGroupMessage(
                        group=group_name,
                        data_type=data_type,
                        data=content,
                        no_echo=no_echo,
                    ),
                    **kwargs,
                )

        await self._retry(send_to_group_attempt)

    async def _retry(self, func: Callable[[], Awaitable[None]]):
        retry_attempt = 0
        while True:
            try:
                await func()
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
                await asyncio.sleep(delay_seconds)

    def _call_back(self, callback_type: Union[CallbackType, str], *args):
        for func in self._handler[callback_type]:
            asyncio.create_task(func(*args))

    async def _start_from_restarting(self):
        if self._state != WebPubSubClientState.DISCONNECTED:
            _LOGGER.warning("Client can be only restarted when it's Disconnected")
            return

        try:
            await self._start_core()
        except Exception as e:
            self._state = WebPubSubClientState.DISCONNECTED
            raise e

    async def _handle_auto_reconnect(self):
        _LOGGER.debug("start auto reconnect")
        success = False
        attempt = 0
        while not self._is_stopping:
            try:
                await self._start_from_restarting()
                success = True
                break
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.warning("An attempt to reconnect connection failed %s", e)
                attempt = attempt + 1
                delay_seconds = self._reconnect_retry_policy.next_retry_delay(attempt)
                if not delay_seconds:
                    break
                _LOGGER.debug("Delay time for reconnect attempt %d: %ds", attempt, delay_seconds)
                await asyncio.sleep(delay_seconds)
        if not success:
            await self._handle_connection_stopped()
        else:
            _LOGGER.debug("reconnect successfully")

    async def _handle_connection_stopped(self):
        _LOGGER.debug("Connection stopped")
        self._is_stopping = False
        self._state = WebPubSubClientState.STOPPED
        self._call_back(CallbackType.STOPPED)

    async def _handle_connection_close_and_no_recovery(self):
        _LOGGER.debug("Connection closed and no recovery")
        self._state = WebPubSubClientState.DISCONNECTED
        self._call_back(
            CallbackType.DISCONNECTED,
            OnDisconnectedArgs(
                connection_id=self._connection_id,
                message=self._last_disconnected_message.message if self._last_disconnected_message else None,
            ),
        )
        if self._auto_reconnect:
            await self._handle_auto_reconnect()
        else:
            await self._handle_connection_stopped()

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

    def _is_connected(self) -> bool:
        """check whether the client is still connected to server after open

        :return: True if the client is connected to server, otherwise False
        :rtype: bool
        """
        return self._state == WebPubSubClientState.CONNECTED and not self._ws.closed

    async def _rejoin_group(self, group_name: str):
        async def _rejoin_group():
            try:
                await self._join_group_core(group_name)
                _LOGGER.debug("rejoin group %s successfully", group_name)
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.debug("fail to rejoin group %s", group_name)
                self._call_back(
                    CallbackType.REJOIN_GROUP_FAILED,
                    OnRejoinGroupFailedArgs(group=group_name, error=e),
                )

        await _rejoin_group()
    @staticmethod
    def _cancel_task(task: Optional[asyncio.Task]) -> None:
        if task and not task.done():
            task.cancel()

    async def _connect(self, url: str):  # pylint: disable=too-many-statements
        async def on_close(close_status_code: int, close_msg: Optional[str]=None):
            if self._state == WebPubSubClientState.CONNECTED:
                _LOGGER.info(
                    "WebSocket connection closed. Code: %s, Reason: %s",
                    close_status_code,
                    close_msg,
                )

                self._last_close_event = CloseEvent(close_status_code=close_status_code, close_reason=close_msg)
                # clean ack cache
                await self._ack_map.clear()

                if self._is_stopping:
                    _LOGGER.warning("The client is stopping state. Stop recovery.")
                    await self._handle_connection_close_and_no_recovery()
                    return

                if self._last_close_event and self._last_close_event.close_status_code == 1008:
                    _LOGGER.warning("The websocket close with status code 1008. Stop recovery.")
                    await self._handle_connection_close_and_no_recovery()
                    return

                if not self._protocol.is_reliable_sub_protocol:
                    _LOGGER.warning("The protocol is not reliable, recovery is not applicable")
                    await self._handle_connection_close_and_no_recovery()
                    return

                recovery_url = self._build_recovery_url()
                if not recovery_url:
                    _LOGGER.warning("Connection id or reconnection token is not available")
                    await self._handle_connection_close_and_no_recovery()
                    return

                self._state = WebPubSubClientState.RECOVERING
                recovery_start = time.time()
                while (time.time() - recovery_start < _RECOVERY_TIMEOUT) and not self._is_stopping:
                    try:
                        await self._connect(recovery_url)
                        _LOGGER.debug("Recovery succeeded")
                        return
                    except:  # pylint: disable=bare-except
                        _LOGGER.debug("Try to recover after %d seconds", _RECOVERY_RETRY_INTERVAL)
                        await asyncio.sleep(_RECOVERY_RETRY_INTERVAL)

                _LOGGER.warning("Recovery attempts failed after 30 seconds or the client is stopping")
                await self._handle_connection_close_and_no_recovery()
 
        async def on_message(data: str):
            async def handle_ack_message(message: AckMessage):
                ack_option = await self._ack_map.get(message.ack_id)
                if ack_option:
                    if not (message.success or (message.error and message.error.name == "Duplicate")):
                        ack_option.error_detail = message.error
                    else:
                        ack_option.error_detail = None
                    ack_option.ack_id = message.ack_id
                    _LOGGER.debug("Ack message received. Ack id is : %d", message.ack_id)
                    ack_option.event.set()

            async def handle_connected_message(message: ConnectedMessage):
                _LOGGER.debug("WebSocket is connected with id: %s", message.connection_id)
                self._connection_id = message.connection_id
                self._reconnection_token = message.reconnection_token

                if not self._is_initial_connected:
                    self._is_initial_connected = True
                    if self._auto_rejoin_groups:
                        async with self._group_map_lock:
                            for group_name, group in self._group_map.items():
                                if group.is_joined:
                                    asyncio.create_task(self._rejoin_group(group_name))

                    self._call_back(
                        CallbackType.CONNECTED,
                        OnConnectedArgs(connection_id=message.connection_id, user_id=message.user_id),
                    )

            async def handle_disconnected_message(message: DisconnectedMessage):
                self._last_disconnected_message = message

            async def handle_group_data_message(message: GroupDataMessage):
                if message.sequence_id:
                    if not self._sequence_id.try_update(message.sequence_id):
                        # // drop duplicated message
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

            async def handle_server_data_message(message: ServerDataMessage):
                if message.sequence_id:
                    if not self._sequence_id.try_update(message.sequence_id):
                        # // drop duplicated message
                        return

                self._call_back(
                    CallbackType.SERVER_MESSAGE,
                    OnServerDataMessageArgs(
                        data_type=message.data_type,
                        data=message.data,
                        sequence_id=message.sequence_id,
                    ),
                )

            parsed_message = self._protocol.parse_messages(data)
            if parsed_message is None:
                #  None means the message is not recognized.
                return
            if parsed_message.kind == "connected":
                await handle_connected_message(parsed_message)
            elif parsed_message.kind == "disconnected":
                await handle_disconnected_message(parsed_message)
            elif parsed_message.kind == "ack":
                await handle_ack_message(parsed_message)
            elif parsed_message.kind == "groupData":
                await handle_group_data_message(parsed_message)
            elif parsed_message.kind == "serverData":
                await handle_server_data_message(parsed_message)
            else:
                _LOGGER.warning("unknown message type: %s", parsed_message.kind)

        async def _listen():
            while self._is_connected():
                msg: aiohttp.WSMessage = await self._ws.receive()
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await on_message(msg.data)
                elif msg.type == aiohttp.WSMsgType.CLOSING:
                    _LOGGER.debug("WebSocket is closing")
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    _LOGGER.debug("WebSocket is closed")
                elif msg.type == aiohttp.WSMsgType.CLOSE:
                    await on_close(msg.data, msg.extra)
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    await on_close(1008, "unexpected WebSocket error")
                    break
                else:
                    _LOGGER.debug("Unknown message: %s", msg)
                
        async def on_open():
            try:
                await self._ws.connect()
            except aiohttp.ClientConnectorError as e:
                raise OpenClientError("Fail to open client") from e

            _LOGGER.debug("WebSocket connection has opened")
            self._state = WebPubSubClientState.CONNECTED
            self._cancel_task(self._task_listen)
            self._task_listen = asyncio.create_task(_listen())

        if self._is_stopping:
            raise OpenClientError("Can't open a client during closing")

        self._ws = WebSocketAppAsync(
            url=url,
            on_open=on_open,
            on_message=on_message,
            on_close=on_close,
            subprotocols=[self._protocol.name] if self._protocol else [],
            header={_USER_AGENT: format_user_agent(self._user_agent)},
        )
        await self._ws.run_forever()

        _LOGGER.debug("WebSocket connection has opened")

        # set coroutine to check sequence id if needed
        if self._protocol.is_reliable_sub_protocol:
            async def sequence_id_ack_periodically():
                while self._is_connected():
                    try:
                        is_updated, seq_id = self._sequence_id.try_get_sequence_id()
                        if is_updated and seq_id is not None:
                            await self._send_message(SequenceAckMessage(sequence_id=seq_id))
                    finally:
                        await asyncio.sleep(1.0)

            self._cancel_task(self._task_seq_ack)
            self._task_seq_ack = asyncio.create_task(sequence_id_ack_periodically())

        _LOGGER.info("connected successfully")

    async def _start_core(self):
        self._state = WebPubSubClientState.CONNECTING
        _LOGGER.info("Staring a new connection")

        # Reset before a pure new connection
        self._sequence_id.reset()
        self._is_initial_connected = False
        self._last_close_event = None
        self._last_disconnected_message = None
        self._connection_id = None
        self._reconnection_token = None
        self._url = None

        self._url = self._credential.get_client_access_url()
        await self._connect(self._url)

    async def open(self) -> None:
        """open the client and connect to service"""

        if self._is_stopping:
            raise OpenClientError("Can't open a client during stopping")
        if self._state != WebPubSubClientState.STOPPED:
            raise OpenClientError("Client can be only started when it's Stopped")

        try:
            await self._start_core()
        except Exception as e:
            self._state = WebPubSubClientState.STOPPED
            self._is_stopping = False
            raise e

    async def close(self) -> None:
        """close the client"""

        if self._state == WebPubSubClientState.STOPPED or self._is_stopping:
            return
        self._is_stopping = True

        await self._ws.close()
        for item in [self._task_listen, self._task_seq_ack]:
            self._cancel_task(item)
        _LOGGER.info("close client successfully")

    @overload
    def subscribe(
        self,
        event: Union[Literal[CallbackType.CONNECTED], str],
        listener: Callable[[OnConnectedArgs], Awaitable[None]],
    ) -> None:
        """Add handler for connected event.
        :param event: The event name. Required.
        :type event: str or ~azure.messaging.webpubsubclient.models.CallbackType.CONNECTED
        :param listener: The handler to add which must be awaitable
        :type listener: callable.
        """

    @overload
    def subscribe(
        self,
        event: Union[Literal[CallbackType.DISCONNECTED], str],
        listener: Callable[[OnDisconnectedArgs], Awaitable[None]],
    ) -> None:
        """Add handler for disconnected event.
        :param event: The event name. Required.
        :type event: str or ~azure.messaging.webpubsubclient.models.CallbackType.DISCONNECTED
        :param listener: The handler to add which must be awaitable
        :type listener: callable.
        """

    @overload
    def subscribe(self, event: Literal[CallbackType.STOPPED], listener: Callable[[], None]) -> None:
        """Add handler for stopped event.
        :param event: The event name. Required.
        :type event: str
        :param listener: The handler to add which must be awaitable
        :type listener: callable.
        """

    @overload
    def subscribe(
        self,
        event: Union[Literal[CallbackType.SERVER_MESSAGE], str],
        listener: Callable[[OnServerDataMessageArgs], Awaitable[None]],
    ) -> None:
        """Add handler for server messages.
        :param event: The event name. Required.
        :type event: str or ~azure.messaging.webpubsubclient.models.CallbackType.SERVER_MESSAGE
        :param listener: The handler to add which must be awaitable
        :type listener: callable.
        """

    @overload
    def subscribe(
        self,
        event: Union[Literal[CallbackType.GROUP_MESSAGE], str],
        listener: Callable[[OnGroupDataMessageArgs], Awaitable[None]],
    ) -> None:
        """Add handler for group messages.
        :param event: The event name. Required.
        :type event: str or ~azure.messaging.webpubsubclient.models.CallbackType.GROUP_MESSAGE
        :param listener: The handler to add which must be awaitable
        :type listener: callable.
        """

    @overload
    def subscribe(
        self,
        event: Union[Literal[CallbackType.REJOIN_GROUP_FAILED], str],
        listener: Callable[[OnRejoinGroupFailedArgs], Awaitable[None]],
    ) -> None:
        """Add handler for rejoining group failed.
        :param event: The event name. Required.
        :type event: str or ~azure.messaging.webpubsubclient.models.CallbackType.REJOIN_GROUP_FAILED
        :param listener: The handler to add which must be awaitable
        :type listener: callable.
        """

    def subscribe(
        self,
        event: Union[CallbackType, str],
        listener: Callable,
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Add handler.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType or str
        :param listener: The handler to add which must be awaitable
        :type listener: callable.
        """
        if inspect.isawaitable(listener):
            raise TypeError("listener should be awaitable.")
        if event in self._handler:
            self._handler[event].append(listener)
        else:
            _LOGGER.error("wrong event type: %s", event)

    @overload
    def unsubscribe(
        self,
        event: Union[Literal[CallbackType.CONNECTED], str],
        listener: Callable[[OnConnectedArgs], Awaitable[None]],
    ) -> None:
        """Remove handler for connected event.
        :param event: The event name. Required.
        :type event: str or ~azure.messaging.webpubsubclient.models.CallbackType.CONNECTED
        :param listener: The handler to remove
        :type listener: callable.
        """

    @overload
    def unsubscribe(
        self,
        event: Union[Literal[CallbackType.DISCONNECTED], str],
        listener: Callable[[OnDisconnectedArgs], Awaitable[None]],
    ) -> None:
        """Remove handler for connected event.
        :param event: The event name. Required.
        :type event: str or ~azure.messaging.webpubsubclient.models.CallbackType.DISCONNECTED
        :param listener: The handler to remove
        :type listener: callable.
        """

    @overload
    def unsubscribe(self, event: Union[Literal[CallbackType.STOPPED], str], listener: Callable[[], None]) -> None:
        """Remove handler for stopped event.
        :param event: The event name. Required.
        :type event: str or ~azure.messaging.webpubsubclient.models.CallbackType.STOPPED
        :param listener: The handler to remove
        :type listener: callable.
        """

    @overload
    def unsubscribe(
        self,
        event: Union[Literal[CallbackType.SERVER_MESSAGE], str],
        listener: Callable[[OnServerDataMessageArgs], Awaitable[None]],
    ) -> None:
        """Remove handler for server message.
        :param event: The event name. Required.
        :type event: str or ~azure.messaging.webpubsubclient.models.CallbackType.SERVER_MESSAGE
        :param listener: The handler to remove
        :type listener: callable.
        """

    @overload
    def unsubscribe(
        self,
        event: Union[Literal[CallbackType.GROUP_MESSAGE], str],
        listener: Callable[[OnGroupDataMessageArgs], Awaitable[None]],
    ) -> None:
        """Remove handler for group message.
        :param event: The event name. Required.
        :type event: str or ~azure.messaging.webpubsubclient.models.CallbackType.GROUP_MESSAGE
        :param listener: The handler to remove
        :type listener: callable.
        """

    @overload
    def unsubscribe(
        self,
        event: Union[Literal[CallbackType.REJOIN_GROUP_FAILED], str],
        listener: Callable[[OnRejoinGroupFailedArgs], Awaitable[None]],
    ) -> None:
        """Remove handler for rejoining group failed.
        :param event: The event name. Required.
        :type event: str or ~azure.messaging.webpubsubclient.models.CallbackType.REJOIN_GROUP_FAILED
        :param listener: The handler to remove
        :type listener: callable.
        """

    def unsubscribe(
        self,
        event: Union[CallbackType, str],
        listener: Callable,
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Remove handler for rejoining group failed.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType or str
        :param listener: The handler to remove
        :type listener: callable.
        """
        if event in self._handler:
            if listener in self._handler[event]:
                self._handler[event].remove(listener)
            else:
                _LOGGER.info("target listener does not exist")
        else:
            _LOGGER.error("wrong event type: %s", event)

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # pylint: disable=unused-argument
        await self.close()

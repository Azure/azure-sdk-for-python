# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
# pylint: disable=client-method-missing-tracing-decorator-async,too-many-lines,networking-import-outside-azure-core-transport
import asyncio
import inspect
from typing import (
    Any,
    overload,
    Callable,
    Union,
    Optional,
    Dict,
    List,
    Literal,
    Awaitable,
    Coroutine,
)
import time
import uuid
import logging
import aiohttp
from azure.core.pipeline.policies import RetryMode

from ..models._models import (
    OnConnectedArgs,
    OnDisconnectedArgs,
    OnServerDataMessageArgs,
    OnGroupDataMessageArgs,
    WebPubSubGroup,
    SendMessageErrorOptionsAsync,
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
    AckMapAsync,
    OpenClientError,
    ReconnectError,
    RecoverError,
)
from ..models._enums import (
    WebPubSubDataType,
    WebPubSubClientState,
    CallbackType,
    WebPubSubProtocolType,
)
from .._client import (
    WebPubSubClientBase,
    WebSocketAppBase,
    _RETRY_TOTAL,
    _RETRY_BACKOFF_FACTOR,
    _RETRY_BACKOFF_MAX,
    _RECOVERY_TIMEOUT,
    _RECOVERY_RETRY_INTERVAL,
    _USER_AGENT,
    _ACK_TIMEOUT,
    _START_TIMEOUT,
    _QUEUE_MAX_SIZE,
)
from .._util import format_user_agent, raise_for_empty_message_ack

_LOGGER = logging.getLogger(__name__)


class WebSocketAppAsync(WebSocketAppBase):  # pylint: disable=too-many-instance-attributes
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
        super().__init__(reconnect_tried_times, recover_start_time)
        self.url = url
        self.on_open = on_open
        self.on_message = on_message
        self.on_close = on_close
        self.on_error = on_error
        self.subprotocols = subprotocols
        self.header = header
        self.event = asyncio.Event()
        self.session: Optional[aiohttp.ClientSession] = None
        self.sock: Optional[aiohttp.client.ClientWebSocketResponse] = None
        self.keep_running = False

    async def send(self, message: str) -> None:
        await self.sock.send_str(message)  # type: ignore

    async def run_forever(self):
        try:
            self.session = aiohttp.ClientSession()
            self.sock = await self.session.ws_connect(self.url, protocols=self.subprotocols, headers=self.header)
        except Exception as e:  # pylint: disable=broad-except
            await self.on_error(self, e)
            await self.session_close()
            self.event.set()
            return
        await self.on_open()
        self.event.set()

        self.keep_running = True
        while self.keep_running:
            msg: aiohttp.WSMessage = await self.sock.receive()  # type: ignore
            if msg.type == aiohttp.WSMsgType.TEXT:
                await self.on_message(msg.data)
            elif msg.type == aiohttp.WSMsgType.CLOSING:
                _LOGGER.debug("WebSocket is closing")
            elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSE):
                _LOGGER.debug("WebSocket is closed")
                await self.on_close(self, msg.data, msg.extra)
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                sock_error = self.sock.exception()
                error_message = getattr(sock_error, "message", str(sock_error))
                _LOGGER.warning("WebSocket error: %s", sock_error)
                if isinstance(sock_error, aiohttp.WebSocketError):
                    await self.on_error(self, sock_error.code, error_message)
                else:
                    await self.on_close(self, 1008, error_message)
                break
            else:
                _LOGGER.debug("Unknown message: %s", msg)

        self.keep_running = False
        await self.session_close()

    async def connect(self):
        self.session = aiohttp.ClientSession()
        self.sock = await self.session.ws_connect(self.url, protocols=self.subprotocols, headers=self.header)

    async def session_close(self):
        try:
            if self.session and not self.session.closed:
                await self.session.close()
        except Exception as e:  # pylint: disable=broad-except
            _LOGGER.warning("Fail to close session: %s", e)

    async def close(self):
        try:
            await self.sock.close()
        except Exception as e:  # pylint: disable=broad-except
            _LOGGER.warning("Fail to close websocket connection: %s", e)
        finally:
            await self.session_close()
        self.keep_running = False

    @property
    def closed(self):
        return not self.sock or self.sock.closed


class WebPubSubClientCredential:
    def __init__(self, client_access_url_provider: Union[str, Callable[[], Coroutine[Any, Any, str]]]) -> None:
        """
        Webpubsub client credential.

        :param client_access_url_provider: Client access url. If it's awaitable callable, it will be called to
         get the url. If it's str, it will be used directly. Please note that if you provide str, the
         connection will be closed and can't be reconnected once it is expired.
        :type client_access_url_provider: str or awaitable Callable
        """
        if isinstance(client_access_url_provider, str):

            async def client_access_url_provider_func() -> str:
                return client_access_url_provider

            self._client_access_url_provider = client_access_url_provider_func
        else:
            self._client_access_url_provider = client_access_url_provider

    async def get_client_access_url(self) -> str:
        """Get client access url.
        :return: Client access url.
        :rtype: str
        """
        return await self._client_access_url_provider()


class WebPubSubClient(
    WebPubSubClientBase
):  # pylint: disable=client-accepts-api-version-keyword,too-many-instance-attributes
    """WebPubSubClient

    :param credential: The url to connect or credential to use when connecting. Required.
    :type credential: str or ~azure.messaging.webpubsubclient.aio.WebPubSubClientCredential
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
        self._ack_map: AckMapAsync = AckMapAsync()
        self._ws: Optional[WebSocketAppAsync] = None
        self._event: asyncio.Event = asyncio.Event()
        self._task_seq_ack: Optional[asyncio.Task] = None
        self._task_run_forever: Optional[asyncio.Task] = None
        self._tasks: List[asyncio.Task] = []

    def _record_task(self, task: asyncio.Task) -> None:
        if len(self._tasks) > _QUEUE_MAX_SIZE:
            self._tasks = [t for t in self._tasks if not t.done()]
        self._tasks.append(task)

    def _next_ack_id(self) -> int:
        self._ack_id = self._ack_id + 1
        return self._ack_id

    async def _send_message(self, message: WebPubSubMessage, **kwargs: Any) -> None:
        pay_load = self._protocol.write_message(message)
        if self._ws.closed:  # type: ignore
            raise SendMessageError("The websocket connection is not connected.")

        await self._ws.send(pay_load)  # type: ignore
        if kwargs.pop("logging_enable", False) or self._logging_enable:
            _LOGGER.debug("\nconnection_id: %s\npay_load: %s", self._connection_id, pay_load)

    async def _send_message_with_ack_id(
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
                SendMessageErrorOptionsAsync(
                    error_detail=AckMessageError(name="", message="Timeout while waiting for ack message.")
                ),
            )
        try:
            await self._send_message(message, **kwargs)
        except Exception as e:
            self._ack_map.pop(ack_id)
            raise e

        message_ack = self._ack_map.get(ack_id)
        raise_for_empty_message_ack(message_ack, ack_id)

        _LOGGER.debug("wait for ack message with ackId: %s", ack_id)
        if message_ack:
            await asyncio.wait_for(message_ack.event.wait(), timeout=self._ack_timeout)
            raise_for_empty_message_ack(self._ack_map.pop(ack_id))
            if message_ack.error_detail is not None:
                raise SendMessageError(
                    message="Failed to send message.",
                    ack_id=message_ack.ack_id,
                    error_detail=message_ack.error_detail,
                )

    def _get_or_add_group(self, name: str) -> WebPubSubGroup:
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
            group = self._get_or_add_group(group_name)
            await self._join_group_core(group_name, **kwargs)
            group.is_joined = True

        await self._retry(join_group_attempt)

    async def _join_group_core(self, group_name: str, **kwargs: Any) -> None:
        ack_id = kwargs.pop("ack_id", None)
        await self._send_message_with_ack_id(
            message=JoinGroupMessage(group=group_name, ack_id=ack_id),
            **kwargs,
        )

    async def leave_group(self, group_name: str, **kwargs: Any) -> None:
        """Leave the client from group
        :param group_name: The group name. Required.
        :type group_name: str.
        :keyword int ack_id: The optional ackId. If not specified, client will generate one.
        """

        async def leave_group_attempt():
            group = self._get_or_add_group(group_name)
            ack_id = kwargs.pop("ack_id", None)
            await self._send_message_with_ack_id(
                message=LeaveGroupMessage(group=group_name, ack_id=ack_id),
                **kwargs,
            )
            group.is_joined = False

        await self._retry(leave_group_attempt)

    @overload
    async def send_event(
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
    async def send_event(
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
    async def send_event(
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

    async def send_event(
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

        async def send_event_attempt():
            ack = kwargs.pop("ack", True)
            ack_id = kwargs.pop("ack_id", None)
            if ack:
                await self._send_message_with_ack_id(
                    message=SendEventMessage(data_type=data_type, data=content, ack_id=ack_id, event=event_name),
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
    async def send_to_group(
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
    async def send_to_group(
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

    async def send_to_group(
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

        async def send_to_group_attempt():
            ack = kwargs.pop("ack", True)
            no_echo = kwargs.pop("no_echo", False)
            ack_id = kwargs.pop("ack_id", None)
            if ack:
                await self._send_message_with_ack_id(
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

    def _call_back(self, callback_type: CallbackType, *args):
        for func in self._handler[callback_type]:
            self._record_task(asyncio.create_task(func(*args)))

    async def _start_from_restarting(self, reconnect_tried_times: Optional[int] = None):
        if self._state != WebPubSubClientState.DISCONNECTED:
            _LOGGER.warning("Client can be only restarted when it's Disconnected")
            return

        try:
            await self._start_core(reconnect_tried_times)
        except Exception as e:
            self._state = WebPubSubClientState.DISCONNECTED
            raise e

    async def _handle_auto_reconnect(self, reconnect_tried_times: Optional[int] = None):
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
                    await asyncio.sleep(delay_seconds)
                await self._start_from_restarting(attempt)
                if self._ws:
                    self._ws.clear_reconnect_recover()
                success = True
                break
            except ReconnectError:
                _LOGGER.debug("Failed to reconnect, and will retry in another task")
                break
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.warning("An attempt to reconnect connection failed: %s", e)
        if not success:
            await self._handle_connection_stopped()
        else:
            _LOGGER.debug("reconnect successfully")

    async def _handle_connection_stopped(self):
        _LOGGER.debug("Connection stopped")
        self._is_stopping = False
        self._state = WebPubSubClientState.STOPPED
        self._call_back(CallbackType.STOPPED)

    async def _handle_connection_close_and_no_recovery(self, reconnect_tried_times: Optional[int] = None):
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
            await self._handle_auto_reconnect(reconnect_tried_times)
        else:
            await self._handle_connection_stopped()

    def is_connected(self) -> bool:
        """check whether the client is still connected to server after open

        :return: True if the client is connected to server, otherwise False
        :rtype: bool
        """
        return self._state == WebPubSubClientState.CONNECTED and self._ws and not self._ws.closed  # type: ignore

    async def _rejoin_group(self, group_name: str):
        try:
            await self._join_group_core(group_name)
            _LOGGER.debug("rejoin group %s successfully", group_name)
        except Exception as e:  # pylint: disable=broad-except
            _LOGGER.debug("fail to rejoin group %s", group_name)
            self._call_back(
                CallbackType.REJOIN_GROUP_FAILED,
                OnRejoinGroupFailedArgs(group=group_name, error=e),
            )

    async def _connect(
        self,
        url: str,
        reconnect_tried_times: Optional[int] = None,
        recover_start_time: Optional[float] = None,
    ):  # pylint: disable=too-many-statements
        async def on_open():
            if self._is_stopping:
                try:
                    if self._ws:
                        await self._ws.close()
                finally:
                    raise OpenClientError("Can't open a client during stopping")

            _LOGGER.debug("WebSocket connection has opened")
            self._state = WebPubSubClientState.CONNECTED

        async def on_message(data: str):
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
                        for group_name, group in self._group_map.items():
                            if group.is_joined:
                                self._record_task(asyncio.create_task(self._rejoin_group(group_name)))

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
                    ack_option.event.set()
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

        async def on_close(
            ws_instance: WebSocketAppAsync,
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
                    _LOGGER.warning("The client is stopping state. Stop recovery.")
                    await self._handle_connection_close_and_no_recovery(ws_instance.reconnect_tried_times)
                    return

                if self._last_close_event and self._last_close_event.close_status_code == 1008:
                    _LOGGER.warning("The websocket close with status code 1008. Stop recovery.")
                    await self._handle_connection_close_and_no_recovery(ws_instance.reconnect_tried_times)
                    return

                if not self._protocol.is_reliable_sub_protocol:
                    _LOGGER.warning("The protocol is not reliable, recovery is not applicable")
                    await self._handle_connection_close_and_no_recovery(ws_instance.reconnect_tried_times)
                    return

                recovery_url = self._build_recovery_url()
                if not recovery_url:
                    _LOGGER.warning("Connection id or reconnection token is not available")
                    await self._handle_connection_close_and_no_recovery(ws_instance.reconnect_tried_times)
                    return

                self._state = WebPubSubClientState.RECOVERING
                recovery_start = (
                    time.time() if ws_instance.recover_start_time is None else ws_instance.recover_start_time
                )
                first_time = True
                while (time.time() - recovery_start < _RECOVERY_TIMEOUT) and not self._is_stopping:
                    try:
                        if ws_instance.recover_start_time is not None or not first_time:
                            await asyncio.sleep(_RECOVERY_RETRY_INTERVAL)
                        await self._connect(recovery_url, None, recovery_start)
                        if self._ws:
                            self._ws.clear_reconnect_recover()
                        _LOGGER.debug("Recovery succeeded")
                        return
                    except RecoverError:
                        _LOGGER.debug("Fail to recover, and will try in another task")
                        return
                    except Exception as e:  # pylint: disable=broad-except
                        first_time = False
                        _LOGGER.debug("Fail to recover: %s", e)
                        _LOGGER.debug("Try to recover after %d seconds", _RECOVERY_RETRY_INTERVAL)

                _LOGGER.warning("Recovery attempts failed after 30 seconds or the client is stopping")
                await self._handle_connection_close_and_no_recovery(ws_instance.reconnect_tried_times)
            else:
                if close_status_code or close_msg:
                    ws_instance.close_event = CloseEvent(close_status_code=close_status_code, close_reason=close_msg)
                ws_instance.event.set()

        async def on_error(ws_instance: WebSocketAppAsync, error: Exception):
            _LOGGER.warning("An error occurred when trying to connect: %s", error)
            ws_instance.error_happened = error

        if self._is_stopping:
            raise OpenClientError("Can't open a client during closing")
        await self._wait_for_tasks([self._task_seq_ack])

        self._ws = WebSocketAppAsync(
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
        task_name = f"run_forever_{uuid.uuid4()}"
        self._task_run_forever = asyncio.create_task(self._ws.run_forever(), name=task_name)
        _LOGGER.debug("create task %s successfully", task_name)
        start_time = time.time()
        try:
            await asyncio.wait_for(self._ws.event.wait(), timeout=self._start_timeout)
        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout when waiting for connection")
        finally:
            cost_time = time.time() - start_time
            if not self.is_connected():
                if not self._task_run_forever.done():
                    if reconnect_tried_times is not None:
                        raise ReconnectError("Failed to reconnect after waiting")
                    if recover_start_time is not None:
                        raise RecoverError("Failed to recover after waiting")
                raise OpenClientError(
                    " ".join(self._error_info(cost_time, self._ws.error_happened, self._ws.close_event))
                )

        # set coroutine to check sequence id if needed
        if self._protocol.is_reliable_sub_protocol:

            async def sequence_id_ack_periodically():
                while self.is_connected():
                    try:
                        is_updated, seq_id = self._sequence_id.try_get_sequence_id()
                        if is_updated and seq_id is not None:
                            await self._send_message(SequenceAckMessage(sequence_id=seq_id))
                    finally:
                        await asyncio.sleep(1.0)

            self._task_seq_ack = asyncio.create_task(
                sequence_id_ack_periodically(), name="sequence_id_ack_periodically"
            )

        _LOGGER.info("connected successfully")

    async def _start_core(self, reconnect_tried_times: Optional[int] = None):
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
        self._tasks.clear()

        self._url = await self._credential.get_client_access_url()
        await self._connect(self._url, reconnect_tried_times)

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
            _LOGGER.info("client has been closed or is stopping")
            return
        self._is_stopping = True
        old_tasks = [self._task_run_forever, self._task_seq_ack] + self._tasks

        await self._ws.close()  # type: ignore
        _LOGGER.info("waiting for close")
        await self._wait_for_tasks(old_tasks)
        if self._is_stopping and self._ws and self._ws.on_close:
            # have to manually trigger on_close
            _LOGGER.debug("manually trigger on_close")
            await self._ws.on_close(self._ws, None, None)  # type: ignore
        _LOGGER.info("close client successfully")

    @staticmethod
    async def _wait_for_tasks(tasks: List[Optional[asyncio.Task]]) -> None:
        async def task_with_timeout(task: asyncio.Task):
            try:
                await asyncio.wait_for(task, timeout=1.0)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.warning("Task %s is not done after 1s, cancel it", task.get_name())

        await asyncio.gather(*[task_with_timeout(t) for t in tasks if t and not t.done()])

    @overload
    async def subscribe(
        self,
        event: Literal[CallbackType.CONNECTED],
        listener: Callable[[OnConnectedArgs], Awaitable[None]],
    ) -> None:
        """Add handler for connected event.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.CONNECTED
        :param listener: The handler to add which must be awaitable
        :type listener: callable.
        """

    @overload
    async def subscribe(
        self,
        event: Literal[CallbackType.DISCONNECTED],
        listener: Callable[[OnDisconnectedArgs], Awaitable[None]],
    ) -> None:
        """Add handler for disconnected event.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.DISCONNECTED
        :param listener: The handler to add which must be awaitable
        :type listener: callable.
        """

    @overload
    async def subscribe(
        self,
        event: Literal[CallbackType.STOPPED],
        listener: Callable[[], Awaitable[None]],
    ) -> None:
        """Add handler for stopped event.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.STOPPED
        :param listener: The handler to add which must be awaitable
        :type listener: callable.
        """

    @overload
    async def subscribe(
        self,
        event: Literal[CallbackType.SERVER_MESSAGE],
        listener: Callable[[OnServerDataMessageArgs], Awaitable[None]],
    ) -> None:
        """Add handler for server messages.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.SERVER_MESSAGE
        :param listener: The handler to add which must be awaitable
        :type listener: callable.
        """

    @overload
    async def subscribe(
        self,
        event: Literal[CallbackType.GROUP_MESSAGE],
        listener: Callable[[OnGroupDataMessageArgs], Awaitable[None]],
    ) -> None:
        """Add handler for group messages.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.GROUP_MESSAGE
        :param listener: The handler to add which must be awaitable
        :type listener: callable.
        """

    @overload
    async def subscribe(
        self,
        event: Literal[CallbackType.REJOIN_GROUP_FAILED],
        listener: Callable[[OnRejoinGroupFailedArgs], Awaitable[None]],
    ) -> None:
        """Add handler for rejoining group failed.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.REJOIN_GROUP_FAILED
         or Literal["rejoin-group-failed"]
        :param listener: The handler to add which must be awaitable
        :type listener: callable.
        """

    async def subscribe(
        self,
        event: CallbackType,
        listener: Callable,
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Add handler.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType
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
    async def unsubscribe(
        self,
        event: Literal[CallbackType.CONNECTED],
        listener: Callable[[OnConnectedArgs], Awaitable[None]],
    ) -> None:
        """Remove handler for connected event.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.CONNECTED
        :param listener: The handler to remove
        :type listener: callable.
        """

    @overload
    async def unsubscribe(
        self,
        event: Literal[CallbackType.DISCONNECTED],
        listener: Callable[[OnDisconnectedArgs], Awaitable[None]],
    ) -> None:
        """Remove handler for connected event.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.DISCONNECTED
        :param listener: The handler to remove
        :type listener: callable.
        """

    @overload
    async def unsubscribe(
        self,
        event: Literal[CallbackType.STOPPED],
        listener: Callable[[], Awaitable[None]],
    ) -> None:
        """Remove handler for stopped event.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.STOPPED
        :param listener: The handler to remove
        :type listener: callable.
        """

    @overload
    async def unsubscribe(
        self,
        event: Literal[CallbackType.SERVER_MESSAGE],
        listener: Callable[[OnServerDataMessageArgs], Awaitable[None]],
    ) -> None:
        """Remove handler for server message.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.SERVER_MESSAGE
        :param listener: The handler to remove
        :type listener: callable.
        """

    @overload
    async def unsubscribe(
        self,
        event: Literal[CallbackType.GROUP_MESSAGE],
        listener: Callable[[OnGroupDataMessageArgs], Awaitable[None]],
    ) -> None:
        """Remove handler for group message.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.GROUP_MESSAGE
        :param listener: The handler to remove
        :type listener: callable.
        """

    @overload
    async def unsubscribe(
        self,
        event: Literal[CallbackType.REJOIN_GROUP_FAILED],
        listener: Callable[[OnRejoinGroupFailedArgs], Awaitable[None]],
    ) -> None:
        """Remove handler for rejoining group failed.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType.REJOIN_GROUP_FAILED
         or Literal["rejoin-group-failed"]
        :param listener: The handler to remove
        :type listener: callable.
        """

    async def unsubscribe(
        self,
        event: CallbackType,
        listener: Callable,
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Remove handler for rejoining group failed.
        :param event: The event name. Required.
        :type event: ~azure.messaging.webpubsubclient.models.CallbackType
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

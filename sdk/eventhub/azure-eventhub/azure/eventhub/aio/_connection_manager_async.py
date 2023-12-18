# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union
from asyncio import Lock

from .._connection_manager import _ConnectionMode
from .._constants import TransportType

if TYPE_CHECKING:
    from .._pyamqp.aio._authentication_async import JWTTokenAuthAsync
    from .._pyamqp.aio._connection_async import Connection as ConnectionAsync
    from ._transport._base_async import AmqpTransportAsync
    try:
        from uamqp.authentication import JWTTokenAsync as uamqp_JWTTokenAuthAsync
        from uamqp.async_ops import ConnectionAsync as uamqp_ConnectionAsync
    except ImportError:
        uamqp_JWTTokenAuthAsync = None
        uamqp_ConnectionAsync = None

    try:
        from typing_extensions import Protocol
    except ImportError:
        Protocol = object  # type: ignore

    class ConnectionManager(Protocol):
        async def get_connection(
            self,
            *,
            host: Optional[str] = None,
            auth: Optional[Union[uamqp_JWTTokenAuthAsync, JWTTokenAuthAsync]] = None,
            endpoint: Optional[str] = None,
        ) -> Union[ConnectionAsync, uamqp_ConnectionAsync]:
            pass

        async def close_connection(self) -> None:
            pass

        async def reset_connection_if_broken(self) -> None:
            pass


class _SharedConnectionManager:  # pylint:disable=too-many-instance-attributes
    def __init__(self, **kwargs) -> None:
        self._loop = kwargs.get("loop")
        self._lock = Lock(loop=self._loop)
        self._conn: Optional[Union[uamqp_ConnectionAsync, ConnectionAsync]] = None

        self._container_id = kwargs.get("container_id")
        self._custom_endpoint_address = kwargs.get("custom_endpoint_address")
        self._debug = kwargs.get("debug")
        self._error_policy = kwargs.get("error_policy")
        self._properties = kwargs.get("properties")
        self._encoding = kwargs.get("encoding") or "UTF-8"
        self._transport_type = kwargs.get("transport_type") or TransportType.Amqp
        self._http_proxy = kwargs.get("http_proxy")
        self._max_frame_size = kwargs.get("max_frame_size")
        self._channel_max = kwargs.get("channel_max")
        self._idle_timeout = kwargs.get("idle_timeout")
        self._remote_idle_timeout_empty_frame_send_ratio = kwargs.get("remote_idle_timeout_empty_frame_send_ratio")
        self._amqp_transport: AmqpTransportAsync = kwargs.pop("amqp_transport")

    async def get_connection(
        self,
        *,
        host: Optional[str] = None,
        auth: Optional[Union[JWTTokenAuthAsync, uamqp_JWTTokenAuthAsync]] = None,
        endpoint: Optional[str] = None,
    ) -> Union[ConnectionAsync, uamqp_ConnectionAsync]:
        async with self._lock:
            if self._conn is None:
                self._conn = self._amqp_transport.create_connection_async(
                    host=host,
                    auth=auth,
                    endpoint=endpoint,
                    custom_endpoint_address=self._custom_endpoint_address,
                    container_id=self._container_id,
                    max_frame_size=self._max_frame_size,
                    channel_max=self._channel_max,
                    idle_timeout=self._idle_timeout,
                    properties=self._properties,
                    remote_idle_timeout_empty_frame_send_ratio=self._remote_idle_timeout_empty_frame_send_ratio,
                    error_policy=self._error_policy,
                    debug=self._debug,
                    loop=self._loop,
                    encoding=self._encoding,
                )
            return self._conn

    async def close_connection(self) -> None:
        async with self._lock:
            if self._conn:
                await self._amqp_transport.close_connection_async(self._conn)
            self._conn = None

    async def reset_connection_if_broken(self) -> None:
        async with self._lock:
            conn_state = self._amqp_transport.get_connection_state(self._conn)
            if self._conn and conn_state in self._amqp_transport.CONNECTION_CLOSING_STATES:
                self._conn = None


class _SeparateConnectionManager:
    def __init__(self, **kwargs) -> None:
        pass

    async def get_connection(
        self,
        *,
        host: Optional[str] = None,
        auth: Optional[Union[JWTTokenAuthAsync, uamqp_JWTTokenAuthAsync]] = None,
        endpoint: Optional[str] = None,
    ) -> None:
        pass  # return None

    async def close_connection(self) -> None:
        pass

    async def reset_connection_if_broken(self) -> None:
        pass


def get_connection_manager(**kwargs) -> "ConnectionManager":
    connection_mode = kwargs.get("connection_mode", _ConnectionMode.SeparateConnection)  # type: ignore
    if connection_mode == _ConnectionMode.ShareConnection:
        return _SharedConnectionManager(**kwargs)
    return _SeparateConnectionManager(**kwargs)

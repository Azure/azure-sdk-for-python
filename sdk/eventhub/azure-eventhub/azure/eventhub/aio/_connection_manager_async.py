# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import TYPE_CHECKING

from uamqp import c_uamqp
from uamqp.async_ops import ConnectionAsync

from .._connection_manager import _ConnectionMode
from .._constants import TransportType

if TYPE_CHECKING:
    from uamqp.authentication import JWTTokenAsync

    try:
        from typing_extensions import Protocol
    except ImportError:
        Protocol = object  # type: ignore

    class ConnectionManager(Protocol):
        async def get_connection(
            self, host: str, auth: "JWTTokenAsync"
        ) -> ConnectionAsync:
            pass

        async def close_connection(self) -> None:
            pass

        async def reset_connection_if_broken(self) -> None:
            pass


class _SharedConnectionManager(object):  # pylint:disable=too-many-instance-attributes
    def __init__(self, **kwargs) -> None:
        self._loop = kwargs.get("loop")
        self._lock = Lock(loop=self._loop)
        self._conn = None

        self._container_id = kwargs.get("container_id")
        self._debug = kwargs.get("debug")
        self._error_policy = kwargs.get("error_policy")
        self._properties = kwargs.get("properties")
        self._encoding = kwargs.get("encoding") or "UTF-8"
        self._transport_type = kwargs.get("transport_type") or TransportType.Amqp
        self._http_proxy = kwargs.get("http_proxy")
        self._max_frame_size = kwargs.get("max_frame_size")
        self._channel_max = kwargs.get("channel_max")
        self._idle_timeout = kwargs.get("idle_timeout")
        self._remote_idle_timeout_empty_frame_send_ratio = kwargs.get(
            "remote_idle_timeout_empty_frame_send_ratio"
        )

    async def get_connection(self, host: str, auth: "JWTTokenAsync") -> ConnectionAsync:
        async with self._lock:
            if self._conn is None:
                self._conn = ConnectionAsync(
                    host,
                    auth,
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
                await self._conn.destroy_async()
            self._conn = None

    async def reset_connection_if_broken(self) -> None:
        async with self._lock:
            if self._conn and self._conn._state in (  # pylint:disable=protected-access
                c_uamqp.ConnectionState.CLOSE_RCVD,  # pylint:disable=c-extension-no-member
                c_uamqp.ConnectionState.CLOSE_SENT,  # pylint:disable=c-extension-no-member
                c_uamqp.ConnectionState.DISCARDING,  # pylint:disable=c-extension-no-member
                c_uamqp.ConnectionState.END,  # pylint:disable=c-extension-no-member
            ):
                self._conn = None


class _SeparateConnectionManager(object):
    def __init__(self, **kwargs) -> None:
        pass

    async def get_connection(self, host: str, auth: "JWTTokenAsync") -> None:
        pass  # return None

    async def close_connection(self) -> None:
        pass

    async def reset_connection_if_broken(self) -> None:
        pass


def get_connection_manager(**kwargs) -> "ConnectionManager":
    connection_mode = kwargs.get("connection_mode", _ConnectionMode.SeparateConnection)
    if connection_mode == _ConnectionMode.ShareConnection:
        return _SharedConnectionManager(**kwargs)
    return _SeparateConnectionManager(**kwargs)

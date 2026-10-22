# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Optional, Union, Any
from threading import Lock
from enum import Enum

from ._constants import TransportType

if TYPE_CHECKING:
    from ._pyamqp.authentication import JWTTokenAuth
    from ._pyamqp._connection import Connection

    try:
        from uamqp.authentication import JWTTokenAuth as uamqp_JWTTokenAuth
        from uamqp import Connection as uamqp_Connection
    except ImportError:
        uamqp_JWTTokenAuth = None
        uamqp_Connection = None
    from ._transport._base import AmqpTransport

    try:
        from typing_extensions import Protocol
    except ImportError:
        Protocol = object  # type: ignore

    class ConnectionManager(Protocol):
        def get_connection(
            self,
            *,
            endpoint: str,
            auth: Optional[Union[JWTTokenAuth, uamqp_JWTTokenAuth]] = None,
        ) -> Union[Connection, uamqp_Connection]:
            pass

        def close_connection(self):
            pass

        def reset_connection_if_broken(self):
            pass


class _ConnectionMode(Enum):
    ShareConnection = 1
    SeparateConnection = 2


class _SharedConnectionManager:  # pylint:disable=too-many-instance-attributes
    def __init__(  # pylint:disable=unused-argument
        self,
        *,
        container_id: Optional[str] = None,
        custom_endpoint_address: Optional[str] = None,
        debug: bool = False,
        error_policy: Optional[Any] = None,
        properties: Optional[Dict[str, Any]] = None,
        encoding: str = "UTF-8",
        transport_type: TransportType = TransportType.Amqp,
        http_proxy: Optional[str] = None,
        max_frame_size: int,
        channel_max: int,
        idle_timeout: Optional[float],
        remote_idle_timeout_empty_frame_send_ratio: float,
        amqp_transport: AmqpTransport,
        **kwargs: Any,
    ):
        self._lock = Lock()
        self._conn: Union[Connection, uamqp_Connection] = None

        self._container_id = container_id
        self._custom_endpoint_address = custom_endpoint_address
        self._debug = debug
        self._error_policy = error_policy
        self._properties = properties
        self._encoding = encoding
        self._transport_type = transport_type
        self._http_proxy = http_proxy
        self._max_frame_size = max_frame_size
        self._channel_max = channel_max
        self._idle_timeout = idle_timeout
        self._remote_idle_timeout_empty_frame_send_ratio = remote_idle_timeout_empty_frame_send_ratio
        self._amqp_transport: AmqpTransport = amqp_transport

    def get_connection(
        self,
        *,
        endpoint: str,
        auth: Optional[Union[JWTTokenAuth, uamqp_JWTTokenAuth]] = None,
    ) -> Union[Connection, uamqp_Connection]:
        with self._lock:
            if self._conn is None:
                self._conn = self._amqp_transport.create_connection(
                    endpoint=endpoint,
                    auth=auth,
                    custom_endpoint_address=self._custom_endpoint_address,
                    container_id=self._container_id,
                    max_frame_size=self._max_frame_size,
                    channel_max=self._channel_max,
                    idle_timeout=self._idle_timeout,
                    properties=self._properties,
                    remote_idle_timeout_empty_frame_send_ratio=self._remote_idle_timeout_empty_frame_send_ratio,
                    error_policy=self._error_policy,
                    debug=self._debug,
                    encoding=self._encoding,
                )
            return self._conn

    def close_connection(self) -> None:
        with self._lock:
            if self._conn:
                self._amqp_transport.close_connection(self._conn)
            self._conn = None

    def reset_connection_if_broken(self) -> None:
        with self._lock:
            conn_state = self._amqp_transport.get_connection_state(self._conn)
            if self._conn and conn_state in self._amqp_transport.CONNECTION_CLOSING_STATES:
                self._conn = None


class _SeparateConnectionManager:
    def __init__(self, **kwargs):
        pass

    def get_connection(  # pylint:disable=unused-argument
        self,
        *,
        endpoint: str,
        auth: Optional[Union[JWTTokenAuth, uamqp_JWTTokenAuth]] = None,
    ) -> None:
        return None

    def close_connection(self) -> None:
        pass

    def reset_connection_if_broken(self) -> None:
        pass


def get_connection_manager(**kwargs: Any) -> "ConnectionManager":
    connection_mode = kwargs.get("connection_mode", _ConnectionMode.SeparateConnection)  # type: ignore
    if connection_mode == _ConnectionMode.ShareConnection:
        return _SharedConnectionManager(**kwargs)
    return _SeparateConnectionManager(**kwargs)

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import TYPE_CHECKING, Union
from threading import Lock
from enum import Enum

from ._constants import TransportType

from ._pyamqp._connection import Connection, _CLOSING_STATES

if TYPE_CHECKING:
    try:
        from typing_extensions import Protocol
    except ImportError:
        Protocol = object  # type: ignore

    try:
        from uamqp import Connection as uamqp_Connection
        from uamqp.authentication import JWTTokenAuth as uamqp_JWTTokenAuth
    except ImportError:
        uamqp_Connection = None
        uamqp_JWTTokenAuth = None
    from ._pyamqp.authentication import JWTTokenAuth

    class ConnectionManager(Protocol):
        def get_connection(
            self, host: str, auth: Union["uamqp_JWTTokenAuth", "JWTTokenAuth"]
        ) -> Union["uamqp_Connection", "Connection"]:
            pass

        def close_connection(self):
            pass

        def reset_connection_if_broken(self):
            pass


class _ConnectionMode(Enum):
    ShareConnection = 1
    SeparateConnection = 2


# TODO: see if we want to use this, and if so, make compatible with uamqp
class _SharedConnectionManager(object):  # pylint:disable=too-many-instance-attributes
    def __init__(self, **kwargs):
        self._lock = Lock()
        self._conn: Union["uamqp_Connection", "Connection"] = None

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

    def get_connection(self, endpoint):
        # type: (str, JWTTokenAuth) -> Connection
        with self._lock:
            if self._conn is None:
                self._conn = Connection(
                    endpoint,
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

    def close_connection(self):
        # type: () -> None
        with self._lock:
            if self._conn:
                self._conn.close()
            self._conn = None

    def reset_connection_if_broken(self):
        # type: () -> None
        with self._lock:
            if self._conn and self._conn.state in _CLOSING_STATES:
                self._conn = None


class _SeparateConnectionManager(object):
    def __init__(self, **kwargs):
        pass

    def get_connection(self, endpoint):  # pylint:disable=unused-argument, no-self-use
        # type: (str) -> None
        return None

    def close_connection(self):
        # type: () -> None
        pass

    def reset_connection_if_broken(self):
        # type: () -> None
        pass


def get_connection_manager(**kwargs):
    # type: (...) -> 'ConnectionManager'
    connection_mode = kwargs.get("connection_mode", _ConnectionMode.SeparateConnection)
    if connection_mode == _ConnectionMode.ShareConnection:
        return _SharedConnectionManager(**kwargs)
    return _SeparateConnectionManager(**kwargs)

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import threading
from uamqp import Connection, TransportType


class _ConnectionManager(object):
    def __init__(self, **kwargs):
        self._lock = threading.Lock()
        self._conn = None

        self._container_id = kwargs.get("container_id")
        self._debug = kwargs.get("debug")
        self._error_policy = kwargs.get("error_policy")
        self._properties = kwargs.get("properties")
        self._encoding = kwargs.get("encoding") or "UTF-8"
        self._transport_type = kwargs.get('transport_type') or TransportType.Amqp
        self._http_proxy = kwargs.get('http_proxy')
        self._max_frame_size = kwargs.get("max_frame_size")
        self._channel_max = kwargs.get("channel_max")
        self._idle_timeout = kwargs.get("idle_timeout")
        self._remote_idle_timeout_empty_frame_send_ratio = kwargs.get("remote_idle_timeout_empty_frame_send_ratio")

    def get_connection(self, host, auth):
        # type: (...) -> Connection
        with self._lock:
            if self._conn is None:
                self._conn = Connection(
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
                    encoding=self._encoding)
            return self._conn

    def close_connection(self):
        with self._lock:
            if self._conn:
                self._conn.destroy()
            self._conn = None


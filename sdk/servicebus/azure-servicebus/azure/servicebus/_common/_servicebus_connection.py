# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from threading import RLock

from uamqp import Connection, c_uamqp

from .utils import create_authentication


class ServiceBusConnection(object):
    def __init__(self, client):
        self._conn = None
        self._client = client
        self._lock = RLock()

    def get_connection(self):
        # pylint:disable=c-extension-no-member
        with self._lock:
            if self._conn and self._conn._state in (  # pylint:disable=protected-access
                c_uamqp.ConnectionState.CLOSE_RCVD,
                c_uamqp.ConnectionState.CLOSE_SENT,
                c_uamqp.ConnectionState.DISCARDING,
                c_uamqp.ConnectionState.END,
                c_uamqp.ConnectionState.ERROR
            ):
                self._conn.destroy()
                self._conn = None

            if not self._conn:
                auth = create_authentication(self._client)
                self._conn = Connection(
                    self._client.fully_qualified_namespace,
                    auth,
                    debug=self._client._config.logging_enable  # pylint:disable=protected-access
                )

            return self._conn

    def close(self):
        with self._lock:
            self._conn.destroy()
            self._conn = None

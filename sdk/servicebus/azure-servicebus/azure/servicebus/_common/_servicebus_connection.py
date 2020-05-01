# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from threading import RLock

from uamqp import Connection, c_uamqp


class ServiceBusConnection(object):
    def __init__(self, host, auth, logging_enable=False):
        self._conn = None
        self._host = host
        self._auth = auth
        self._logging_enable = logging_enable
        self._lock = RLock()

    def get_connection(self):
        with self._lock:
            if self._conn and self._conn._state in (  # pylint:disable=protected-access
                c_uamqp.ConnectionState.CLOSE_RCVD,  # pylint:disable=c-extension-no-member
                c_uamqp.ConnectionState.CLOSE_SENT,  # pylint:disable=c-extension-no-member
                c_uamqp.ConnectionState.DISCARDING,  # pylint:disable=c-extension-no-member
                c_uamqp.ConnectionState.END,  # pylint:disable=c-extension-no-member
            ):
                self._conn.destroy()
                self._conn = None

            if not self._conn:
                self._conn = Connection(self._host, self._auth, debug=self._logging_enable)

            return self._conn

    def close(self):
        with self._lock:
            self._conn.destroy()
            self._conn = None

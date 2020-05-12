# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from asyncio import Lock

from uamqp import ConnectionAsync, c_uamqp

from ._async_utils import create_authentication


class ServiceBusConnection(object):
    def __init__(self, client):
        self._conn = None
        self._client = client
        self._lock = Lock()

    async def get_connection(self):
        # pylint:disable=c-extension-no-member
        async with self._lock:
            if self._conn and self._conn._state in (  # pylint:disable=protected-access
                c_uamqp.ConnectionState.CLOSE_RCVD,
                c_uamqp.ConnectionState.CLOSE_SENT,
                c_uamqp.ConnectionState.DISCARDING,
                c_uamqp.ConnectionState.END,
                c_uamqp.ConnectionState.ERROR
            ):
                await self._conn.destroy_async()
                self._conn = None

            if not self._conn:
                auth = await create_authentication(self._client)
                self._conn = ConnectionAsync(
                    self._client.fully_qualified_namespace,
                    auth,
                    debug=self._client._config.logging_enable  # pylint:disable=protected-access
                )

            return self._conn

    async def close(self):
        async with self._lock:
            await self._conn.destroy_async()
            self._conn = None

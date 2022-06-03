# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import asyncio


class AsyncTimer:
    """A non-blocking timer, that calls a function after a specified number of seconds:
    :param int interval: time interval in seconds
    :param callable callback: function to be called after the interval has elapsed
    """

    def __init__(self, interval, callback):
        self._interval = interval
        self._callback = callback
        self._task = None

    def start(self):
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._interval)
        await self._callback()

    def cancel(self):
        if self._task is not None:
            self._task.cancel()

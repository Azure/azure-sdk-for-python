# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
import logging
from typing import Any, Callable
from azure.core.polling import AsyncPollingMethod

from .._shared.response_handlers import process_storage_error
from .._generated.models import StorageErrorException


logger = logging.getLogger(__name__)


class CloseHandlesAsync(AsyncPollingMethod):

    def __init__(self, interval):
        self._command = None
        self._continuation_token = None
        self._exception = None
        self.handles_closed = 0
        self.polling_interval = interval

    async def _update_status(self):
        try:
            status = await self._command(marker=self._continuation_token)
        except StorageErrorException as error:
            process_storage_error(error)
        self._continuation_token = status.get('marker')
        self.handles_closed += status.get('number_of_handles_closed') or 0

    def initialize(self, command, initial_status, _):  # pylint: disable=arguments-differ
        # type: (Any, Any, Callable) -> None
        self._command = command
        self._continuation_token = initial_status['marker']
        self.handles_closed = initial_status['number_of_handles_closed']

    async def run(self):
        # type: () -> None
        try:
            while not self.finished():
                await self._update_status()
                await asyncio.sleep(self.polling_interval)
        except Exception as e:
            logger.warning(str(e))
            raise

    def status(self):
        return self.handles_closed

    def finished(self):
        # type: () -> bool
        """Is this polling finished?
        :rtype: bool
        """
        return self._continuation_token is None

    def resource(self):
        # type: () -> Any
        return self.handles_closed

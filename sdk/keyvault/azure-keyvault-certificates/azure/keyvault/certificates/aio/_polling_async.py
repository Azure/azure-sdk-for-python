# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
import logging
from typing import Any, Callable
from azure.core.polling import AsyncPollingMethod


logger = logging.getLogger(__name__)


class CreateCertificatePollerAsync(AsyncPollingMethod):
    def __init__(self, interval=5, unknown_issuer=False):
        self._command = None
        self._status = None
        self.polling_interval = interval
        self.unknown_issuer = unknown_issuer

    async def _update_status(self):
        # type: () -> None
        pending_certificate = await self._command()
        if (pending_certificate.status.lower() != 'completed'
                and pending_certificate.status.lower() != 'inprogress'
                and pending_certificate.status.lower() != 'cancelled'):
            raise Exception('Unknown status code for pending certificate: {}'.format(pending_certificate))
        self._status = pending_certificate.status.lower()

    def initialize(self, command, initial_status, _):
        # type: (Any, Any, Callable) -> None
        self._command = command
        self._status = initial_status

    async def run(self):
        # type: () -> None
        try:
            while not self.finished():
                await self._update_status()
                await asyncio.sleep(self.polling_interval)
        except Exception as e:
            logger.warning(str(e))
            raise

    def finished(self):
        # type: () -> bool
        if self.unknown_issuer:
            return True
        return self._status == 'completed' or self._status == 'cancelled'

    def resource(self):
        # type: () -> Any
        return self._status

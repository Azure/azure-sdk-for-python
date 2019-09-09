# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import asyncio
import logging
from typing import Any, Callable

from azure.core.polling import AsyncPollingMethod
from azure.keyvault.certificates._shared import parse_vault_id


logger = logging.getLogger(__name__)


class CreateCertificatePollerAsync(AsyncPollingMethod):
    def __init__(self, interval=5, unknown_issuer=False):
        self._command = None
        self._status = None
        self._certificate_id = None
        self.polling_interval = interval
        self.unknown_issuer = unknown_issuer

    async def _update_status(self) -> None:
        pending_certificate = await self._command()
        self._status = pending_certificate.status.lower()
        if not self._certificate_id:
            self._certificate_id = parse_vault_id(pending_certificate.id)

    def initialize(self, client: Any, initial_response: Any, _: Callable) -> None:
        self._command = client
        self._status = initial_response

    async def run(self) -> None:
        try:
            while not self.finished():
                await self._update_status()
                await asyncio.sleep(self.polling_interval)
        except Exception as e:
            logger.warning(str(e))
            raise

    def finished(self) -> bool:
        if self.unknown_issuer:
            return True
        return self._status in ('completed', 'cancelled', 'failed')

    def resource(self) -> Any:
        return self._status

    def status(self) -> str:
        return self._status

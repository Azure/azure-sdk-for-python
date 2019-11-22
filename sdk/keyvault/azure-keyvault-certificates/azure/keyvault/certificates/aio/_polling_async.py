# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import asyncio
import logging
from typing import Any, Callable, Union
from azure.core.polling import AsyncPollingMethod
from .._models import KeyVaultCertificate, CertificateOperation


logger = logging.getLogger(__name__)


class CreateCertificatePollerAsync(AsyncPollingMethod):
    def __init__(self, get_certificate_command, interval=5):
        self._command = None
        self._resource = None
        self._pending_certificate_op = None
        self._get_certificate_command = get_certificate_command
        self._polling_interval = interval

    async def _update_status(self) -> None:
        self._pending_certificate_op = await self._command()

    def initialize(self, client: Any, initial_response: Any, _: Callable) -> None:
        self._command = client
        self._pending_certificate_op = initial_response

    async def run(self) -> None:
        try:
            while not self.finished():
                await self._update_status()
                await asyncio.sleep(self._polling_interval)
            if self._pending_certificate_op.status.lower() == "completed":
                self._resource = await self._get_certificate_command()
            else:
                self._resource = self._pending_certificate_op
        except Exception as e:
            logger.warning(str(e))
            raise

    def finished(self) -> bool:
        if self._pending_certificate_op.issuer_name.lower() == "unknown":
            return True
        return self._pending_certificate_op.status.lower() != "inprogress"

    def resource(self) -> Union[KeyVaultCertificate, CertificateOperation]:
        return self._resource

    def status(self) -> str:
        return self._pending_certificate_op.status.lower()

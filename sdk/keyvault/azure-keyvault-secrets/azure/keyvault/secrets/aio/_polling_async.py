# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import asyncio
import logging
from typing import Any, Callable
from azure.core.polling import AsyncPollingMethod
from azure.core.exceptions import ResourceNotFoundError
from ..models import DeletedSecret


logger = logging.getLogger(__name__)


class DeleteSecretPollerAsync(AsyncPollingMethod):
    def __init__(self, sd_disabled, interval=5):
        self._command = None
        self._deleted_secret = None
        self._sd_disabled = sd_disabled
        self._polling_interval = interval
        self._status = "deleting"

    async def _update_status(self) -> None:
        # type: () -> None
        try:
            await self._command()
            self._status = "deleted"
        except ResourceNotFoundError:
            self._status = "deleting"

    def initialize(self, client: Any, initial_response: str, _: Callable) -> None:
        self._command = client
        self._deleted_secret = initial_response

    async def run(self) -> None:
        try:
            while not self.finished():
                await self._update_status()
                await asyncio.sleep(self._polling_interval)
        except Exception as e:
            logger.warning(str(e))
            raise

    def finished(self) -> bool:
        if self._sd_disabled:
            return True
        return self._status == "deleted"

    def resource(self) -> DeletedSecret:
        return self._deleted_secret

    def status(self) -> str:
        return self._status

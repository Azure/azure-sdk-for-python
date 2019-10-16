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
    def __init__(self, deleted_secret_if_no_sd, interval=5):
        self._command = None
        self._deleted_secret = deleted_secret_if_no_sd
        self._polling_interval = interval
        self._status = None

    async def _update_status(self) -> None:
        # type: () -> None
        try:
            self._deleted_secret = await self._command()
            self._status = "deleted"
        except ResourceNotFoundError:
            self._deleted_secret = None
            self._status = "deleting"

    def initialize(self, client: Any, initial_response: str, _: Callable) -> None:
        self._command = client
        self._status = initial_response

    async def run(self) -> None:
        try:
            while not self.finished():
                await self._update_status()
                await asyncio.sleep(self._polling_interval)
        except Exception as e:
            logger.warning(str(e))
            raise

    def finished(self) -> bool:
        if self._deleted_secret:
            return True
        return False

    def resource(self) -> DeletedSecret:
        return self._deleted_secret

    def status(self) -> str:
        return self._status

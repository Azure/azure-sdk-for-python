# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import asyncio
import logging
from typing import TYPE_CHECKING

from azure.core.polling import AsyncPollingMethod
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
if TYPE_CHECKING:
    # pylint:disable=ungrouped-imports
    from typing import Any, Callable, Union

logger = logging.getLogger(__name__)

class RecoverDeletedAsyncPollingMethod(AsyncPollingMethod):
    def __init__(self, initial_status, finished_status, interval=2):
        self._command = None
        self._resource = None
        self._polling_interval = interval
        self._status = initial_status
        self._finished_status = finished_status

    async def _update_status(self) -> None:
        try:
            await self._command()
            self._status = self._finished_status
        except ResourceNotFoundError:
            pass
        except HttpResponseError as e:
            # If we are polling on get_deleted_* and we don't have get permissions, we will get
            # ResourceNotFoundError until the resource is recovered, at which point we'll get a 403.
            if e.status_code == 403:
                self._status = self._finished_status
            else:
                raise

    def initialize(self, client: "Any", initial_response: str, _: "Callable") -> None:
        self._command = client
        self._resource = initial_response

    async def run(self) -> None:
        try:
            while not self.finished():
                await self._update_status()
                await asyncio.sleep(self._polling_interval)
        except Exception as e:
            logger.warning(str(e))
            raise

    def finished(self) -> bool:
        return self._status == self._finished_status

    def resource(self) -> "Any":
        return self._resource

    def status(self) -> str:
        return self._status


class DeleteAsyncPollingMethod(RecoverDeletedAsyncPollingMethod):
    def __init__(self, initial_status, finished_status, sd_disabled, interval=2):
        self._sd_disabled = sd_disabled
        super(DeleteAsyncPollingMethod, self).__init__(initial_status, finished_status, interval)

    def finished(self) -> bool:
        return self._sd_disabled or self._status == self._finished_status

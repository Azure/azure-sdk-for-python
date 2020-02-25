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


class AsyncKeyVaultPollingMethod(AsyncPollingMethod):
    """Poll with GET requests until one succeeds.

    This allows waiting for Key Vault to delete, or recover, a resource, by polling for the existence of the deleted
    or recovered resource, respectively.
    """

    def __init__(self, command, final_resource, finished, interval=2):
        self._command = command
        self._resource = final_resource
        self._polling_interval = interval
        self._finished = finished

    def initialize(self, client, initial_response, deserialization_callback):
        pass

    async def _update_status(self) -> None:
        try:
            await self._command()
            self._finished = True
        except ResourceNotFoundError:
            pass
        except HttpResponseError as e:
            # If we are polling on get_deleted_* and we don't have get permissions, we will get
            # ResourceNotFoundError until the resource is recovered, at which point we'll get a 403.
            if e.status_code == 403:
                self._finished = True
            else:
                raise

    async def run(self) -> None:
        try:
            while not self.finished():
                await self._update_status()
                if not self.finished():
                    await asyncio.sleep(self._polling_interval)
        except Exception as e:
            logger.warning(str(e))
            raise

    def finished(self) -> bool:
        return self._finished

    def resource(self) -> "Any":
        return self._resource

    def status(self) -> str:
        return "finished" if self._finished else "polling"

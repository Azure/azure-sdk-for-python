# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import time

from azure.core.polling import PollingMethod
from azure.core.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class DeleteResourcePoller(PollingMethod):
    def __init__(self, interval=5):
        self._command = None
        self._deleted_resource = None
        self._polling_interval = interval
        self._status = "deleting"

    def _update_status(self):
        # type: () -> None
        try:
            self._command()
            self._status = "deleted"
        except ResourceNotFoundError:
            self._status = "deleting"

    def initialize(self, client, initial_response, _):
        # type: (Any, Any, Callable) -> None
        self._command = client
        self._deleted_resource = initial_response

    def run(self):
        # type: () -> None
        try:
            while not self.finished():
                self._update_status()
                time.sleep(self._polling_interval)
        except Exception as e:
            logger.warning(str(e))
            raise

    def finished(self):
        # type: () -> bool
        return not self._deleted_resource.recovery_id or self._status == "deleted"

    def resource(self):
        # type: () -> Any
        return self._deleted_resource

    def status(self):
        # type: () -> str
        return self._status

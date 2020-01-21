# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import time
import threading
import uuid
from typing import TYPE_CHECKING

from azure.core.polling import PollingMethod, LROPoller, NoPolling
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

try:
    from urlparse import urlparse # type: ignore # pylint: disable=unused-import
except ImportError:
    from urllib.parse import urlparse

from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.common import with_current_context

if TYPE_CHECKING:
    # pylint: disable=ungrouped-imports
    from typing import Any, Callable, Union, List, Optional

logger = logging.getLogger(__name__)


class KeyVaultOperationPoller(LROPoller):
    """Poller for long running operations where calling result() doesn't wait for operation to complete.
    """

    # pylint: disable=arguments-differ
    def __init__(self, polling_method):
        # type: (PollingMethod) -> None
        super(KeyVaultOperationPoller, self).__init__(None, None, None, NoPolling())
        self._polling_method = polling_method

    # pylint: disable=arguments-differ
    def result(self):
        # type: () -> Any
        """Returns a representation of the final resource without waiting for the operation to complete.

        :returns: The deserialized resource of the long running operation
        :raises ~azure.core.exceptions.HttpResponseError: Server problem with the query.
        """
        return self._polling_method.resource()

    @distributed_trace
    def wait(self, timeout=None):
        # type: (Optional[int]) -> None
        """Wait on the long running operation for a number of seconds.

        You can check if this call has ended with timeout with the "done()" method.

        :param int timeout: Period of time to wait for the long running
         operation to complete (in seconds).
        :raises ~azure.core.exceptions.HttpResponseError: Server problem with the query.
        """

        if not self._polling_method.finished():
            self._done = threading.Event()
            self._thread = threading.Thread(
                target=with_current_context(self._start),
                name="KeyVaultOperationPoller({})".format(uuid.uuid4()))
            self._thread.daemon = True
            self._thread.start()

        if self._thread is None:
            return
        self._thread.join(timeout=timeout)
        try:
            # Let's handle possible None in forgiveness here
            raise self._exception  # type: ignore
        except TypeError: # Was None
            pass

class RecoverDeletedPollingMethod(PollingMethod):
    def __init__(self, command, final_resource, initial_status, finished_status, interval=2):
        self._command = command
        self._resource = final_resource
        self._polling_interval = interval
        self._status = initial_status
        self._finished_status = finished_status

    def _update_status(self):
        # type: () -> None
        try:
            self._command()
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

    def initialize(self, client, initial_response, deserialization_callback):
        pass

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
        return self._status == self._finished_status

    def resource(self):
        # type: () -> Any
        return self._resource

    def status(self):
        # type: () -> str
        return self._status


class DeletePollingMethod(RecoverDeletedPollingMethod):
    def __init__(self, command, final_resource, initial_status, finished_status, sd_disabled, interval=2):
        self._sd_disabled = sd_disabled
        super(DeletePollingMethod, self).__init__(
            command=command,
            final_resource=final_resource,
            initial_status=initial_status,
            finished_status=finished_status,
            interval=interval
        )

    def finished(self):
        # type: () -> bool
        return self._sd_disabled or self._status == self._finished_status

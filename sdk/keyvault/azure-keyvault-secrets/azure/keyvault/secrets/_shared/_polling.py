# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import time
import threading
import uuid
from typing import TYPE_CHECKING

from azure.core.polling import PollingMethod, LROPoller
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

try:
    from urlparse import urlparse # type: ignore # pylint: disable=unused-import
except ImportError:
    from urllib.parse import urlparse

from azure.core.pipeline.transport._base import HttpResponse  # type: ignore
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.common import with_current_context

if TYPE_CHECKING:
    # pylint: disable=ungrouped-imports
    import requests
    from msrest.serialization import Model # type: ignore # pylint: disable=unused-import
    from typing import Any, Callable, Union, List, Optional
    DeserializationCallbackType = Union[Model, Callable[[requests.Response], Model]]

logger = logging.getLogger(__name__)


class KeyVaultOperationPoller(LROPoller):
    """Poller for long running operations where calling result() doesn't wait for operation to complete.

    :param client: A pipeline service client
    :type client: ~azure.core.PipelineClient
    :param initial_response: The initial call response
    :type initial_response:
     ~azure.core.pipeline.transport.HttpResponse or ~azure.core.pipeline.transport.AsyncHttpResponse
    :param deserialization_callback: A callback that takes a Response and return a deserialized object.
                                     If a subclass of Model is given, this passes "deserialize" as callback.
    :type deserialization_callback: callable or msrest.serialization.Model
    :param polling_method: The polling strategy to adopt
    :type polling_method: ~azure.core.polling.PollingMethod
    """

    def __init__(self, client, initial_response, deserialization_callback, polling_method):
        # type: (Any, HttpResponse, DeserializationCallbackType, PollingMethod) -> None
        # pylint: disable=super-init-not-called
        self._client = client
        self._response = initial_response
        self._callbacks = []  # type: List[Callable]
        self._polling_method = polling_method

        # This implicit test avoids bringing in an explicit dependency on Model directly
        try:
            deserialization_callback = deserialization_callback.deserialize # type: ignore
        except AttributeError:
            pass

        # Might raise a CloudError
        self._polling_method.initialize(self._client, self._response, deserialization_callback)

        # Prepare thread execution
        self._thread = None
        self._done = None
        self._exception = None

    # pylint: disable=arguments-differ
    def result(self):
        # type: (Optional[int]) -> Model
        """Returns the result of the long running operation without blocking until its completion.

        :returns: The deserialized resource of the long running operation,
         if one is available.
        :raises ~azure.core.exceptions.HttpResponseError: Server problem with the query.
        """
        return self._polling_method.resource()

    @distributed_trace
    def wait(self, timeout=None):
        # type: (Optional[int]) -> None
        """Wait on the long running operation for a specified length
        of time. You can check if this call as ended with timeout with the
        "done()" method.

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
    def __init__(self, initial_status, finished_status, interval=2):
        self._command = None
        self._resource = None
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
            if e.status_code == 403:
                self._status = self._finished_status
            else:
                raise

    def initialize(self, client, initial_response, _):
        # type: (Any, Any, Callable) -> None
        self._command = client
        self._resource = initial_response

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
    def __init__(self, initial_status, finished_status, sd_disabled, interval=2):
        self._sd_disabled = sd_disabled
        super(DeletePollingMethod, self).__init__(initial_status, finished_status, interval)

    def finished(self):
        # type: () -> bool
        return self._sd_disabled or self._status == "deleted"

# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import threading
import uuid
try:
    from urlparse import urlparse # type: ignore # pylint: disable=unused-import
except ImportError:
    from urllib.parse import urlparse

from typing import Any, Callable, Union, List, Optional, TYPE_CHECKING
from azure.core.pipeline.transport._base import HttpResponse  # type: ignore
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.common import with_current_context

if TYPE_CHECKING:
    import requests
    from msrest.serialization import Model # type: ignore # pylint: disable=unused-import
    DeserializationCallbackType = Union[Model, Callable[[requests.Response], Model]]


class PollingMethod(object):
    """ABC class for polling method.
    """
    def initialize(self, client, initial_response, deserialization_callback):
        # type: (Any, Any, Any) -> None
        raise NotImplementedError("This method needs to be implemented")

    def run(self):
        # type: () -> None
        raise NotImplementedError("This method needs to be implemented")

    def status(self):
        # type: () -> str
        raise NotImplementedError("This method needs to be implemented")

    def finished(self):
        # type: () -> bool
        raise NotImplementedError("This method needs to be implemented")

    def resource(self):
        # type: () -> Any
        raise NotImplementedError("This method needs to be implemented")

class NoPolling(PollingMethod):
    """An empty poller that returns the deserialized initial response.
    """
    def __init__(self):
        self._initial_response = None
        self._deserialization_callback = None

    def initialize(self, _, initial_response, deserialization_callback):
        # type: (Any, requests.Response, Callable) -> None
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback

    def run(self):
        # type: () -> None
        """Empty run, no polling.
        """

    def status(self):
        # type: () -> str
        """Return the current status as a string.

        :rtype: str
        """
        return "succeeded"

    def finished(self):
        # type: () -> bool
        """Is this polling finished?

        :rtype: bool
        """
        return True

    def resource(self):
        # type: () -> Any
        return self._deserialization_callback(self._initial_response)


class LROPoller(object):
    """Poller for long running operations.

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
        if not self._polling_method.finished():
            self._done = threading.Event()
            self._thread = threading.Thread(
                target=with_current_context(self._start),
                name="LROPoller({})".format(uuid.uuid4()))
            self._thread.daemon = True
            self._thread.start()

    def _start(self):
        """Start the long running operation.
        On completion, runs any callbacks.

        :param callable update_cmd: The API request to check the status of
         the operation.
        """
        try:
            self._polling_method.run()
        except Exception as err: #pylint: disable=broad-except
            self._exception = err

        finally:
            self._done.set()

        callbacks, self._callbacks = self._callbacks, []
        while callbacks:
            for call in callbacks:
                call(self._polling_method)
            callbacks, self._callbacks = self._callbacks, []

    def status(self):
        # type: () -> str
        """Returns the current status string.

        :returns: The current status string
        :rtype: str
        """
        return self._polling_method.status()

    def result(self, timeout=None):
        # type: (Optional[int]) -> Model
        """Return the result of the long running operation, or
        the result available after the specified timeout.

        :returns: The deserialized resource of the long running operation,
         if one is available.
        :raises ~azure.core.exceptions.HttpResponseError: Server problem with the query.
        """
        self.wait(timeout)  # type: ignore
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
        if self._thread is None:
            return
        self._thread.join(timeout=timeout)
        try:
            # Let's handle possible None in forgiveness here
            raise self._exception  # type: ignore
        except TypeError: # Was None
            pass

    def done(self):
        # type: () -> bool
        """Check status of the long running operation.

        :returns: 'True' if the process has completed, else 'False'.
        :rtype: bool
        """
        return self._thread is None or not self._thread.is_alive()

    def add_done_callback(self, func):
        # type: (Callable) -> None
        """Add callback function to be run once the long running operation
        has completed - regardless of the status of the operation.

        :param callable func: Callback function that takes at least one
         argument, a completed LongRunningOperation.
        """
        # Still use "_done" and not "done", since CBs are executed inside the thread.
        if self._done is None or self._done.is_set():
            func(self._polling_method)
        # Let's add them still, for consistency (if you wish to access to it for some reasons)
        self._callbacks.append(func)

    def remove_done_callback(self, func):
        # type: (Callable) -> None
        """Remove a callback from the long running operation.

        :param callable func: The function to be removed from the callbacks.
        :raises ValueError: if the long running operation has already completed.
        """
        if self._done is None or self._done.is_set():
            raise ValueError("Process is complete.")
        self._callbacks = [c for c in self._callbacks if c != func]

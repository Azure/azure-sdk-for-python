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

import re
import threading
import time
import uuid
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from msrest.exceptions import DeserializationError, ClientException
from msrestazure.azure_exceptions import CloudError


FINISHED = frozenset(['succeeded', 'canceled', 'failed'])
FAILED = frozenset(['canceled', 'failed'])
SUCCEEDED = frozenset(['succeeded'])


def finished(status):
    if hasattr(status, 'value'):
        status = status.value
    return str(status).lower() in FINISHED


def failed(status):
    if hasattr(status, 'value'):
        status = status.value
    return str(status).lower() in FAILED


def succeeded(status):
    if hasattr(status, 'value'):
        status = status.value
    return str(status).lower() in SUCCEEDED


def _validate(url):
    """Validate a url.

    :param str url: Polling URL extracted from response header.
    :raises: ValueError if URL has no scheme or host.
    """
    if url is None:
        return
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("Invalid URL header")

def _get_header_url(response, header_name):
    """Get a URL from a header requests.

    :param requests.Response response: REST call response.
    :param str header_name: Header name.
    :returns: URL if not None AND valid, None otherwise
    """
    url = response.headers.get(header_name)
    try:
        _validate(url)
    except ValueError:
        return None
    else:
        return url

class BadStatus(Exception):
    pass


class BadResponse(Exception):
    pass


class OperationFailed(Exception):
    pass


class SimpleResource:
    """An implementation of Python 3 SimpleNamespace.
    Used to deserialize resource objects from response bodies where
    no particular object type has been specified.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        keys = sorted(self.__dict__)
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "{}({})".format(type(self).__name__, ", ".join(items))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class LongRunningOperation(object):
    """LongRunningOperation
    Provides default logic for interpreting operation responses
    and status updates.
    """
    _convert = re.compile('([a-z0-9])([A-Z])')

    def __init__(self, response, outputs):
        self.method = response.request.method
        self.status = ""
        self.resource = None
        self.get_outputs = outputs
        self.async_url = None
        self.location_url = None
        self.initial_status_code = None

    def _raise_if_bad_http_status_and_method(self, response):
        """Check response status code is valid for a Put or Patch
        request. Must be 200, 201, 202, or 204.

        :raises: BadStatus if invalid status.
        """
        code = response.status_code
        if code in {200, 202} or \
           (code == 201 and self.method in {'PUT', 'PATCH'}) or \
           (code == 204 and self.method in {'DELETE', 'POST'}):
            return
        raise BadStatus(
            "Invalid return status for {!r} operation".format(self.method))

    def _is_empty(self, response):
        """Check if response body contains meaningful content.

        :rtype: bool
        :raises: DeserializationError if response body contains invalid
         json data.
        """
        if not response.content:
            return True
        try:
            body = response.json()
            return not body
        except ValueError:
            raise DeserializationError(
                "Error occurred in deserializing the response body.")

    def _deserialize(self, response):
        """Attempt to deserialize resource from response.

        :param requests.Response response: latest REST call response.
        """
        # Hacking response with initial status_code
        previous_status = response.status_code
        response.status_code = self.initial_status_code
        resource = self.get_outputs(response)
        response.status_code = previous_status

        # Hack for Storage or SQL, to workaround the bug in the Python generator
        if resource is None:
            previous_status = response.status_code
            for status_code_to_test in [200, 201]:
                try:
                    response.status_code = status_code_to_test
                    resource = self.get_outputs(response)
                except ClientException:
                    pass
                else:
                    return resource
                finally:
                    response.status_code = previous_status
        return resource

    def _get_async_status(self, response):
        """Attempt to find status info in response body.

        :param requests.Response response: latest REST call response.
        :rtype: str
        :returns: Status if found, else 'None'.
        """
        if self._is_empty(response):
            return None
        body = response.json()
        return body.get('status')

    def _get_provisioning_state(self, response):
        """
        Attempt to get provisioning state from resource.
        :param requests.Response response: latest REST call response.
        :returns: Status if found, else 'None'.
        """
        if self._is_empty(response):
            return None
        body = response.json()
        return body.get("properties", {}).get("provisioningState")

    def should_do_final_get(self):
        """Check whether the polling should end doing a final GET.

        :param requests.Response response: latest REST call response.
        :rtype: bool
        """
        return (self.async_url or not self.resource) and \
                self.method in {'PUT', 'PATCH'}

    def set_initial_status(self, response):
        """Process first response after initiating long running
        operation and set self.status attribute.

        :param requests.Response response: initial REST call response.
        """
        self._raise_if_bad_http_status_and_method(response)

        if self._is_empty(response):
            self.resource = None
        else:
            try:
                self.resource = self.get_outputs(response)
            except DeserializationError:
                self.resource = None

        self.set_async_url_if_present(response)

        if response.status_code in {200, 201, 202, 204}:
            self.initial_status_code = response.status_code
            if self.async_url or self.location_url or response.status_code == 202:
                self.status = 'InProgress'
            elif response.status_code == 201:
                status = self._get_provisioning_state(response)
                self.status = status or 'InProgress'
            elif response.status_code == 200:
                status = self._get_provisioning_state(response)
                self.status = status or 'Succeeded'
            elif response.status_code == 204:
                self.status = 'Succeeded'
                self.resource = None
            else:
                raise OperationFailed("Invalid status found")
            return
        raise OperationFailed("Operation failed or cancelled")

    def get_status_from_location(self, response):
        """Process the latest status update retrieved from a 'location'
        header.

        :param requests.Response response: latest REST call response.
        :raises: BadResponse if response has no body and not status 202.
        """
        self._raise_if_bad_http_status_and_method(response)
        code = response.status_code
        if code == 202:
            self.status = "InProgress"
        else:
            self.status = 'Succeeded'
            if self._is_empty(response):
                self.resource = None
            else:
                self.resource = self._deserialize(response)

    def get_status_from_resource(self, response):
        """Process the latest status update retrieved from the same URL as
        the previous request.

        :param requests.Response response: latest REST call response.
        :raises: BadResponse if status not 200 or 204.
        """
        self._raise_if_bad_http_status_and_method(response)
        if self._is_empty(response):
            raise BadResponse('The response from long running operation '
                              'does not contain a body.')

        status = self._get_provisioning_state(response)
        self.status = status or 'Succeeded'

        self.resource = self._deserialize(response)

    def get_status_from_async(self, response):
        """Process the latest status update retrieved from a
        'azure-asyncoperation' header.

        :param requests.Response response: latest REST call response.
        :raises: BadResponse if response has no body, or body does not
         contain status.
        """
        self._raise_if_bad_http_status_and_method(response)
        if self._is_empty(response):
            raise BadResponse('The response from long running operation '
                              'does not contain a body.')

        self.status = self._get_async_status(response)
        if not self.status:
            raise BadResponse("No status found in body")

        # Status can contains information, see ARM spec:
        # https://github.com/Azure/azure-resource-manager-rpc/blob/master/v1.0/Addendum.md#operation-resource-format
        # "properties": {
        # /\* The resource provider can choose the values here, but it should only be
        #   returned on a successful operation (status being "Succeeded"). \*/
        #},
        # So try to parse it
        try:
            self.resource = self.get_outputs(response)
        except Exception:
            self.resource = None

    def set_async_url_if_present(self, response):
        async_url = _get_header_url(response, 'azure-asyncoperation')
        if async_url:
            self.async_url = async_url
        
        location_url = _get_header_url(response, 'location')
        if location_url:
            self.location_url = location_url


class AzureOperationPoller(object):
    """Initiates long running operation and polls status in separate
    thread.

    :param callable send_cmd: The API request to initiate the operation.
    :param callable update_cmd: The API reuqest to check the status of
        the operation.
    :param callable output_cmd: The function to deserialize the resource
        of the operation.
    :param int timeout: Time in seconds to wait between status calls,
        default is 30.
    """

    def __init__(self, send_cmd, output_cmd, update_cmd, timeout=30):
        self._timeout = timeout
        self._callbacks = []

        try:
            self._response = send_cmd()
            self._operation = LongRunningOperation(self._response, output_cmd)
            self._operation.set_initial_status(self._response)
        except BadStatus:
            self._operation.status = 'Failed'
            raise CloudError(self._response)
        except BadResponse as err:
            self._operation.status = 'Failed'
            raise CloudError(self._response, str(err))
        except OperationFailed:
            raise CloudError(self._response)

        self._thread = None
        self._done = None
        self._exception = None
        if not finished(self.status()):
            self._done = threading.Event()
            self._thread = threading.Thread(
                target=self._start,
                name="AzureOperationPoller({})".format(uuid.uuid4()),
                args=(update_cmd,))
            self._thread.daemon = True
            self._thread.start()

    def _start(self, update_cmd):
        """Start the long running operation.
        On completion, runs any callbacks.

        :param callable update_cmd: The API reuqest to check the status of
         the operation.
        """
        try:
            self._poll(update_cmd)

        except BadStatus:
            self._operation.status = 'Failed'
            self._exception = CloudError(self._response)

        except BadResponse as err:
            self._operation.status = 'Failed'
            self._exception = CloudError(self._response, str(err))

        except OperationFailed:
            self._exception = CloudError(self._response)

        except Exception as err:
            self._exception = err

        finally:
            self._done.set()

        callbacks, self._callbacks = self._callbacks, []
        while callbacks:
            for call in callbacks:
                call(self._operation)
            callbacks, self._callbacks = self._callbacks, []

    def _delay(self):
        """Check for a 'retry-after' header to set timeout,
        otherwise use configured timeout.
        """
        if self._response is None:
            return
        if self._response.headers.get('retry-after'):
            time.sleep(int(self._response.headers['retry-after']))
        else:
            time.sleep(self._timeout)

    def _polling_cookie(self):
        """Collect retry cookie - we only want to do this for the test server
        at this point, unless we implement a proper cookie policy.

        :returns: Dictionary containing a cookie header if required,
         otherwise an empty dictionary.
        """
        parsed_url = urlparse(self._response.request.url)
        host = parsed_url.hostname.strip('.')
        if host == 'localhost':
            return {'cookie': self._response.headers.get('set-cookie', '')}
        return {}

    def _poll(self, update_cmd):
        """Poll status of operation so long as operation is incomplete and
        we have an endpoint to query.

        :param callable update_cmd: The function to call to retrieve the
         latest status of the long running operation.
        :raises: OperationFailed if operation status 'Failed' or 'Cancelled'.
        :raises: BadStatus if response status invalid.
        :raises: BadResponse if response invalid.
        """
        initial_url = self._response.request.url

        while not finished(self.status()):
            self._delay()
            headers = self._polling_cookie()

            if self._operation.async_url:
                self._response = update_cmd(
                    self._operation.async_url, headers)
                self._operation.set_async_url_if_present(self._response)
                self._operation.get_status_from_async(
                    self._response)
            elif self._operation.location_url:
                self._response = update_cmd(
                    self._operation.location_url, headers)
                self._operation.set_async_url_if_present(self._response)
                self._operation.get_status_from_location(
                    self._response)
            elif self._operation.method == "PUT":
                self._response = update_cmd(initial_url, headers)
                self._operation.set_async_url_if_present(self._response)
                self._operation.get_status_from_resource(
                    self._response)
            else:
                raise BadResponse(
                    'Location header is missing from long running operation.')

        if failed(self._operation.status):
            raise OperationFailed("Operation failed or cancelled")
        elif self._operation.should_do_final_get():
            self._response = update_cmd(initial_url)
            self._operation.get_status_from_resource(
                self._response)

    def status(self):
        """Returns the current status string.

        :returns: The current status string
        :rtype: str
        """
        return self._operation.status

    def result(self, timeout=None):
        """Return the result of the long running operation, or
        the result available after the specified timeout.

        :returns: The deserialized resource of the long running operation,
         if one is available.
        :raises CloudError: Server problem with the query.
        """
        self.wait(timeout)
        return self._operation.resource

    def wait(self, timeout=None):
        """Wait on the long running operation for a specified length
        of time.

        :param int timeout: Perion of time to wait for the long running
         operation to complete.
        :raises CloudError: Server problem with the query.
        """
        if self._thread is None:
            return
        self._thread.join(timeout=timeout)
        try:
            raise self._exception
        except TypeError:
            pass

    def done(self):
        """Check status of the long running operation.

        :returns: 'True' if the process has completed, else 'False'.
        """
        return self._thread is None or not self._thread.isAlive()

    def add_done_callback(self, func):
        """Add callback function to be run once the long running operation
        has completed - regardless of the status of the operation.

        :param callable func: Callback function that takes at least one
         argument, a completed LongRunningOperation.
        :raises: ValueError if the long running operation has already
         completed.
        """
        if self._done is None or self._done.is_set():
            raise ValueError("Process is complete.")
        self._callbacks.append(func)

    def remove_done_callback(self, func):
        """Remove a callback from the long running operation.

        :param callable func: The function to be removed from the callbacks.
        :raises: ValueError if the long running operation has already
         completed.
        """
        if self._done is None or self._done.is_set():
            raise ValueError("Process is complete.")
        self._callbacks = [c for c in self._callbacks if c != func]

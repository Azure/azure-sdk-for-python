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
import json
import time
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from msrest.exceptions import DeserializationError
from msrest.polling import PollingMethod

from ..azure_exceptions import CloudError


FINISHED = frozenset(['succeeded', 'canceled', 'failed'])
FAILED = frozenset(['canceled', 'failed'])
SUCCEEDED = frozenset(['succeeded'])

_AZURE_ASYNC_OPERATION_FINAL_STATE = "azure-async-operation"
_LOCATION_FINAL_STATE = "location"

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


class BadStatus(Exception):
    pass


class BadResponse(Exception):
    pass


class OperationFailed(Exception):
    pass

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

def get_header_url(response, header_name):
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


class LongRunningOperation(object):
    """LongRunningOperation
    Provides default logic for interpreting operation responses
    and status updates.

    :param requests.Response response: The initial response.
    :param callable deserialization_callback: The deserialization callaback.
    :param dict lro_options: LRO options.
    :param kwargs: Unused for now
    """

    def __init__(self, response, deserialization_callback, lro_options=None, **kwargs):
        self.method = response.request.method
        self.initial_response = response
        self.status = ""
        self.resource = None
        self.deserialization_callback = deserialization_callback
        self.async_url = None
        self.location_url = None
        if lro_options is None:
            lro_options = {
                'final-state-via': _AZURE_ASYNC_OPERATION_FINAL_STATE
            }
        self.lro_options = lro_options

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
        :raises: DeserializationError if response body contains invalid json data.
        """
        # Assume ClientResponse has "body", and otherwise it's a requests.Response
        content = response.text() if hasattr(response, "body") else response.text
        if not content:
            return True
        try:
            return not json.loads(content)
        except ValueError:
            raise DeserializationError(
                "Error occurred in deserializing the response body.")

    def _as_json(self, response):
        """Assuming this is not empty, return the content as JSON.

        Result/exceptions is not determined if you call this method without testing _is_empty.

        :raises: DeserializationError if response body contains invalid json data.
        """
        # Assume ClientResponse has "body", and otherwise it's a requests.Response
        content = response.text() if hasattr(response, "body") else response.text
        try:
            return json.loads(content)
        except ValueError:
            raise DeserializationError(
                "Error occurred in deserializing the response body.")

    def _deserialize(self, response):
        """Attempt to deserialize resource from response.

        :param requests.Response response: latest REST call response.
        """
        return self.deserialization_callback(response)

    def _get_async_status(self, response):
        """Attempt to find status info in response body.

        :param requests.Response response: latest REST call response.
        :rtype: str
        :returns: Status if found, else 'None'.
        """
        if self._is_empty(response):
            return None
        body = self._as_json(response)
        return body.get('status')

    def _get_provisioning_state(self, response):
        """
        Attempt to get provisioning state from resource.
        :param requests.Response response: latest REST call response.
        :returns: Status if found, else 'None'.
        """
        if self._is_empty(response):
            return None
        body = self._as_json(response)
        return body.get("properties", {}).get("provisioningState")

    def should_do_final_get(self):
        """Check whether the polling should end doing a final GET.

        :param requests.Response response: latest REST call response.
        :rtype: bool
        """
        return ((self.async_url or not self.resource) and self.method in {'PUT', 'PATCH'}) \
                or (self.lro_options['final-state-via'] == _LOCATION_FINAL_STATE and self.location_url and self.async_url and self.method == 'POST')

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
                self.resource = self._deserialize(response)
            except DeserializationError:
                self.resource = None

        self.set_async_url_if_present(response)

        if response.status_code in {200, 201, 202, 204}:
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

        self.parse_resource(response)

    def parse_resource(self, response):
        """Assuming this response is a resource, use the deserialization callback to parse it.
        If body is empty, assuming no resource to return.
        """
        self._raise_if_bad_http_status_and_method(response)
        if not self._is_empty(response):
            self.resource = self._deserialize(response)
        else:
            self.resource = None

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
            self.resource = self._deserialize(response)
        except Exception:
            self.resource = None

    def set_async_url_if_present(self, response):
        async_url = get_header_url(response, 'azure-asyncoperation')
        if async_url:
            self.async_url = async_url
        location_url = get_header_url(response, 'location')
        if location_url:
            self.location_url = location_url

    def get_status_link(self):
        if self.async_url:
            return self.async_url
        elif self.location_url:
            return self.location_url
        elif self.method == "PUT":
            return self.initial_response.request.url
        else:
            raise BadResponse("Unable to find a valid status link for polling")


class ARMPolling(PollingMethod):

    def __init__(self, timeout=30, lro_options=None, **operation_config):
        self._timeout = timeout
        self._operation = None # Will hold an instance of LongRunningOperation
        self._response = None  # Will hold latest received response
        self._operation_config = operation_config
        self._lro_options = lro_options

    def status(self):
        """Return the current status as a string.
        :rtype: str
        """
        if not self._operation:
            raise ValueError("set_initial_status was never called. Did you give this instance to a poller?")
        return self._operation.status

    def finished(self):
        """Is this polling finished?
        :rtype: bool
        """
        return finished(self.status())

    def resource(self):
        """Return the built resource.
        """
        return self._operation.resource

    def initialize(self, client, initial_response, deserialization_callback):
        """Set the initial status of this LRO.

        :param initial_response: The initial response of the poller
        :raises: CloudError if initial status is incorrect LRO state
        """
        self._client = client
        self._response = initial_response
        self._operation = LongRunningOperation(initial_response, deserialization_callback, self._lro_options)
        try:
            self._operation.set_initial_status(initial_response)
        except BadStatus:
            self._operation.status = 'Failed'
            raise CloudError(initial_response)
        except BadResponse as err:
            self._operation.status = 'Failed'
            raise CloudError(initial_response, str(err))
        except OperationFailed:
            raise CloudError(initial_response)

    def run(self):
        try:
            self._poll()
        except BadStatus:
            self._operation.status = 'Failed'
            raise CloudError(self._response)

        except BadResponse as err:
            self._operation.status = 'Failed'
            raise CloudError(self._response, str(err))

        except OperationFailed:
            raise CloudError(self._response)

    def _poll(self):
        """Poll status of operation so long as operation is incomplete and
        we have an endpoint to query.

        :param callable update_cmd: The function to call to retrieve the
         latest status of the long running operation.
        :raises: OperationFailed if operation status 'Failed' or 'Cancelled'.
        :raises: BadStatus if response status invalid.
        :raises: BadResponse if response invalid.
        """

        while not self.finished():
            self._delay()
            self.update_status()

        if failed(self._operation.status):
            raise OperationFailed("Operation failed or cancelled")

        elif self._operation.should_do_final_get():
            if self._operation.method == 'POST' and self._operation.location_url:
                final_get_url = self._operation.location_url
            else:
                final_get_url = self._operation.initial_response.request.url
            self._response = self.request_status(final_get_url)
            self._operation.parse_resource(self._response)

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

    def update_status(self):
        """Update the current status of the LRO.
        """
        if self._operation.async_url:
            self._response = self.request_status(self._operation.async_url)
            self._operation.set_async_url_if_present(self._response)
            self._operation.get_status_from_async(self._response)
        elif self._operation.location_url:
            self._response = self.request_status(self._operation.location_url)
            self._operation.set_async_url_if_present(self._response)
            self._operation.get_status_from_location(self._response)
        elif self._operation.method == "PUT":
            initial_url = self._operation.initial_response.request.url
            self._response = self.request_status(initial_url)
            self._operation.set_async_url_if_present(self._response)
            self._operation.get_status_from_resource(self._response)
        else:
            raise BadResponse("Unable to find status link for polling.")

    def request_status(self, status_link):
        """Do a simple GET to this status link.

        This method re-inject 'x-ms-client-request-id'.

        :rtype: requests.Response
        """
        request = self._client.get(status_link)
        # ARM requires to re-inject 'x-ms-client-request-id' while polling
        header_parameters = {
            'x-ms-client-request-id': self._operation.initial_response.request.headers['x-ms-client-request-id']
        }
        return self._client.send(request, header_parameters, stream=False, **self._operation_config)

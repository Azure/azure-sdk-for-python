# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Service-specific Exceptions in the Azure Cosmos database service.
"""
from azure.core.exceptions import (
    AzureError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError
)
from . import http_constants


class CosmosHttpResponseError(HttpResponseError):
    """An HTTP request to the Azure Cosmos database service has failed."""

    def __init__(self, status_code=None, message=None, response=None, **kwargs):
        """
        :param int status_code: HTTP response code.
        :param str message: Error message.
        """
        self.headers = response.headers if response else {}
        self.sub_status = None
        self.http_error_message = message
        status = status_code or (int(response.status_code) if response else 0)

        if http_constants.HttpHeaders.SubStatus in self.headers:
            self.sub_status = int(self.headers[http_constants.HttpHeaders.SubStatus])
            formatted_message = "Status code: %d Sub-status: %d\n%s" % (status, self.sub_status, str(message))
        else:
            formatted_message = "Status code: %d\n%s" % (status, str(message))

        super(CosmosHttpResponseError, self).__init__(message=formatted_message, response=response, **kwargs)
        self.status_code = status


class CosmosResourceNotFoundError(ResourceNotFoundError, CosmosHttpResponseError):
    """An HTTP error response with status code 404."""


class CosmosResourceExistsError(ResourceExistsError, CosmosHttpResponseError):
    """An HTTP error response with status code 409."""


class CosmosAccessConditionFailedError(CosmosHttpResponseError):
    """An HTTP error response with status code 412."""


class CosmosBatchOperationError(HttpResponseError):
    """A transactional batch request to the Azure Cosmos database service has failed.

    :ivar int error_index: Index of operation within the batch that caused the error.
    :ivar headers: Error headers.
    :vartype headers: dict[str, Any]
    :ivar status_code: HTTP response code.
    :vartype status_code: int
    :ivar message: Error message.
    :vartype message: str
    :ivar operation_responses: List of failed operations' responses.
    :vartype operation_responses: List[dict[str, Any]]
    .. admonition:: Example:

        .. literalinclude:: ../samples/document_management.py
            :start-after: [START handle_batch_error]
            :end-before: [END handle_batch_error]
            :language: python
            :dedent: 0
            :caption: Handle a CosmosBatchOperationError:
            :name: handle_batch_error
    """
    def __init__(
            self,
            error_index=None,
            headers=None,
            status_code=None,
            message=None,
            operation_responses=None,
            **kwargs):
        self.error_index = error_index
        self.headers = headers
        self.sub_status = None
        self.http_error_message = message
        self.operation_responses = operation_responses
        status = status_code

        if http_constants.HttpHeaders.SubStatus in self.headers:
            self.sub_status = int(self.headers[http_constants.HttpHeaders.SubStatus])
            formatted_message = "Status code: %d Sub-status: %d\n%s" % (status, self.sub_status, str(message))
        else:
            formatted_message = "Status code: %d\n%s" % (status, str(message))

        super(CosmosBatchOperationError, self).__init__(message=formatted_message, response=None, **kwargs)
        self.status_code = status


class CosmosClientTimeoutError(AzureError):
    """An operation failed to complete within the specified timeout."""

    def __init__(self, **kwargs):
        message = "Client operation failed to complete within specified timeout."
        self.response = None
        self.history = None
        super(CosmosClientTimeoutError, self).__init__(message, **kwargs)


def _partition_range_is_gone(e):
    if (e.status_code == http_constants.StatusCodes.GONE
            and e.sub_status == http_constants.SubStatusCodes.PARTITION_KEY_RANGE_GONE):
        return True
    return False

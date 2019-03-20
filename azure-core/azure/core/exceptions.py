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

import logging
import sys

from typing import Callable, Any, Optional, TYPE_CHECKING


_LOGGER = logging.getLogger(__name__)


def raise_with_traceback(exception, message="", *args, **kwargs):
    # type: (Callable, str, Any, Any) -> None
    """Raise exception with a specified traceback.

    This MUST be called inside a "except" clause.

    :param Exception exception: Error type to be raised.
    :param str message: Message to include with error, empty by default.
    :param args: Any additional args to be included with exception.
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    # If not called inside a "except", exc_type will be None. Assume it will not happen
    exc_msg = "{}, {}: {}".format(message, exc_type.__name__, exc_value)  # type: ignore
    error = exception(exc_msg, *args, **kwargs)
    try:
        raise error.with_traceback(exc_traceback)
    except AttributeError:
        error.__traceback__ = exc_traceback
        raise error


class AzureError(Exception):
    """Base exception for all errors."""

    def __init__(self, message, *args, **kwargs):
        self.inner_exception = kwargs.get('error')
        self.response = kwargs.get('response')
        exc_type, exc_value, exc_traceback = sys.exc_info()
        # If not called inside a "except", exc_type will be None. Assume it will not happen
        self.exc_msg = "{}, {}: {}".format(message, exc_type.__name__, exc_value)  # type: ignore
        self.message = str(message)
        super(AzureError, self).__init__(self.message, *args)


class AzureLibraryError(AzureError):
    """An error occurred in the client while processing the pipeline."""


class AzureLibraryResponse(AzureLibraryError):
    """An error occurred in the client while processing the response."""


class AzureLibraryRequest(AzureLibraryError):
    """An error occurred in the client while building the request."""


class DecodeError(AzureLibraryResponse):
    """Error raised during response deserialization."""


class ServiceRequestError(AzureError):
    """An error occurred while attempt to make a request to the service."""


class ConnectionError(ServiceRequestError):
    """An error occurred while attempting to establish the connection.
    These errors are safe to retry."""


class ConnectionTimeoutError(ConnectionError):
    """The request timed out while trying to connect to the remote server.
    These errors are safe to retry."""


class ConnectionReadError(ServiceRequestError):
    """An error occurred during the request/response.
    These errors may not be safe to retry."""


class ReadTimeoutError(ConnectionReadError):
    """The server did not send any data in the allotted amount of time.
    These errors may not be safe to retry."""


class ClientRequestError(ServiceRequestError):
    """An error response with status code 4xx.
    This will not be raised directly by the Azure core pipeline."""


class ResourceExistsError(ClientRequestError):
    """An error response with status code 4xx.
    This will not be raised directly by the Azure core pipeline."""


class ClientAuthenticationError(ClientRequestError):
    """An error response with status code 4xx.
    This will not be raised directly by the Azure core pipeline."""


class ResourceModifiedError(ClientRequestError):
    """An error response with status code 4xx.
    This will not be raised directly by the Azure core pipeline."""


class ServerError(ServiceRequestError):
    """An error response with status code 5xx.
    This will not be raised directly by the Azure core pipeline."""



class TooManyRedirectsError(ServiceRequestError):
    """Reached the maximum number of redirect attempts."""

    def __init__(self, history, *args, **kwargs):
        self.history = history
        message = "Reached maximum redirect attempts."
        super(TooManyRedirectsError, self).__init__(message, *args, **kwargs)

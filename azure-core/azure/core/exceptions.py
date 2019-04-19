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


def raise_with_traceback(exception, *args, **kwargs):
    # type: (Callable, Any, Any) -> None
    """Raise exception with a specified traceback.

    This MUST be called inside a "except" clause.

    :param Exception exception: Error type to be raised.
    :param args: Any additional args to be included with exception.
    :param kwargs: Keyword arguments to include with the exception.

    Keyword arguments:
    message Message to be associated with the exception. If omitted, defaults to an empty string.
    """
    message = kwargs.pop('message', '')
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
        self.exc_type, self.exc_value, self.exc_traceback = sys.exc_info()
        self.exc_type = self.exc_type.__name__ if self.exc_type else type(self.inner_exception)
        self.exc_msg = "{}, {}: {}".format(message, self.exc_type, self.exc_value)  # type: ignore
        self.message = str(message)
        super(AzureError, self).__init__(self.message, *args)

    def raise_with_traceback(self):
        try:
            raise super(AzureError, self).with_traceback(self.exc_traceback)
        except AttributeError:
            self.__traceback__ = self.exc_traceback
            raise self

class DecodeError(AzureError):
    """Error raised during response deserialization."""

class ServiceRequestError(AzureError):
    """An error occurred while attempt to make a request to the service."""


class ConnectError(ServiceRequestError):
    """An error occurred while attempting to establish the connection.
    These errors are safe to retry."""


class ServiceResponseError(AzureError):
    """The request was sent, but the client failed to understand the response.
    These errors may not be safe to retry"""


class ReadTimeoutError(ServiceResponseError):
    """The server did not send any data in the allotted amount of time.
    These errors may not be safe to retry."""


class HttpRequestError(ServiceRequestError):
    """A request was made, and a non-success status code was received from the service.

    :ivar status_code: HttpResponse's status code
    :ivar response: The response that triggered the exception.
    """

    def __init__(self, message=None, response=None, **kwargs):       
        self.reason = None
        if response:
            self.reason=response.reason
        message = "Operation returned an invalid status code {}".format(self.reason)
        try:
            try:
                if self.error.error.code or self.error.error.message:
                    message = "({}) {}".format(
                        self.error.error.code,
                        self.error.error.message)
            except AttributeError:
                if self.error.message:
                    message = self.error.message
        except AttributeError:
            pass
        super(HttpRequestError, self).__init__(message=message, response=response, **kwargs)

class ResourceExistsError(HttpRequestError):
    """An error response with status code 4xx.
    This will not be raised directly by the Azure core pipeline."""


class ResourceNotFoundError(HttpRequestError):
    """ An error response, typically triggered by a 412 response (for update) or 404 (for get/post)
    """


class ClientAuthenticationError(HttpRequestError):
    """An error response with status code 4xx.
    This will not be raised directly by the Azure core pipeline."""


class ResourceModifiedError(HttpRequestError):
    """An error response with status code 4xx, typically 412 Conflict.
    This will not be raised directly by the Azure core pipeline."""


class ServerError(HttpRequestError):
    """An error response with status code 5xx.
    This will not be raised directly by the Azure core pipeline."""


class TooManyRedirectsError(HttpRequestError):
    """Reached the maximum number of redirect attempts."""

    def __init__(self, history, *args, **kwargs):
        self.history = history
        message = "Reached maximum redirect attempts."
        super(TooManyRedirectsError, self).__init__(message, *args, **kwargs)

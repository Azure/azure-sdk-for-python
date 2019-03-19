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


class ClientException(Exception):
    """Base exception for all Client Runtime exceptions."""

    def __init__(self, message, inner_exception=None, *args, **kwargs):
        # type: (str, Any, str, str) -> None
        self.inner_exception = inner_exception
        _LOGGER.debug(message)
        super(ClientException, self).__init__(message, *args, **kwargs)  # type: ignore


class SerializationError(ClientException):
    """Error raised during request serialization."""
    pass


class DeserializationError(ClientException):
    """Error raised during response deserialization."""
    pass


class ValidationError(ClientException):
    """Request parameter validation failed."""

    _messages = {
        "min_length": "must have length greater than {!r}.",
        "max_length": "must have length less than {!r}.",
        "minimum": "must be greater than {!r}.",
        "maximum": "must be less than {!r}.",
        "minimum_ex": "must be equal to or greater than {!r}.",
        "maximum_ex": "must be equal to or less than {!r}.",
        "min_items": "must contain at least {!r} items.",
        "max_items": "must contain at most {!r} items.",
        "pattern": "must conform to the following pattern: {!r}.",
        "unique": "must contain only unique items.",
        "multiple": "must be a multiple of {!r}.",
        "required": "can not be None.",
        "type": "must be of type {!r}"
    }

    def __init__(self, rule, target, value, *args, **kwargs):
        # type: (str, str, str, str, str) -> None
        self.rule = rule
        self.target = target
        message = "Parameter {!r} ".format(target)
        reason = self._messages.get(
            rule, "failed to meet validation requirement.")
        message += reason.format(value)
        super(ValidationError, self).__init__(message, *args, **kwargs)


class ClientRequestError(ClientException):
    """Client request failed."""
    pass


class MaxRetryError(ClientException):

    def __init__(self, response, history, *args, **kwargs):
        self.history = history
        message = "Reached maximum retry attempts."
        if response:
            message += "Last error: [{}]{}".format(
                response.http_response.status_code,
                response.http_response.reason)
        super(MaxRetryError, self).__init__(message, *args, **kwargs)


class MaxRedirectError(ClientException):

    def __init__(self, history, *args, **kwargs):
        self.history = history
        message = "Reached maximum redirect attempts."
        super(MaxRedirectError, self).__init__(message, *args, **kwargs)


class ConnectionError(ClientException):
    pass


class AuthenticationError(ClientException):
    """Client request failed to authenticate."""
    pass


class TokenExpiredError(AuthenticationError):
    """OAuth token expired, request failed."""
    pass


class TokenInvalidError(AuthenticationError):
    """OAuth token invalid, request failed."""
    pass

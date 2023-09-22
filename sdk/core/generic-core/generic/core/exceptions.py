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
from __future__ import annotations
import sys

from types import TracebackType
from typing import (
    Any,
    Optional,
    Type,
    List,
    Mapping,
    TypeVar,
    Generic,
    TYPE_CHECKING,
)
from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from .pipeline.policies import RequestHistory

HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")
KeyType = TypeVar("KeyType")
ValueType = TypeVar("ValueType")


__all__ = [
    "ServiceError",
    "ServiceRequestError",
    "ServiceResponseError",
    "HttpResponseError",
    "DecodeError",
    "ResourceExistsError",
    "ResourceNotFoundError",
    "ClientAuthenticationError",
    "ResourceModifiedError",
    "ResourceNotModifiedError",
    "TooManyRedirectsError",
    "StreamConsumedError",
    "StreamClosedError",
    "ResponseNotReadError",
    "SerializationError",
    "DeserializationError",
]


@runtime_checkable
class _HttpResponseCommonAPI(Protocol):
    """Protocol used by exceptions for HTTP response.

    As HttpResponseError uses very few properties of HttpResponse, a protocol
    is faster and simpler than import all the possible types (at least 6).
    """

    @property
    def reason(self) -> Optional[str]:
        ...

    @property
    def status_code(self) -> Optional[int]:
        ...

    def text(self) -> str:
        ...

    @property
    def request(self) -> object:  # object as type, since all we need is str() on it
        ...


class ErrorMap(Generic[KeyType, ValueType]):
    """Error Map class. To be used in map_error method, behaves like a dictionary.
    It returns the error type if it is found in custom_error_map. Or return default_error

    :param dict custom_error_map: User-defined error map, it is used to map status codes to error types.
    :keyword error default_error: Default error type. It is returned if the status code is not found in custom_error_map
    """

    def __init__(
        self,  # pylint: disable=unused-argument
        custom_error_map: Optional[Mapping[KeyType, ValueType]] = None,
        *,
        default_error: Optional[ValueType] = None,
        **kwargs: Any,
    ) -> None:
        self._custom_error_map = custom_error_map or {}
        self._default_error = default_error

    def get(self, key: KeyType) -> Optional[ValueType]:
        ret = self._custom_error_map.get(key)
        if ret:
            return ret
        return self._default_error


def map_error(
    status_code: int, response: _HttpResponseCommonAPI, error_map: Mapping[int, Type[HttpResponseError]]
) -> None:
    if not error_map:
        return
    error_type = error_map.get(status_code)
    if not error_type:
        return
    error = error_type(response=response)
    raise error


class ServiceError(Exception):
    """Base exception for all errors.

    :param object message: The message object stringified as 'message' attribute
    :keyword error: The original exception if any
    :paramtype error: Exception

    :ivar inner_exception: The exception passed with the 'error' kwarg
    :vartype inner_exception: Exception
    :ivar exc_type: The exc_type from sys.exc_info()
    :ivar exc_value: The exc_value from sys.exc_info()
    :ivar exc_traceback: The exc_traceback from sys.exc_info()
    :ivar exc_msg: A string formatting of message parameter, exc_type and exc_value
    :ivar str message: A stringified version of the message parameter
    :ivar str continuation_token: A token reference to continue an incomplete operation. This value is optional
     and will be `None` where continuation is either unavailable or not applicable.
    """

    def __init__(self, message: Optional[object], *args: Any, **kwargs: Any) -> None:
        self.inner_exception: Optional[BaseException] = kwargs.get("error")

        exc_info = sys.exc_info()
        self.exc_type: Optional[Type[Any]] = exc_info[0]
        self.exc_value: Optional[BaseException] = exc_info[1]
        self.exc_traceback: Optional[TracebackType] = exc_info[2]

        self.exc_type = self.exc_type if self.exc_type else type(self.inner_exception)
        self.exc_msg: str = "{}, {}: {}".format(message, self.exc_type.__name__, self.exc_value)
        self.message: str = str(message)
        self.continuation_token: Optional[str] = kwargs.get("continuation_token")
        super(ServiceError, self).__init__(self.message, *args)

    def raise_with_traceback(self) -> None:
        """Raise the exception with the existing traceback.

        .. deprecated:: 1.22.0
           This method is deprecated as we don't support Python 2 anymore. Use raise/from instead.
        """
        try:
            raise super(ServiceError, self).with_traceback(self.exc_traceback)  # pylint: disable=raise-missing-from
        except AttributeError:
            self.__traceback__: Optional[TracebackType] = self.exc_traceback
            raise self  # pylint: disable=raise-missing-from


class ServiceRequestError(ServiceError):
    """An error occurred while attempt to make a request to the service.
    No request was sent.
    """


class ServiceResponseError(ServiceError):
    """The request was sent, but the client failed to understand the response.
    The connection may have timed out. These errors can be retried for idempotent or
    safe operations"""


class ServiceRequestTimeoutError(ServiceRequestError):
    """Error raised when timeout happens"""


class ServiceResponseTimeoutError(ServiceResponseError):
    """Error raised when timeout happens"""


class HttpResponseError(ServiceError):
    """A request was made, and a non-success status code was received from the service.

    :param object message: The message object stringified as 'message' attribute
    :param response: The response that triggered the exception.
    :type response: ~generic.core.pipeline.transport.HttpResponse or ~generic.core.pipeline.transport.AsyncHttpResponse

    :ivar reason: The HTTP response reason
    :vartype reason: str
    :ivar status_code: HttpResponse's status code
    :vartype status_code: int
    :ivar response: The response that triggered the exception.
    :vartype response: ~generic.core.pipeline.transport.HttpResponse or
        ~generic.core.pipeline.transport.AsyncHttpResponse
    """

    def __init__(
        self, message: Optional[object] = None, response: Optional[_HttpResponseCommonAPI] = None, **kwargs: Any
    ) -> None:

        self.reason: Optional[str] = None
        self.status_code: Optional[int] = None
        self.response: Optional[_HttpResponseCommonAPI] = response
        if response:
            self.reason = response.reason
            self.status_code = response.status_code

        # By priority, message is:
        # - parameter "message", OR
        # - generic meassage using "reason"
        message = message or "Operation returned an invalid status '{}'".format(self.reason)
        super(HttpResponseError, self).__init__(message=message, **kwargs)

    def __str__(self) -> str:
        retval = super(HttpResponseError, self).__str__()
        try:
            # https://github.com/python/mypy/issues/14743#issuecomment-1664725053
            body = self.response.text()  # type: ignore
            if body:
                return "{}\nContent: {}".format(retval, body)[:2048]
        except Exception:  # pylint: disable=broad-except
            pass
        return retval


class DecodeError(HttpResponseError):
    """Error raised during response deserialization."""


class IncompleteReadError(DecodeError):
    """Error raised if peer closes the connection before we have received the complete message body."""


class ResourceExistsError(HttpResponseError):
    """An error response with status code 4xx.
    This will not be raised directly by the core pipeline."""


class ResourceNotFoundError(HttpResponseError):
    """An error response, typically triggered by a 412 response (for update) or 404 (for get/post)"""


class ClientAuthenticationError(HttpResponseError):
    """An error response with status code 4xx.
    This will not be raised directly by the core pipeline."""


class ResourceModifiedError(HttpResponseError):
    """An error response with status code 4xx, typically 412 Conflict.
    This will not be raised directly by the core pipeline."""


class ResourceNotModifiedError(HttpResponseError):
    """An error response with status code 304.
    This will not be raised directly by the core pipeline."""


class TooManyRedirectsError(HttpResponseError, Generic[HTTPRequestType, HTTPResponseType]):
    """Reached the maximum number of redirect attempts.

    :param history: The history of requests made while trying to fulfill the request.
    :type history: list[~generic.core.pipeline.policies.RequestHistory]
    """

    def __init__(
        self, history: "List[RequestHistory[HTTPRequestType, HTTPResponseType]]", *args: Any, **kwargs: Any
    ) -> None:
        self.history = history
        message = "Reached maximum redirect attempts."
        super(TooManyRedirectsError, self).__init__(message, *args, **kwargs)


class StreamConsumedError(ServiceError):
    """Error thrown if you try to access the stream of a response once consumed.

    It is thrown if you try to read / stream an ~generic.core.rest.HttpResponse or
    ~generic.core.rest.AsyncHttpResponse once the response's stream has been consumed.

    :param response: The response that triggered the exception.
    :type response: ~generic.core.rest.HttpResponse or ~generic.core.rest.AsyncHttpResponse
    """

    def __init__(self, response: _HttpResponseCommonAPI) -> None:
        message = (
            "You are attempting to read or stream the content from request {}. "
            "You have likely already consumed this stream, so it can not be accessed anymore.".format(response.request)
        )
        super(StreamConsumedError, self).__init__(message)


class StreamClosedError(ServiceError):
    """Error thrown if you try to access the stream of a response once closed.

    It is thrown if you try to read / stream an ~generic.core.rest.HttpResponse or
    ~generic.core.rest.AsyncHttpResponse once the response's stream has been closed.

    :param response: The response that triggered the exception.
    :type response: ~generic.core.rest.HttpResponse or ~generic.core.rest.AsyncHttpResponse
    """

    def __init__(self, response: _HttpResponseCommonAPI) -> None:
        message = (
            "The content for response from request {} can no longer be read or streamed, since the "
            "response has already been closed.".format(response.request)
        )
        super(StreamClosedError, self).__init__(message)


class ResponseNotReadError(ServiceError):
    """Error thrown if you try to access a response's content without reading first.

    It is thrown if you try to access an ~generic.core.rest.HttpResponse or
    ~generic.core.rest.AsyncHttpResponse's content without first reading the response's bytes in first.

    :param response: The response that triggered the exception.
    :type response: ~generic.core.rest.HttpResponse or ~generic.core.rest.AsyncHttpResponse
    """

    def __init__(self, response: _HttpResponseCommonAPI) -> None:
        message = (
            "You have not read in the bytes for the response from request {}. "
            "Call .read() on the response first.".format(response.request)
        )
        super(ResponseNotReadError, self).__init__(message)


class SerializationError(ValueError):
    """Raised if an error is encountered during serialization."""


class DeserializationError(ValueError):
    """Raised if an error is encountered during deserialization."""

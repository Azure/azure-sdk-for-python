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

import abc
from typing import TypeVar, Generic

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")

try:
    from contextlib import (  # pylint: disable=unused-import
        AbstractContextManager,
    )  # type: ignore
except ImportError:  # Python <= 3.5

    class AbstractContextManager(object):  # type: ignore
        def __enter__(self):
            """Return `self` upon entering the runtime context."""
            return self

        @abc.abstractmethod
        def __exit__(self, exc_type, exc_value, traceback):
            """Raise any exception triggered within the runtime context."""
            return None


class PipelineContext(dict):
    """A context object carried by the pipeline request and response containers.

    This is transport specific and can contain data persisted between
    pipeline requests (for example reusing an open connection pool or "session"),
    as well as used by the SDK developer to carry arbitrary data through
    the pipeline.

    :param transport: The HTTP transport type.
    :param kwargs: Developer-defined keyword arguments.
    """

    def __init__(self, transport, **kwargs):  # pylint: disable=super-init-not-called
        self.transport = transport
        self.options = kwargs
        self._protected = ["transport", "options"]

    def __setitem__(self, key, item):
        if key in self._protected:
            raise ValueError("Context value {} cannot be overwritten.".format(key))
        return super(PipelineContext, self).__setitem__(key, item)

    def __delitem__(self, key):
        if key in self._protected:
            raise ValueError("Context value {} cannot be deleted.".format(key))
        return super(PipelineContext, self).__delitem__(key)

    def clear(self):
        """Context objects cannot be cleared.

        :raises: TypeError
        """
        raise TypeError("Context objects cannot be cleared.")

    def update(self, *args, **kwargs):
        """Context objects cannot be updated.

        :raises: TypeError
        """
        raise TypeError("Context objects cannot be updated.")

    def pop(self, *args):
        """Removes specified key and returns the value.
        """
        if args and args[0] in self._protected:
            raise ValueError("Context value {} cannot be popped.".format(args[0]))
        return super(PipelineContext, self).pop(*args)


class PipelineRequest(Generic[HTTPRequestType]):
    """A pipeline request object.

    Container for moving the HttpRequest through the pipeline.
    Universal for all transports, both synchronous and asynchronous.

    :param http_request: The request object.
    :type http_request: ~azure.core.pipeline.transport.HttpRequest
    :param context: Contains the context - data persisted between pipeline requests.
    :type context: ~azure.core.pipeline.PipelineContext
    """

    def __init__(self, http_request, context):
        # type: (HTTPRequestType, PipelineContext) -> None
        self.http_request = http_request
        self.context = context


class PipelineResponse(Generic[HTTPRequestType, HTTPResponseType]):
    """A pipeline response object.

    The PipelineResponse interface exposes an HTTP response object as it returns through the pipeline of Policy objects.
    This ensures that Policy objects have access to the HTTP response.

    This also has a "context" object where policy can put additional fields.
    Policy SHOULD update the "context" with additional post-processed field if they create them.
    However, nothing prevents a policy to actually sub-class this class a return it instead of the initial instance.

    :param http_request: The request object.
    :type http_request: ~azure.core.pipeline.transport.HttpRequest
    :param http_response: The response object.
    :type http_response: ~azure.core.pipeline.transport.HttpResponse
    :param context: Contains the context - data persisted between pipeline requests.
    :type context: ~azure.core.pipeline.PipelineContext
    """

    def __init__(self, http_request, http_response, context):
        # type: (HTTPRequestType, HTTPResponseType, PipelineContext) -> None
        self.http_request = http_request
        self.http_response = http_response
        self.context = context


from ._base import Pipeline  # pylint: disable=wrong-import-position

__all__ = ["Pipeline", "PipelineRequest", "PipelineResponse", "PipelineContext"]

try:
    from ._base_async import AsyncPipeline  # pylint: disable=unused-import

    __all__.append("AsyncPipeline")
except (SyntaxError, ImportError):
    pass  # Asynchronous pipelines not supported.

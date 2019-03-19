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

try:
    ABC = abc.ABC
except AttributeError: # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})  # type: ignore

try:
    from contextlib import AbstractContextManager  # type: ignore
except ImportError: # Python <= 3.5
    class AbstractContextManager(object):  # type: ignore
        def __enter__(self):
            """Return `self` upon entering the runtime context."""
            return self

        @abc.abstractmethod
        def __exit__(self, exc_type, exc_value, traceback):
            """Raise any exception triggered within the runtime context."""
            return None


class PipelineRequest(object):
    """Represents a HTTP request in a Pipeline.

    URL can be given without query parameters, to be added later using "format_parameters".

    Instance can be created without data, to be added later using "add_content"

    Instance can be created without files, to be added later using "add_formdata"

    :param str method: HTTP method (GET, HEAD, etc.)
    :param str url: At least complete scheme/host/path
    :param dict[str,str] headers: HTTP headers
    :param files: Files list.
    :param data: Body to be sent.
    :type data: bytes or str.
    """
    def __init__(self, http_request, context=None):
        # type: (HTTPRequestType, Optional[Any]) -> None
        self.http_request = http_request
        self.context = context


class PipelineResponse(object):
    """A pipeline response object.

    The PipelineResponse interface exposes an HTTP response object as it returns through the pipeline of Policy objects.
    This ensures that Policy objects have access to the HTTP response.

    This also have a "context" dictionnary where policy can put additional fields.
    Policy SHOULD update the "context" dictionary with additional post-processed field if they create them.
    However, nothing prevents a policy to actually sub-class this class a return it instead of the initial instance.
    """
    def __init__(self, http_request, http_response, context=None):
        # type: (HttpRequest[HTTPRequestType], HTTPResponseType, Optional[Dict[str, Any]]) -> None
        self.http_request = http_request
        self.http_response = http_response
        self.context = context or {}


from .base import Pipeline

__all__ = [
    'Pipeline',
    'PipelineRequest',
    'PipelineResponse'
]

try:
    from .base_async import AsyncPipeline
    __all__.append('AsyncPipeline')
except (SyntaxError, ImportError):
    pass  # Asynchronous pipelines not supported.



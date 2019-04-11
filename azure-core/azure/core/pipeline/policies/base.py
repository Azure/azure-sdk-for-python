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
import copy
import logging

from typing import TYPE_CHECKING, Generic, TypeVar, cast, IO, List, Union, Any, Mapping, Dict, Optional, Tuple, Callable, Iterator  # pylint: disable=unused-import

from azure.core.pipeline import ABC

HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")

_LOGGER = logging.getLogger(__name__)


class HTTPPolicy(ABC, Generic[HTTPRequestType, HTTPResponseType]):
    """An HTTP policy ABC.
    """
    def __init__(self):
        self.next = None

    @abc.abstractmethod
    def send(self, request):
        # type: (PipelineRequest[HTTPRequestType]) -> PipelineResponse[HTTPRequestType, HTTPResponseType]
        """Mutate the request.

        Context content is dependent on the HttpTransport.
        """
        pass

class SansIOHTTPPolicy(Generic[HTTPRequestType, HTTPResponseType]):
    """Represents a sans I/O policy.

    This policy can act before the I/O, and after the I/O.
    Use this policy if the actual I/O in the middle is an implementation
    detail.

    Context is not available, since it's implementation dependent.
    if a policy needs a context of the Sender, it can't be universal.

    Example: setting a UserAgent does not need to be tied to
    sync or async implementation or specific HTTP lib
    """

    def on_request(self, request, **kwargs):
        # type: (PipelineRequest[HTTPRequestType], Any) -> None
        """Is executed before sending the request to next policy.
        """
        pass

    def on_response(self, request, response, **kwargs):
        # type: (PipelineRequest[HTTPRequestType], PipelineResponse[HTTPRequestType, HTTPResponseType], Any) -> None
        """Is executed after the request comes back from the policy.
        """
        pass

    def on_exception(self, request, **kwargs):
        # type: (PipelineRequest[HTTPRequestType], Any) -> bool
        """Is executed if an exception comes back fron the following
        policy.

        Return True if the exception has been handled and should not
        be forwarded to the caller.

        This method is executed inside the exception handler.
        To get the exception, raise and catch it:

            try:
                raise
            except MyError:
                do_something()

        or use

            exc_type, exc_value, exc_traceback = sys.exc_info()
        """
        return False


class RequestHistory(object):
    """A container for an attempted request and the applicable response.

    This is used to document requests/responses that resulted in redirected requests.
    """
 
    def __init__(self, http_request, http_response=None, error=None, context=None):
        # type: (PipelineRequest[HTTPRequestType], Exception, Optional[Dict[str, Any]]) -> None
        self.http_request = copy.deepcopy(http_request)
        self.http_response = http_response
        self.error = error
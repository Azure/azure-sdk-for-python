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

from ._helpers import HttpVerbs
try:
    from ._rest_py3 import (
        HttpRequest,
        HttpResponse,
        StreamConsumedError,
        ResponseNotReadError,
        ResponseClosedError,
    )
except (SyntaxError, ImportError):
    from ._rest import (  # type: ignore
        HttpRequest,
        HttpResponse,
        StreamConsumedError,
        ResponseNotReadError,
        ResponseClosedError,
    )

__all__ = [
    "HttpVerbs",
    "HttpRequest",
    "HttpResponse",
    "StreamConsumedError",
    "ResponseNotReadError",
    "ResponseClosedError",
]

try:
    from ._rest_py3 import (  # pylint: disable=unused-import
        AsyncHttpResponse,
        _AsyncContextManager,
    )

    __all__.extend([
        "AsyncHttpResponse",
        "_AsyncContextManager",
    ])
except (SyntaxError, ImportError):
    pass

#### FOR BUGBASH

from ._sync_test_client import TestRestClient  # pylint: disable=unused-import
__all__.extend(["TestRestClient"])
try:
    from ._async_test_client import AsyncTestRestClient  # pylint: disable=unused-import
    __all__.extend(["AsyncTestRestClient"])
except (SyntaxError, ImportError):
    pass

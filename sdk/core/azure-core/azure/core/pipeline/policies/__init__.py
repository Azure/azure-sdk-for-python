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

from .base import HTTPPolicy, SansIOHTTPPolicy
from .authentication import BearerTokenCredentialPolicy
from .custom_hook import CustomHookPolicy
from .redirect import RedirectPolicy
from .retry import RetryPolicy
from .universal import (
    HeadersPolicy,
    UserAgentPolicy,
    NetworkTraceLoggingPolicy,
    ContentDecodePolicy,
    ProxyPolicy
)

__all__ = [
    'HTTPPolicy',
    'SansIOHTTPPolicy',
    'BearerTokenCredentialPolicy',
    'HeadersPolicy',
    'UserAgentPolicy',
    'NetworkTraceLoggingPolicy',
    'ContentDecodePolicy',
    'RetryPolicy',
    'RedirectPolicy',
    'ProxyPolicy',
    'CustomHookPolicy'
]

#pylint: disable=unused-import

try:
    from .base_async import AsyncHTTPPolicy
    from .authentication_async import AsyncBearerTokenCredentialPolicy
    from .redirect_async import AsyncRedirectPolicy
    from .retry_async import AsyncRetryPolicy
    __all__.extend([
        'AsyncHTTPPolicy',
        'AsyncBearerTokenCredentialPolicy',
        'AsyncRedirectPolicy',
        'AsyncRetryPolicy'
    ])
except (ImportError, SyntaxError):
    pass  # Async not supported

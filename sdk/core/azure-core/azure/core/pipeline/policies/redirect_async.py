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
from typing import Any, Callable, Optional

from azure.core.exceptions import TooManyRedirectsError
from . import AsyncHTTPPolicy
from .redirect import RedirectPolicy


class AsyncRedirectPolicy(RedirectPolicy, AsyncHTTPPolicy):
    """An async redirect policy.

    An async redirect policy in the pipeline can be configured directly or per operation.

    .. code-block:: python

        config = FooService.create_config()

        # Client allows redirects. Defaults to True.
        config.redirect_policy.allow = True

        # The maximum allowed redirects. The default value is 30
        config.redirect_policy.max_redirects = 10

        # It can also be overridden per operation.
        result = client.get_operation(redirects_allow=True, redirect_max=5)

        # Alternatively you can disable redirects entirely
        from azure.core.pipeline.policies import AsyncRedirectPolicy
        config.redirect_policy = AsyncRedirectPolicy.no_redirects()

    Keyword arguments:
    :param redirects_allow: Whether the client allows redirects. Defaults to True.
    :param redirect_max: The maximum allowed redirects. Defaults to 30.
    """

    async def send(self, request):
        """Sends the PipelineRequest object to the next policy. Uses redirect settings
        to send the request to redirect endpoint if necessary.

        :param request: The PipelineRequest object
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: Returns the PipelineResponse or raises error if maximum redirects exceeded.
        :rtype: ~azure.core.pipeline.PipelineResponse
        :raises: ~azure.core.exceptions.TooManyRedirectsError if maximum redirects exceeded.
        """
        redirects_remaining = True
        redirect_settings = self.configure_redirects(request.context.options)
        while redirects_remaining:
            response = await self.next.send(request)
            redirect_location = self.get_redirect_location(response)
            if redirect_location:
                redirects_remaining = self.increment(redirect_settings, response, redirect_location)
                request.http_request = response.http_request
                continue
            return response

        raise TooManyRedirectsError(redirect_settings['history'])

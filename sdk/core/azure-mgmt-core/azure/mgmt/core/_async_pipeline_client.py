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
from azure.core import AsyncPipelineClient
from azure.core.pipeline.policies import (
    ContentDecodePolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    RequestIdPolicy,
)
from .policies import AsyncARMAutoResourceProviderRegistrationPolicy


class AsyncARMPipelineClient(AsyncPipelineClient):
    """A pipeline client designed for ARM explicitly.

    :param str base_url: URL for the request.
    :keyword AsyncPipeline pipeline: If omitted, a Pipeline object is created and returned.
    :keyword list[HTTPPolicy] policies: If omitted, the standard policies of the configuration object is used.
    :keyword HttpTransport transport: If omitted, RequestsTransport is used for synchronous transport.
    """

    def __init__(self, base_url, **kwargs):
        if "policies" not in kwargs:
            if "config" not in kwargs:
                raise ValueError(
                    "Current implementation requires to pass 'config' if you don't pass 'policies'"
                )
            kwargs["policies"] = self._default_policies(**kwargs)
        super(AsyncARMPipelineClient, self).__init__(base_url, **kwargs)

    @staticmethod
    def _default_policies(config, **kwargs):
        return [
            RequestIdPolicy(**kwargs),
            AsyncARMAutoResourceProviderRegistrationPolicy(),
            config.headers_policy,
            config.user_agent_policy,
            config.proxy_policy,
            ContentDecodePolicy(**kwargs),
            config.redirect_policy,
            config.retry_policy,
            config.authentication_policy,
            config.custom_hook_policy,
            config.logging_policy,
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
        ]

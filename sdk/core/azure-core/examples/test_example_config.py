# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------


# [START configuration]
from azure.core import Configuration
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import RequestsTransport
from azure.core.pipeline.policies import (
    HeadersPolicy,
    BearerTokenCredentialPolicy,
    UserAgentPolicy,
    RetryPolicy,
    RedirectPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    ContentDecodePolicy
)

# Example class to create configuration for a service client
class FooServiceClient():

    @staticmethod
    def _create_config(credential, scopes, **kwargs):
        # Here the SDK developer would define the default
        # config to interact with the service
        config = Configuration(**kwargs)
        config.headers_policy = kwargs.get('headers_policy', HeadersPolicy({"CustomHeader": "Value"}, **kwargs))
        config.user_agent_policy = kwargs.get('user_agent_policy', UserAgentPolicy("ServiceUserAgentValue", **kwargs))
        config.authentication_policy = kwargs.get('authentication_policy', BearerTokenCredentialPolicy(credential, scopes, **kwargs))
        config.retry_policy = kwargs.get('retry_policy', RetryPolicy(**kwargs))
        config.redirect_policy = kwargs.get('redirect_policy', RedirectPolicy(**kwargs))
        config.logging_policy = kwargs.get('logging_policy', NetworkTraceLoggingPolicy(**kwargs))
        config.proxy_policy = kwargs.get('proxy_policy', ProxyPolicy(**kwargs))
        return config

    def __init__(self, **kwargs):
        transport = kwargs.get('transport', RequestsTransport(**kwargs))
        config = FooServiceClient._create_config(**kwargs)
        policies = [
            config.user_agent_policy,
            config.headers_policy,
            config.authentication_policy,
            ContentDecodePolicy(),
            config.proxy_policy,
            config.redirect_policy,
            config.retry_policy,
            config.logging_policy,
        ]
        self._pipeline = Pipeline(transport, policies=policies)
# [END configuration]


def example_connection_config():

    # [START connection_configuration]
    from azure.core import Configuration

    config = Configuration(
        connection_timeout=100,
        connection_verify=True,
        connection_cert=None,
        connection_data_block_size=4096
    )

    # Or parameters can be tweaked later:
    config.connection.timeout = 100
    config.connection.verify = True
    config.connection.cert = None
    config.connection.data_block_size = 4096
    # [END connection_configuration]

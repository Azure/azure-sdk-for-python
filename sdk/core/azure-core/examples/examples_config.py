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


from azure.core.configuration import Configuration
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import HeadersPolicy
from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from azure.core.pipeline.policies import UserAgentPolicy
from azure.core.pipeline.policies import RetryPolicy
from azure.core.pipeline.policies import RedirectPolicy
from azure.core.pipeline.policies import NetworkTraceLoggingPolicy
from azure.core.pipeline.policies import ProxyPolicy
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.transport import RequestsTransport


# [START configuration]

# Example of configuration for a service client
class FooServiceClient():

    @staticmethod
    def create_config(credential, scopes, **kwargs):
        # Here the SDK developer would define the default
        # config to interact with the service
        config = Configuration(**kwargs)
        config.headers_policy = HeadersPolicy({"CustomHeader": "Value"}, **kwargs)
        config.authentication_policy = BearerTokenCredentialPolicy(credential, scopes, **kwargs)
        config.user_agent_policy = UserAgentPolicy("ServiceUserAgentValue", **kwargs)
        config.retry_policy = RetryPolicy(**kwargs)
        config.redirect_policy = RedirectPolicy(**kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.proxy_policy = ProxyPolicy(**kwargs)
        config.transport = kwargs.get('transport', RequestsTransport)

    def __init__(self, configuration=None, **kwargs):
        config = configuration or FooServiceClient.create_config(**kwargs)
        transport = config.get_transport(**kwargs)
        policies = [
            config.user_agent_policy,
            config.headers_policy,
            config.authentication_policy,
            ContentDecodePolicy(),
            config.redirect_policy,
            config.retry_policy,
            config.logging_policy,
        ]
        self._pipeline = Pipeline(transport, policies=policies)
# [END configuration]


def example_connection_config():

    # [START connection_configuration]
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

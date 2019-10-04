#--------------------------------------------------------------------------
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
#--------------------------------------------------------------------------

import sys
from azure.core.configuration import Configuration
from azure.core.pipeline.transport import HttpRequest
from azure.core import PipelineClient
from azure.core.pipeline.policies import RedirectPolicy
from azure.core.pipeline.policies import UserAgentPolicy
from azure.core.pipeline.policies import SansIOHTTPPolicy


def test_example_headers_policy():
    url = "https://bing.com"
    config = Configuration()
    config.user_agent_policy = UserAgentPolicy("myusergant")
    config.redirect_policy = RedirectPolicy()

    # [START headers_policy]
    from azure.core.pipeline.policies import HeadersPolicy

    config.headers_policy = HeadersPolicy()
    config.headers_policy.add_header('CustomValue', 'Foo')

    # Or headers can be added per operation. These headers will supplement existing headers
    # or those defined in the config headers policy. They will also overwrite existing
    # identical headers.
    client = PipelineClient(base_url=url, config=config)
    request = client.get(url)
    pipeline_response = client._pipeline.run(request, headers={'CustomValue': 'Bar'})
    # [END headers_policy]

    response = pipeline_response.http_response
    assert response.status_code == 200


def test_example_user_agent_policy():
    url = "https://bing.com"
    config = Configuration()
    config.redirect_policy = RedirectPolicy()

    # [START user_agent_policy]
    from azure.core.pipeline.policies import UserAgentPolicy

    config.user_agent_policy = UserAgentPolicy()

    # The user-agent policy allows you to append a custom value to the header.
    config.user_agent_policy.add_user_agent("CustomValue")

    # You can also pass in a custom value per operation to append to the end of the user-agent.
    # This can be used together with the policy configuration to append multiple values.
    client = PipelineClient(base_url=url, config=config)
    request = client.get(url)
    pipeline_response = client._pipeline.run(request, user_agent="AnotherValue")
    # [END user_agent_policy]

    response = pipeline_response.http_response
    assert response.status_code == 200


def example_network_trace_logging():
    filename = "log.txt"
    url = "https://bing.com"
    config = Configuration()
    config.redirect_policy = RedirectPolicy()

    # [START network_trace_logging_policy]
    from azure.core.pipeline.policies import NetworkTraceLoggingPolicy
    import sys
    import logging

    # Create a logger for the 'azure' SDK
    logger = logging.getLogger("azure")
    logger.setLevel(logging.DEBUG)

    # Configure a console output
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)

    # Configure a file output
    file_handler = logging.FileHandler(filename)
    logger.addHandler(file_handler)

    # Enable network trace logging. This will be logged at DEBUG level.
    # By default, logging is disabled.
    config.logging_policy = NetworkTraceLoggingPolicy()
    config.logging_policy.enable_http_logger = True

    # The logger can also be enabled per operation.
    client = PipelineClient(base_url=url, config=config)
    request = client.get(url)
    pipeline_response = client._pipeline.run(request, logging_enable=True)

    # [END network_trace_logging_policy]
    response = pipeline_response.http_response
    assert response.status_code == 200

def example_proxy_policy():

    # [START proxy_policy]
    from azure.core.pipeline.policies import ProxyPolicy

    config = Configuration()
    config.proxy_policy = ProxyPolicy()

    # Example
    config.proxy_policy.proxies = {'http': 'http://10.10.1.10:3148'}

    # Use basic auth
    config.proxy_policy.proxies = {'https': 'http://user:password@10.10.1.10:1180/'}

    # You can also configure proxies by setting the environment variables
    # HTTP_PROXY and HTTPS_PROXY.
    # [END proxy_policy]

def example_on_exception():
    policy = SansIOHTTPPolicy()
    request = HttpRequest("GET", "https://bing.com")
    # [START on_exception]
    try:
        response = policy.next.send(request)
    except Exception:
        if not policy.on_exception(request):
            raise

    # or use
    exc_type, exc_value, exc_traceback = sys.exc_info()
    # [END on_exception]

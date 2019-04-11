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


class Configuration(object):

    def __init__(self, transport=None, **kwargs):
        # Communication configuration - applied per transport.
        self.connection = ConnectionConfiguration(**kwargs)

        # Headers (sent with every request)
        self.headers_policy = None

        # Proxy settings (Currently used to configure transport, could be pipeline policy instead)
        self.proxy_policy = None
 
        # Redirect configuration
        self.redirect_policy = None

        # Retry configuration
        self.retry_policy = None

        # Logger configuration
        self.logging_policy = None

        # User Agent configuration
        self.user_agent_policy = None

        # HTTP Transport
        self.transport = transport

    def get_transport(self, **kwargs):
        if self.transport:
            return self.transport(configuration=self, **kwargs)


class ConnectionConfiguration(object):
    """HTTP transport connection configuration settings."""

    def __init__(self, **kwargs):
        self.timeout = kwargs.pop('connection_timeout', 100)
        self.verify = kwargs.pop('connection_verify', True)
        self.cert = kwargs.pop('connection_cert', None)
        self.data_block_size = kwargs.pop('connection_data_block_size', 4096)
        self.keep_alive = kwargs.pop('connection_keep_alive', True)

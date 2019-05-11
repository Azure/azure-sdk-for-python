# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from uamqp import constants
from azure.eventhub.policies import *


class Configuration(object):
    def __init__(self, **kwargs):
        self.user_agent_policy = UserAgentPolicy(**kwargs)
        self.retry_policy = RetryPolicy(**kwargs)
        self.redirect_policy = RedirectPolicy(**kwargs)
        self.network_trace_policy = NetworkTraceLoggingPolicy(**kwargs)
        self.http_proxy_policy = ProxyPolicy(**kwargs)
        self.auto_reconnect_policy = AutoReconnectPolicy(**kwargs)
        self.keep_alive_policy = KeepAlivePolicy(**kwargs)
        self.transport_type = constants.TransportType.AmqpOverWebsocket if self.http_proxy_policy.http_proxy \
            else kwargs.get("transport_type", constants.TransportType.Amqp)
        self.auth_timeout = kwargs.get("auth_timeout", 60)

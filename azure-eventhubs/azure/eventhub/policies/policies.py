# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from .base import AMQPClientPolicy
from uamqp import AMQPClient


class RetryPolicy(AMQPClientPolicy):

    def __init__(self, **kwargs):
        self.max_retries = kwargs.get("max_retries", 3)

    def apply(self, amqp_client):  # type: (AMQPClient) -> None
        raise NotImplementedError("Placeholder for future implementation")


class ProxyPolicy(AMQPClientPolicy):
    def __init__(self, **kwargs):
        self.http_proxy = kwargs.get("http_proxy")

    def apply(self, amqp_client):  # type: (AMQPClient) -> None
        raise NotImplementedError("Placeholder for future implementation")


class AutoReconnectPolicy(AMQPClientPolicy):
    def __init__(self, **kwargs):
        self.auto_reconnect = kwargs.get("auto_reconnect", True)

    def apply(self, amqp_client):  # type: (AMQPClient) -> None
        raise NotImplementedError("Placeholder for future implementation")


class KeepAlivePolicy(AMQPClientPolicy):
    def __init__(self, **kwargs):
        self.keep_alive = kwargs.get("keep_alive", 30)

    def apply(self, amqp_client):  # type: (AMQPClient) -> None
        raise NotImplementedError("Placeholder for future implementation")


class UserAgentPolicy(AMQPClientPolicy):
    def __init__(self, **kwargs):
        self.user_agent = kwargs.get("user_agent")

    def apply(self, amqp_client):  # type: (AMQPClient) -> None
        raise NotImplementedError("Placeholder for future implementation")


class NetworkTraceLoggingPolicy(AMQPClientPolicy):
    def __init__(self, **kwargs):
        self.network_trace_logging = kwargs.get("debug", False)

    def apply(self, amqp_client):  # type: (AMQPClient) -> None
        raise NotImplementedError("Placeholder for future implementation")


class RedirectPolicy(AMQPClientPolicy):
    def __init__(self, **kwargs):
        self.redirect = kwargs.get("redirect")

    def apply(self, amqp_client):  # type: (AMQPClient) -> None
        raise NotImplementedError("Placeholder for future implementation")

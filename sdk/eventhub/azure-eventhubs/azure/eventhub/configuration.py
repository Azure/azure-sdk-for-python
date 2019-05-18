# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from uamqp.constants import TransportType


class Configuration(object):
    def __init__(self, **kwargs):
        self.user_agent = kwargs.get("user_agent")
        self.max_retries = kwargs.get("max_retries", 3)
        self.network_tracing = kwargs.get("debug", False)
        self.http_proxy = kwargs.get("http_proxy")
        self.auto_reconnect = kwargs.get("auto_reconnect", False)
        self.keep_alive = kwargs.get("keep_alive", 1)
        self.transport_type = TransportType.AmqpOverWebsocket if self.http_proxy \
            else kwargs.get("transport_type", TransportType.Amqp)
        self.auth_timeout = kwargs.get("auth_timeout", 60)
        self.prefetch = kwargs.get("prefetch")
        self.send_timeout = kwargs.get("send_timeout", 60)

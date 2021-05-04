# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Optional, Dict, Any

from uamqp.constants import TransportType


class Configuration(object):  # pylint:disable=too-many-instance-attributes
    def __init__(self, **kwargs):
        self.user_agent = kwargs.get("user_agent")  # type: Optional[str]
        self.retry_total = kwargs.get("retry_total", 3)  # type: int
        self.retry_backoff_factor = kwargs.get(
            "retry_backoff_factor", 0.8
        )  # type: float
        self.retry_backoff_max = kwargs.get("retry_backoff_max", 120)  # type: int
        self.logging_enable = kwargs.get("logging_enable", False)  # type: bool
        self.http_proxy = kwargs.get("http_proxy")  # type: Optional[Dict[str, Any]]
        self.transport_type = (
            TransportType.AmqpOverWebsocket
            if self.http_proxy
            else kwargs.get("transport_type", TransportType.Amqp)
        )
        # The following configs are not public, for internal usage only
        self.auth_timeout = kwargs.get("auth_timeout", 60)  # type: int
        self.encoding = kwargs.get("encoding", "UTF-8")
        self.auto_reconnect = kwargs.get("auto_reconnect", True)
        self.keep_alive = kwargs.get("keep_alive", 30)
        self.timeout = kwargs.get("timeout", 60)  # type: float

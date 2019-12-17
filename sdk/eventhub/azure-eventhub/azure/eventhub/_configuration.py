# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Optional, Dict

from uamqp.constants import TransportType


class Configuration(object):  # pylint:disable=too-many-instance-attributes
    def __init__(self, **kwargs):
        self.user_agent = kwargs.get("user_agent")  # type: Optional[str]
        self.retry_total = kwargs.get("retry_total", 3)  # type: int
        self.max_retries = self.retry_total  # type: int
        self.backoff_factor = kwargs.get("retry_backoff_factor", 0.8)  # type: float
        self.backoff_max = kwargs.get("retry_backoff_max", 120)  # type: int
        self.network_tracing = kwargs.get("network_tracing", False)  # type: bool
        self.http_proxy = kwargs.get("http_proxy")  # type: Optional[Dict[str, Any]]
        self.transport_type = (
            TransportType.AmqpOverWebsocket
            if self.http_proxy
            else kwargs.get("transport_type", TransportType.Amqp)
        )
        self.auth_timeout = kwargs.get("auth_timeout", 60)  # type: int
        self.prefetch = kwargs.get("prefetch", 300)  # type: int
        self.max_batch_size = kwargs.get("max_batch_size", self.prefetch)  # type: int
        self.receive_timeout = kwargs.get("receive_timeout", 0)  # type: int
        self.send_timeout = kwargs.get("send_timeout", 60)  # type: int

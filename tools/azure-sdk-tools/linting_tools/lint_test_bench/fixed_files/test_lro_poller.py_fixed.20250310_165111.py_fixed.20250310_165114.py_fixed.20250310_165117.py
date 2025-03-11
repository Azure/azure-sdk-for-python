# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Dict, List, Any
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

# This code violates client-lro-methods-use-polling and client-method-missing-tracing-decoration

class Some1Client():
    @distributed_trace
    def begin_thing(self, **kwargs) -> "LROPoller[None]":
        polling = kwargs.pop('polling', True)
        return LROPoller(self, None, polling=polling, **kwargs)

    @distributed_trace
    def begin_thing2(self, **kwargs) -> "LROPoller[None]":
        polling = kwargs.pop('polling', True)
        return LROPoller(self, None, polling=polling, **kwargs)


class Some2Client():
    @distributed_trace
    def begin_thing(self, **kwargs) -> "LROPoller[None]":
        polling = kwargs.pop('polling', True)
        return LROPoller(self, None, polling=polling, **kwargs)

    @distributed_trace
    def begin_thing2(self, **kwargs) -> "LROPoller[None]":
        polling = kwargs.pop('polling', True)
        return LROPoller(self, None, polling=polling, **kwargs)

    @distributed_trace
    def poller(self, **kwargs) -> "LROPoller[None]":
        polling = kwargs.pop('polling', True)
        return LROPoller(self, None, polling=polling, **kwargs)

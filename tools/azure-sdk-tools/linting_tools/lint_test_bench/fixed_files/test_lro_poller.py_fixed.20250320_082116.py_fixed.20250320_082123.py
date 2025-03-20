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
    def begin_thing(self, **kwargs) -> LROPoller:
        # Ensure the method uses polling
        poller = LROPoller(self, kwargs.get("some_key"), kwargs.get("some_other_key"), kwargs.get("some_third_key"))
        return poller

    @distributed_trace
    def begin_thing2(self, **kwargs) -> LROPoller:
        # Ensure the method uses polling
        poller = LROPoller(self, kwargs.get("some_key"), kwargs.get("some_other_key"), kwargs.get("some_third_key"))
        return poller


class Some2Client():
    def begin_thing(self) -> List[str]:
        return []

    @distributed_trace
    def begin_thing2(self) -> Dict[str, Any]:
        return {}
    
    @distributed_trace
    def poller(self, **kwargs) -> LROPoller:
        return LROPoller(self, kwargs.get("some_key"), kwargs.get("some_other_key"), kwargs.get("some_third_key"))

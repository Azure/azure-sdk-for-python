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
    def begin_thing(self, polling: bool=True, **kwargs) -> LROPoller:
        if polling:
            return LROPoller(self, kwargs.get("some_key"), kwargs.get("some_other_key"), kwargs.get("some_third_key"))
        return LROPoller(self, kwargs.get("some_key"), kwargs.get("some_other_key"), kwargs.get("some_third_key"))

    @distributed_trace
    def begin_thing2(self, polling: bool=True, **kwargs) -> LROPoller:
        if polling:
            return LROPoller(self, kwargs.get("some_key"), kwargs.get("some_other_key"), kwargs.get("some_third_key"))
        return LROPoller(self, kwargs.get("some_key"), kwargs.get("some_other_key"), kwargs.get("some_third_key"))

class Some2Client():
    @distributed_trace
    def get_thing(self) -> List[str]:  # Renamed to follow guidelines
        return []

    @distributed_trace
    def get_thing2(self) -> Dict[str, Any]:  # Renamed to follow guidelines
        return {}

    @distributed_trace
    def begin_thing3(self, polling: bool=True, **kwargs) -> LROPoller:  # Method renamed to follow LRO naming convention
        if polling:
            return LROPoller(self, kwargs.get("some_key"), kwargs.get("some_other_key"), kwargs.get("some_third_key"))
        return LROPoller(self, kwargs.get("some_key"), kwargs.get("some_other_key"), kwargs.get("some_third_key"))

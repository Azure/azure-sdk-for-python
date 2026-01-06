# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC
from typing import ContextManager


class HostedAgentContext(ContextManager["HostedAgentContext"], ABC):
    pass


class HostedAgentContextConfigurer(ABC):
    pass

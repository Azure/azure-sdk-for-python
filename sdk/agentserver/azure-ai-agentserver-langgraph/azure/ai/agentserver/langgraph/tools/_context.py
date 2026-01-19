# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from dataclasses import dataclass, field

from ._resolver import ResolvedTools


@dataclass
class FoundryToolContext:
    """Context for tool resolution.

    :param resolved_tools: The resolved tools of all registered foundry tools.
    :type resolved_tools: ResolvedTools
    """
    resolved_tools: ResolvedTools = field(default_factory=lambda: ResolvedTools([]))

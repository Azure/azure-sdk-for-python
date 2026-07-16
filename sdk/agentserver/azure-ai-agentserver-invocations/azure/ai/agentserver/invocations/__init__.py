# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Invocations-protocol host for Azure AI Hosted Agents — an :class:`~azure.ai.agentserver.core.AgentServerHost` subclass exposing ``InvocationAgentServerHost``."""

# NOTE: keep this module docstring on a SINGLE line. The apiview-stub-generator
# (apistub, pinned via eng/apiview_reqs.txt) namespace detector mis-parses a
# multi-line module docstring in a package __init__ — a closing triple-quote on
# its own line leaves its parser stuck in "docstring" mode, so the package
# namespace resolves to "" and api.md generation breaks. The public API is
# enumerated in ``__all__`` below.
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._invocation import InvocationAgentServerHost
from ._version import VERSION

__all__ = ["InvocationAgentServerHost"]
__version__ = VERSION

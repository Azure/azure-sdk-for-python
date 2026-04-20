# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Conversations protocol for Azure AI Hosted Agents.

This package provides an conversation protocol host as a subclass of
:class:`~azure.ai.agentserver.core.AgentServerHost`.

Quick start::

    from azure.ai.agentserver.conversations import ConversationAgentServerHost
    from starlette.responses import JSONResponse

    app = ConversationAgentServerHost()

    @app.invoke_handler
    async def handle(request):
        return JSONResponse({"ok": True})

    app.run()
"""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._conversation import ConversationAgentServerHost, ConversationContext, ConversationError
from ._version import VERSION

__all__ = ["ConversationAgentServerHost", "ConversationContext", "ConversationError"]
__version__ = VERSION

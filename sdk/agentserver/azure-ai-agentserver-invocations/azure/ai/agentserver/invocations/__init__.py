# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Invocations protocol for Azure AI Hosted Agents.

This package provides invocation protocol hosts as subclasses of
:class:`~azure.ai.agentserver.core.AgentServerHost`.

**HTTP protocol** (``invocations``)::

    from azure.ai.agentserver.invocations import InvocationAgentServerHost
    from starlette.responses import JSONResponse

    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request):
        return JSONResponse({"ok": True})

    app.run()

**WebSocket protocol** (``invocations_ws``)::

    from azure.ai.agentserver.invocations import InvocationWSAgentServerHost, InvocationWSContext

    app = InvocationWSAgentServerHost()

    @app.ws_invoke_handler
    async def handle(payload, context):
        return {"reply": "hello"}

    app.run()
"""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._invocation import InvocationAgentServerHost
from ._invocation_ws import InvocationWSAgentServerHost, InvocationWSContext, InvocationWSError
from ._version import VERSION

__all__ = [
    "InvocationAgentServerHost",
    "InvocationWSAgentServerHost",
    "InvocationWSContext",
    "InvocationWSError",
]
__version__ = VERSION

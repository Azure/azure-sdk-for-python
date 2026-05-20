# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Invocations protocol for Azure AI Hosted Agents.

This package provides an invocation protocol host as a subclass of
:class:`~azure.ai.agentserver.core.AgentServerHost`.

Quick start::

    from azure.ai.agentserver.invocations import InvocationAgentServerHost
    from starlette.responses import JSONResponse

    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request):
        return JSONResponse({"ok": True})

    app.run()
"""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._invocation import InvocationAgentServerHost
from ._version import VERSION

__all__ = ["InvocationAgentServerHost"]
__version__ = VERSION

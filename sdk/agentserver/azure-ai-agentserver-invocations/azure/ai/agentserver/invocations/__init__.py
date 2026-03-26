# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Invocations protocol for Azure AI Hosted Agents.

This package provides the invocation protocol endpoints and handler
wiring for :class:`~azure.ai.agentserver.core.AgentServer`.

Quick start::

    from azure.ai.agentserver.core import AgentServer
    from azure.ai.agentserver.invocations import InvocationHandler
    from starlette.responses import JSONResponse

    server = AgentServer()
    invocations = InvocationHandler(server)

    @invocations.invoke_handler
    async def handle(request):
        return JSONResponse({"ok": True})

    server.run()
"""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._invocation import InvocationHandler
from ._version import VERSION

__all__ = ["InvocationHandler"]
__version__ = VERSION

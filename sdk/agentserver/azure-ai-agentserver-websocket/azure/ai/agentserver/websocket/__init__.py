# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Websocket protocol for Azure AI Hosted Agents.

This package provides an websocket protocol host as a subclass of
:class:`~azure.ai.agentserver.core.AgentServerHost`.

Quick start::

    from azure.ai.agentserver.websocket import WebsocketAgentServerHost
    from starlette.responses import JSONResponse

    app = WebsocketAgentServerHost()

    @app.invoke_handler
    async def handle(request):
        return JSONResponse({"ok": True})

    app.run()
"""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._websocket import WebsocketAgentServerHost, WebsocketContext, WebsocketError
from ._version import VERSION

__all__ = ["WebsocketAgentServerHost", "WebsocketContext", "WebsocketError"]
__version__ = VERSION

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Activity protocol host for Azure AI Hosted Agents.

This package provides an activity protocol host as a subclass of
:class:`~azure.ai.agentserver.core.AgentServerHost`.

Decorator-based usage (recommended)::

    from azure.ai.agentserver.activity import ActivityAgentServerHost

    app = ActivityAgentServerHost()

    @app.activity("message")
    async def on_message(context, state):
        await context.send_activity(f"Echo: {context.activity.text}")

    app.run()

Custom handler usage::

    from azure.ai.agentserver.activity import ActivityAgentServerHost

    async def handle(request):
        activity = request.state.activity
        # Custom processing...
        return Response(status_code=202)

    app = ActivityAgentServerHost(handler=handle)
    app.run()
"""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._activity import ActivityAgentServerHost
from ._m365_bridge import _apply_msal_patches as apply_msal_patches
from ._version import VERSION

__all__ = ["ActivityAgentServerHost", "apply_msal_patches"]
__version__ = VERSION

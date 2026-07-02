# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Activity protocol host for Azure AI Hosted Agents.

This package provides an activity protocol host as a subclass of
:class:`~azure.ai.agentserver.core.AgentServerHost`.

Default usage — the M365 Agents SDK is initialized during construction and the
host acts as the underlying ``AgentApplication`` (register handlers and reach
the full M365 surface directly on the host)::

    from azure.ai.agentserver.activity import ActivityAgentServerHost

    app = ActivityAgentServerHost()

    @app.activity("message")
    async def on_message(context, state):
        await context.send_activity(f"Echo: {context.activity.text}")

    app.run()

The default path also accepts optional overrides — pass any of ``storage`` /
``connection_manager`` / ``adapter`` / ``authorization`` / ``config`` (or
``digital_worker=True``) and the host builds the rest from the environment::

    from microsoft_agents.hosting.core import MemoryStorage

    # Override just the storage backend; the host builds the rest.
    app = ActivityAgentServerHost(storage=MemoryStorage())

Injected ``AgentApplication`` usage — host a pre-built M365 ``AgentApplication``
you constructed yourself (the adapter is taken from ``agent_app.adapter``)::

    from azure.ai.agentserver.activity import ActivityAgentServerHost

    # agent_app: a fully-built microsoft_agents AgentApplication (with an adapter)
    app = ActivityAgentServerHost.from_agent_application(agent_app)
    app.run()

Custom handler usage — the M365 SDK is not initialized; you own the pipeline::

    from starlette.responses import Response

    from azure.ai.agentserver.activity import ActivityAgentServerHost

    async def handle(request):
        activity = request.state.activity
        # Custom processing...
        return Response(status_code=202)

    app = ActivityAgentServerHost.from_request_handler(handle)
    app.run()
"""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._activity import ActivityAgentServerHost
from ._version import VERSION

__all__ = ["ActivityAgentServerHost"]
__version__ = VERSION

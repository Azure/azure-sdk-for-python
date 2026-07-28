# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Activity protocol host for Azure AI Hosted Agents.

This package provides an activity protocol host as a subclass of
:class:`~azure.ai.agentserver.core.AgentServerHost`.

Default usage — the M365 Agents SDK is initialized during construction and the
built ``AgentApplication`` is exposed as the ``agent_app`` property (register
handlers on it and reach the full M365 surface)::

    from azure.ai.agentserver.activity import ActivityAgentServerHost

    host = ActivityAgentServerHost()
    app = host.agent_app

    @app.activity("message")
    async def on_message(context, state):
        await context.send_activity(f"Echo: {context.activity.text}")

    host.run()

The default path also accepts optional overrides — pass any of ``storage`` /
``connection_manager`` / ``adapter`` / ``authorization`` / ``connection_config``
(or ``digital_worker=True``) and the host builds the rest from the environment::

    from microsoft_agents.hosting.core import MemoryStorage

    # Override just the storage backend; the host builds the rest.
    host = ActivityAgentServerHost(storage=MemoryStorage())
    app = host.agent_app

Injected ``AgentApplication`` usage — host a pre-built M365 ``AgentApplication``
you constructed yourself (the adapter is taken from ``agent_app.adapter``)::

    from azure.ai.agentserver.activity import ActivityAgentServerHost

    # agent_app: a fully-built microsoft_agents AgentApplication (with an adapter)
    host = ActivityAgentServerHost(agent_app=agent_app)
    host.run()

Custom handler usage — the M365 SDK is not initialized; you own the pipeline::

    from starlette.responses import Response

    from azure.ai.agentserver.activity import ActivityAgentServerHost

    async def handle(request):
        activity = request.state.activity
        # Custom processing...
        return Response(status_code=202)

    host = ActivityAgentServerHost(request_handler=handle)
    host.run()
"""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._activity import ActivityAgentServerHost
from ._config import get_hosted_agent_env
from ._version import VERSION

__all__ = ["ActivityAgentServerHost", "get_hosted_agent_env"]
__version__ = VERSION

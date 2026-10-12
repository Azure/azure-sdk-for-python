# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
FILE: readiness_handler_sample.py

DESCRIPTION:
    Demonstrates replacing the default readiness response with
    application-specific readiness logic.

USAGE:
    python readiness_handler_sample.py

    GET /readiness returns 503 until AGENT_READY is set to "true":

    curl -i http://localhost:8088/readiness
    AGENT_READY=true python readiness_handler_sample.py
"""

import os

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.core import AgentServerHost

app = AgentServerHost()


async def dependencies_ready() -> bool:
    """Return whether this sample application is ready to receive traffic."""
    return os.environ.get("AGENT_READY", "").lower() == "true"


@app.readiness_handler
async def readiness(request: Request) -> Response:
    """Return the application-specific readiness response."""
    del request
    if await dependencies_ready():
        return JSONResponse({"status": "healthy"})

    return JSONResponse({"status": "not_ready"}, status_code=503)


if __name__ == "__main__":
    app.run()

# Copyright (c) Microsoft. All rights reserved.

"""Echo activity protocol agent with a fully custom request handler.

Demonstrates ``request_handler``: you own the request pipeline entirely.
The M365 Agents SDK is **not** initialized — your ``async`` handler receives the
raw Starlette ``Request`` (with the parsed activity dict on
``request.state.activity``) and returns a Starlette ``Response``.

The host still provides the Foundry platform contract for free: the
``POST /activity/messages`` endpoint, session resolution, OpenTelemetry tracing
and W3C baggage, error-source classification, and the required response headers.
You just decide what each request does.

Because there is no M365 SDK bridge here, **this handler makes the outbound
Teams reply itself** — it mints a Bot Connector token with the container's
managed identity and POSTs the reply to the channel's ``serviceUrl``. This is
what "own the pipeline" means: you control inbound *and* outbound.
"""

import logging
from os import environ

import aiohttp
from azure.identity.aio import DefaultAzureCredential
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.activity import ActivityAgentServerHost

logger = logging.getLogger("custom-handler")

# Bot Connector token scope. The container's user-assigned managed identity
# (FOUNDRY_AGENT_INSTANCE_CLIENT_ID) is the agent's bot identity.
_BOT_CONNECTOR_SCOPE = "https://api.botframework.com/.default"
_INSTANCE_CLIENT_ID = environ.get("FOUNDRY_AGENT_INSTANCE_CLIENT_ID", "").strip()


async def _send_teams_reply(service_url: str, conversation_id: str, text: str) -> None:
    """Mint a Bot Connector token and POST a message activity back to the channel.

    SECURITY (production): custom-handler mode performs no M365 inbound
    authentication, so ``service_url`` here comes straight from the inbound
    payload and is untrusted. Sending a managed-identity Bot Connector token to
    an unvalidated URL allows token exfiltration and SSRF. Before minting or
    attaching credentials in a real deployment, authenticate the inbound
    activity (JWT from the Bot Framework) and validate ``service_url`` against an
    allowlist of trusted Bot Connector endpoints. This sample skips those steps
    for brevity and must not be used as-is in production.
    """
    cred_kwargs = {"managed_identity_client_id": _INSTANCE_CLIENT_ID} if _INSTANCE_CLIENT_ID else {}
    credential = DefaultAzureCredential(**cred_kwargs)
    try:
        token = (await credential.get_token(_BOT_CONNECTOR_SCOPE)).token
    finally:
        await credential.close()

    url = f"{service_url.rstrip('/')}/v3/conversations/{conversation_id}/activities"
    payload = {"type": "message", "text": text}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status >= 400:
                body = await resp.text()
                logger.error("Outbound reply failed | status=%s | body=%s", resp.status, body)
            else:
                logger.info("Outbound reply sent | status=%s", resp.status)


async def handle(request: Request) -> Response:
    """Custom handler: you own inbound and outbound (no M365 SDK)."""
    activity = request.state.activity
    activity_type = activity.get("type", "")
    text = (activity.get("text") or "").strip()

    logger.info("[HANDLER] type=%s | text=%s", activity_type, text)

    # "invoke" activities expect a synchronous JSON reply body (no outbound call).
    if activity_type == "invoke":
        return JSONResponse({"status": 200, "body": {"echo": text}})

    # For a normal message, send the echo back over the Bot Connector channel.
    service_url = (activity.get("serviceUrl") or "").strip()
    conversation = activity.get("conversation") or {}
    conversation_id = conversation.get("id", "") if isinstance(conversation, dict) else ""

    if activity_type == "message" and text and service_url and conversation_id:
        try:
            await _send_teams_reply(service_url, conversation_id, f"Echo (custom handler): {text}")
        except Exception:  # pragma: no cover - best-effort outbound
            logger.exception("Failed to send outbound Teams reply")

    # Acknowledge receipt of the inbound activity.
    return Response(status_code=202)


app = ActivityAgentServerHost(request_handler=handle)


if __name__ == "__main__":
    app.run()

# Copyright (c) Microsoft. All rights reserved.

"""Auto Sign-In Agent — Activity Protocol with OAuth.

Demonstrates OAuth auto sign-in with multiple providers (Graph and GitHub)
using the M365 Agents SDK's ``auth_handlers`` feature.

This sample uses the **handler pattern** because ``auth_handlers`` is
an ``AgentApplication`` feature that requires direct access to the
M365 SDK ``AgentApplication`` instance.

Available commands:
    /me     — Sign in with Graph and show profile info
    /prs    — Sign in with GitHub and list recent PRs
    /status — Show current token status
    /logout — Sign out of all providers

Required environment variables:

    # M365 Agents SDK (auto-injected by Foundry)
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHTYPE
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHORITY
    CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID

    # OAuth handler — Graph
    AGENTAPPLICATION__USERAUTHORIZATION__HANDLERS__GRAPH__SETTINGS__AZUREBOTOAUTHCONNECTIONNAME=<name>

    # OAuth handler — GitHub
    AGENTAPPLICATION__USERAUTHORIZATION__HANDLERS__GITHUB__SETTINGS__AZUREBOTOAUTHCONNECTIONNAME=<name>

    # Auto sign-in
    AGENTAPPLICATION__USERAUTHORIZATION__AUTOSIGNIN=true

Usage::

    python auto_signin_activity_agent.py
"""

import logging
import sys
import traceback
from os import environ

from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.activity import ActivityAgentServerHost

from microsoft_agents.activity import Activity, ActivityTypes, load_configuration_from_env
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.hosting.core import (
    AgentApplication,
    Authorization,
    ClaimsIdentity,
    HttpAdapterBase,
    MemoryStorage,
    RestChannelServiceClientFactory,
    TurnContext,
    TurnState,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Enable M365 SDK logging
ms_agents_logger = logging.getLogger("microsoft_agents")
ms_agents_logger.addHandler(logging.StreamHandler())
ms_agents_logger.setLevel(logging.INFO)


# ── M365 SDK setup (handler pattern for auth_handlers) ───────────

# Apply MSAL patches BEFORE creating MsalConnectionManager.
# In Foundry hosted containers (AUTHTYPE=UserManagedIdentity), the stock
# MsalAuth uses ManagedIdentityClient which doesn't support fmi_path.
# This patch replaces get_agentic_application_token with DefaultAzureCredential.
# The zero-config decorator samples get this for free via the M365 bridge.
from azure.ai.agentserver.activity import apply_msal_patches
apply_msal_patches()

config = load_configuration_from_env(environ)
STORAGE = MemoryStorage()
CONNECTION_MANAGER = MsalConnectionManager(**config)
CLIENT_FACTORY = RestChannelServiceClientFactory(CONNECTION_MANAGER)
ADAPTER = HttpAdapterBase(channel_service_client_factory=CLIENT_FACTORY)
AUTHORIZATION = Authorization(STORAGE, CONNECTION_MANAGER, **config)

AGENT_APP = AgentApplication[TurnState](
    storage=STORAGE,
    adapter=ADAPTER,
    authorization=AUTHORIZATION,
    **config,
)


# ── Activity handlers ────────────────────────────────────────────


@AGENT_APP.conversation_update("membersAdded")
async def on_members_added(context: TurnContext, _state: TurnState):
    """Welcome new members with auth status info."""
    await context.send_activity(
        "Welcome to the Auto Sign-In sample!\n\n"
        "**Commands:**\n"
        "- **/me** — Sign in with Graph and show your profile\n"
        "- **/prs** — Sign in with GitHub and list your recent PRs\n"
        "- **/status** — Show current token status\n"
        "- **/logout** — Sign out of all providers"
    )
    return True


@AGENT_APP.message("/me", auth_handlers=["GRAPH"])
async def on_me(context: TurnContext, state: TurnState):
    """Show user profile from Microsoft Graph.

    The ``auth_handlers=["GRAPH"]`` parameter triggers auto sign-in
    for the GRAPH OAuth connection before this handler runs.
    The token is available in ``state.temp.auth_tokens["GRAPH"]``.
    """
    import aiohttp

    token = state.temp.auth_tokens.get("GRAPH")
    if not token:
        await context.send_activity("No Graph token available. Try again.")
        return

    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}"}
        async with session.get("https://graph.microsoft.com/v1.0/me", headers=headers) as resp:
            if resp.status == 200:
                profile = await resp.json()
                name = profile.get("displayName", "Unknown")
                email = profile.get("mail", profile.get("userPrincipalName", "Unknown"))
                job = profile.get("jobTitle", "N/A")
                await context.send_activity(
                    f"**Your Profile (Graph)**\n\n"
                    f"- **Name:** {name}\n"
                    f"- **Email:** {email}\n"
                    f"- **Job Title:** {job}"
                )
            else:
                await context.send_activity(f"Graph API returned {resp.status}.")


@AGENT_APP.message("/prs", auth_handlers=["GITHUB"])
async def on_prs(context: TurnContext, state: TurnState):
    """List recent GitHub PRs.

    The ``auth_handlers=["GITHUB"]`` parameter triggers auto sign-in
    for the GITHUB OAuth connection before this handler runs.
    """
    import aiohttp

    token = state.temp.auth_tokens.get("GITHUB")
    if not token:
        await context.send_activity("No GitHub token available. Try again.")
        return

    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with session.get(
            "https://api.github.com/user/repos?sort=updated&per_page=5",
            headers=headers,
        ) as resp:
            if resp.status == 200:
                repos = await resp.json()
                lines = ["**Your Recent GitHub Repos:**\n"]
                for repo in repos:
                    lines.append(f"- [{repo['full_name']}]({repo['html_url']})")
                await context.send_activity("\n".join(lines))
            else:
                await context.send_activity(f"GitHub API returned {resp.status}.")


@AGENT_APP.message("/status")
async def on_status(context: TurnContext, state: TurnState):
    """Show current OAuth token status."""
    tokens = getattr(getattr(state, "temp", None), "auth_tokens", {}) or {}
    if tokens:
        status_lines = ["**Token Status:**\n"]
        for name, token in tokens.items():
            status_lines.append(f"- **{name}:** {'Available' if token else 'Not available'}")
        await context.send_activity("\n".join(status_lines))
    else:
        await context.send_activity("No tokens are currently cached. Use **/me** or **/prs** to sign in.")


@AGENT_APP.message("/logout")
async def on_logout(context: TurnContext, state: TurnState):
    """Sign out of all OAuth connections."""
    await context.send_activity("You have been signed out. Use **/me** or **/prs** to sign in again.")


@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    """Default message handler."""
    await context.send_activity(
        f"You said: {context.activity.text}\n\n"
        "Try **/me**, **/prs**, **/status**, or **/logout**."
    )


@AGENT_APP.error
async def on_error(context: TurnContext, error: Exception):
    """Handle unhandled errors."""
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The agent encountered an error or bug.")


# ── Foundry host with custom handler ─────────────────────────────


async def handle(request) -> Response:
    """Bridge to M365 SDK — parses activity and delegates to AGENT_APP."""
    activity = Activity.model_validate(request.state.activity)

    if not activity.type or not activity.conversation or not activity.conversation.id:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "invalid_request", "message": "Missing type or conversation.id"}},
        )

    claims = ClaimsIdentity({}, is_authenticated=False, authentication_type="Anonymous")

    try:
        invoke_response = await ADAPTER.process_activity(claims, activity, AGENT_APP.on_turn)
    except PermissionError:
        return Response(status_code=401)

    if activity.type == "invoke" or activity.delivery_mode == "expectReplies":
        if invoke_response is not None:
            return JSONResponse(content=invoke_response.body, status_code=invoke_response.status)
        return JSONResponse(content={}, status_code=200)

    return Response(status_code=202)


app = ActivityAgentServerHost(handler=handle)

if __name__ == "__main__":
    app.run()

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""M365 Agents SDK bridge for the Activity protocol host.

Provides auto-initialization of the M365 Agents SDK stack from
environment variables, MSAL auth patches for Foundry containers,
and a bridge function that converts activity dicts into M365 SDK
turn processing.

This module is used internally by :class:`ActivityAgentServerHost`
when decorator-based handlers are registered. Users who pass their
own ``handler`` callable bypass this module entirely.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger("azure.ai.agentserver")

# Lazy imports — these are only needed when the bridge is actually used.
# This avoids hard dependency failures if M365 SDK isn't installed.
_m365_initialized = False
_adapter = None
_agent_app = None
_connection_manager = None


def _apply_msal_patches() -> None:
    """Apply MSAL auth patches for Foundry container MAIB auth.

    When AUTH_TYPE is UserManagedIdentity, the stock MsalAuth uses
    ManagedIdentityClient which doesn't support fmi_path. This patch
    replaces get_agentic_application_token with DefaultAzureCredential.
    """
    try:
        from microsoft_agents.authentication.msal.msal_auth import MsalAuth
    except ImportError:
        logger.debug("microsoft-agents-authentication-msal not installed; skipping MSAL patches")
        return

    _PATCH_FLAG = "_activity_sdk_msal_patched"
    if getattr(MsalAuth, _PATCH_FLAG, False):
        return

    async def _get_token_via_dac(self, tenant_id: str, agent_app_instance_id: str) -> Optional[str]:
        from azure.identity.aio import DefaultAzureCredential

        if not agent_app_instance_id:
            from microsoft_agents.authentication.msal.errors import authentication_errors
            raise ValueError(str(authentication_errors.AgentApplicationInstanceIdRequired))

        logger.info(
            "[activity-bridge] Acquiring agentic application token via "
            "DefaultAzureCredential for agent_app_instance_id=%s",
            agent_app_instance_id,
        )

        client_id = getattr(self._msal_configuration, "CLIENT_ID", None)
        credential_kwargs: dict[str, Any] = {
            "identity_config": {"fmi_path": agent_app_instance_id},
        }
        if client_id:
            credential_kwargs["managed_identity_client_id"] = client_id

        credential = DefaultAzureCredential(**credential_kwargs)
        try:
            token = await credential.get_token("api://AzureADTokenExchange/.default")
            return token.token
        except Exception:
            logger.exception(
                "Failed to acquire agentic application token for agent_app_instance_id=%s",
                agent_app_instance_id,
            )
            return None
        finally:
            try:
                await credential.close()
            except Exception:
                pass

    MsalAuth.get_agentic_application_token = _get_token_via_dac
    setattr(MsalAuth, _PATCH_FLAG, True)
    logger.info("Patched MsalAuth.get_agentic_application_token → DefaultAzureCredential")


def _ensure_m365_initialized(storage: Any = None):
    """Lazily initialize the M365 Agents SDK from environment variables.

    Called on first request when decorators are used. Idempotent.

    :param storage: Optional M365 storage implementation. Falls back to
        ``MemoryStorage`` when omitted.
    :type storage: Any
    :return: The initialized AgentApplication and adapter.
    :rtype: tuple[Any, Any]
    """
    global _m365_initialized, _adapter, _agent_app, _connection_manager

    if _m365_initialized:
        return _agent_app, _adapter

    try:
        from microsoft_agents.activity import Activity, load_configuration_from_env
        from microsoft_agents.authentication.msal import MsalConnectionManager
        from microsoft_agents.hosting.core import (
            AgentApplication,
            Authorization,
            HttpAdapterBase,
            MemoryStorage,
            RestChannelServiceClientFactory,
            TurnState,
        )
    except ImportError as exc:
        raise ImportError(
            "Activity decorator handlers require the M365 Agents SDK. "
            "Install: pip install microsoft-agents-hosting-core "
            "microsoft-agents-authentication-msal microsoft-agents-activity azure-identity"
        ) from exc

    # Apply MSAL patches before any MsalConnectionManager is created
    _apply_msal_patches()

    logger.info("Initializing M365 Agents SDK...")
    config = load_configuration_from_env(os.environ)
    storage = storage or MemoryStorage()
    _connection_manager = MsalConnectionManager(**config)
    client_factory = RestChannelServiceClientFactory(_connection_manager)
    _adapter = HttpAdapterBase(channel_service_client_factory=client_factory)
    authorization = Authorization(storage, _connection_manager, **config)
    _agent_app = AgentApplication[TurnState](
        storage=storage,
        adapter=_adapter,
        authorization=authorization,
        **config,
    )
    _m365_initialized = True
    logger.info("M365 Agents SDK initialized successfully.")
    return _agent_app, _adapter


async def create_bridge_handler(request: Request) -> Response:
    """Built-in bridge handler for decorator-based agents.

    Converts the activity dict (set by ActivityAgentServerHost on
    request.state) into an M365 SDK Activity and processes it through
    the AgentApplication turn pipeline.

    On first call, initializes the M365 SDK and replays any pending
    handler registrations captured by the lazy proxy.
    """
    from microsoft_agents.activity import Activity
    from microsoft_agents.hosting.core import ClaimsIdentity

    global _lazy_agent_app
    storage = getattr(request.app.state, "activity_storage", None)
    agent_app, adapter = _ensure_m365_initialized(storage)

    # Replay pending decorator registrations onto the real AgentApplication
    if _lazy_agent_app is not None and not _lazy_agent_app._replayed:
        _lazy_agent_app._replay_on(agent_app)

    activity_dict = request.state.activity
    activity_type = activity_dict.get("type", "unknown")
    session_id = request.state.session_id

    logger.info(
        "Bridge: activity received | type=%s | session=%s",
        activity_type, session_id,
    )
    logger.debug(
        "Bridge: activity details | conversation=%s | serviceUrl=%s | channelId=%s | from=%s",
        activity_dict.get("conversation", {}).get("id", "?") if isinstance(activity_dict.get("conversation"), dict) else "?",
        activity_dict.get("serviceUrl", ""),
        activity_dict.get("channelId", ""),
        activity_dict.get("from", {}).get("id", "?") if isinstance(activity_dict.get("from"), dict) else "?",
    )

    activity = Activity.model_validate(activity_dict)

    if not activity.type or not activity.conversation or not activity.conversation.id:
        logger.warning(
            "Bridge: rejecting activity with 400 | type=%s | has_conversation=%s | conversation_id=%s",
            activity.type, activity.conversation is not None,
            activity.conversation.id if activity.conversation else "None",
        )
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "invalid_request", "message": "Activity must have type and conversation.id"}},
        )

    claims = ClaimsIdentity({}, is_authenticated=False, authentication_type="Anonymous")

    try:
        invoke_response = await adapter.process_activity(claims, activity, agent_app.on_turn)
    except PermissionError:
        logger.error("Permission denied processing activity | type=%s", activity_type)
        return Response(status_code=401)
    except TypeError as exc:
        logger.warning("TypeError processing activity (likely missing serviceUrl) | type=%s | error=%s", activity_type, exc)
        return Response(status_code=202)
    except Exception:
        # Re-raise so the outer _create_activity_endpoint can classify
        # the error and return 500 with proper x-platform-error-source.
        raise

    if activity.type == "invoke" or activity.delivery_mode == "expectReplies":
        if invoke_response is not None:
            return JSONResponse(content=invoke_response.body, status_code=invoke_response.status)
        return JSONResponse(content={}, status_code=200)

    return Response(status_code=202)


class _LazyAgentApp:
    """Proxy that defers AgentApplication access until first request."""

    def __init__(self):
        self._pending_registrations: list = []
        self._replayed = False

    def activity(self, activity_type: str):
        """Capture an activity handler registration for later replay."""
        def decorator(fn):
            self._pending_registrations.append(("activity", activity_type, fn))
            return fn
        return decorator

    def error(self, fn):
        """Capture an error handler registration for later replay."""
        self._pending_registrations.append(("error", None, fn))
        return fn

    def _replay_on(self, agent_app):
        """Replay all captured registrations onto the real AgentApplication.

        Idempotent — only replays once even if called concurrently.
        """
        if self._replayed:
            return
        self._replayed = True
        for kind, arg, fn in self._pending_registrations:
            if kind == "activity":
                agent_app.activity(arg)(fn)
            elif kind == "error":
                agent_app.error(fn)
        self._pending_registrations.clear()


# Module-level lazy proxy — shared across all decorator calls
_lazy_agent_app: Optional[_LazyAgentApp] = None


def _get_or_create_lazy_app() -> _LazyAgentApp:
    global _lazy_agent_app
    if _lazy_agent_app is None:
        _lazy_agent_app = _LazyAgentApp()
    return _lazy_agent_app


def _reset_for_testing() -> None:
    """Reset all module-level state. For test isolation only."""
    global _m365_initialized, _adapter, _agent_app, _connection_manager, _lazy_agent_app
    _m365_initialized = False
    _adapter = None
    _agent_app = None
    _connection_manager = None
    _lazy_agent_app = None

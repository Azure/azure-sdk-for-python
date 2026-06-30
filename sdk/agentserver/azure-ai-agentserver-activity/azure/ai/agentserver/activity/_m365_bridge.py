# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""M365 Agents SDK bridge for the Activity protocol host.

Builds the M365 Agents SDK stack (``AgentApplication`` + adapter) from
environment variables or caller-supplied components, applies the MSAL auth
patch for the Foundry digital-worker model, and provides the request handler
that converts inbound activity dicts into M365 SDK turn processing.

Used internally by :class:`ActivityAgentServerHost` when no custom ``handler``
is supplied. Callers that pass their own ``handler`` bypass this module
entirely.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger("azure.ai.agentserver")


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

    async def _get_token_via_dac(  # pylint: disable=unused-argument
        self, tenant_id: str, agent_app_instance_id: str
    ) -> Optional[str]:
        from azure.identity.aio import DefaultAzureCredential

        if not agent_app_instance_id:
            # pylint: disable=import-error,no-name-in-module
            from microsoft_agents.authentication.msal.errors import authentication_errors
            raise ValueError(str(authentication_errors.AgentApplicationInstanceIdRequired))

        logger.info(
            "[activity-bridge] Acquiring agentic application token via "
            "DefaultAzureCredential for agent_app_instance_id=%s",
            agent_app_instance_id,
        )

        client_id = getattr(self._msal_configuration, "CLIENT_ID", None)  # pylint: disable=protected-access
        credential_kwargs: dict[str, Any] = {
            "identity_config": {"fmi_path": agent_app_instance_id},
        }
        if client_id:
            credential_kwargs["managed_identity_client_id"] = client_id

        credential = DefaultAzureCredential(**credential_kwargs)
        try:
            token = await credential.get_token("api://AzureADTokenExchange/.default")
            return token.token
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception(
                "Failed to acquire agentic application token for agent_app_instance_id=%s",
                agent_app_instance_id,
            )
            return None
        finally:
            try:
                await credential.close()
            except Exception:  # pylint: disable=broad-exception-caught
                pass

    MsalAuth.get_agentic_application_token = _get_token_via_dac
    setattr(MsalAuth, _PATCH_FLAG, True)
    logger.info("Patched MsalAuth.get_agentic_application_token → DefaultAzureCredential")


def build_m365_app(
    *,
    digital_worker: bool = False,
    storage: Optional[Any] = None,
    connection_manager: Optional[Any] = None,
    adapter: Optional[Any] = None,
    authorization: Optional[Any] = None,
    config: Optional[dict] = None,
    agent_app: Optional[Any] = None,
):
    """Build the M365 Agents SDK ``AgentApplication`` (and adapter) eagerly.

    Constructs the full M365 stack from environment variables, or assembles it
    from caller-supplied components. Any component left as ``None`` is created
    with the default derived from the process environment.

    :keyword digital_worker: When ``True``, apply the federated-identity (FMI)
        MSAL patch before creating the connection manager (digital-worker
        model). When ``False`` (default), the simple agent-instance-identity
        model is used and no patch is applied.
    :paramtype digital_worker: bool
    :keyword storage: Optional storage backend (defaults to ``MemoryStorage``).
    :keyword connection_manager: Optional connection manager (defaults to
        ``MsalConnectionManager`` built from ``config``).
    :keyword adapter: Optional channel adapter (defaults to ``HttpAdapterBase``).
    :keyword authorization: Optional ``Authorization`` instance.
    :keyword config: Optional configuration mapping (defaults to
        ``load_configuration_from_env(os.environ)``).
    :keyword agent_app: Optional, fully-built ``AgentApplication`` to use as-is.
        When supplied, the other component arguments are ignored except
        ``adapter`` (falls back to ``agent_app.adapter``).
    :return: A tuple of ``(agent_app, adapter)``.
    :rtype: tuple
    :raises ImportError: If the M365 Agents SDK is not installed.
    """
    # Apply the FMI patch (digital-worker only) before any MsalConnectionManager
    # is created. The simple agent-instance-identity model must NOT be patched.
    if digital_worker:
        _apply_msal_patches()

    # Fast path: a fully-built agent_app was injected. No SDK import is needed
    # to assemble the default stack.
    if agent_app is not None:
        resolved_adapter = adapter if adapter is not None else getattr(agent_app, "adapter", None)
        if resolved_adapter is None:
            raise ValueError(
                "When injecting agent_app=, also pass adapter= "
                "(or ensure agent_app.adapter is set)."
            )
        return agent_app, resolved_adapter

    try:
        from microsoft_agents.activity import load_configuration_from_env
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
            "ActivityAgentServerHost requires the M365 Agents SDK when no custom "
            "handler= is provided. Install: pip install microsoft-agents-hosting-core "
            "microsoft-agents-authentication-msal microsoft-agents-activity azure-identity"
        ) from exc

    logger.info("Initializing M365 Agents SDK...")
    resolved_config = config if config is not None else load_configuration_from_env(os.environ)
    resolved_storage = storage if storage is not None else MemoryStorage()
    resolved_cm = (
        connection_manager
        if connection_manager is not None
        else MsalConnectionManager(**resolved_config)
    )
    if adapter is not None:
        resolved_adapter = adapter
    else:
        client_factory = RestChannelServiceClientFactory(resolved_cm)
        resolved_adapter = HttpAdapterBase(channel_service_client_factory=client_factory)
    resolved_authorization = (
        authorization
        if authorization is not None
        else Authorization(resolved_storage, resolved_cm, **resolved_config)
    )
    built_app = AgentApplication[TurnState](
        storage=resolved_storage,
        adapter=resolved_adapter,
        authorization=resolved_authorization,
        **resolved_config,
    )
    logger.info("M365 Agents SDK initialized successfully.")
    return built_app, resolved_adapter


def make_bridge_handler(agent_app: Any, adapter: Any, *, digital_worker: bool = False):
    """Create a request handler bound to a specific AgentApplication + adapter.

    :param agent_app: The M365 ``AgentApplication`` used to process each turn.
    :param adapter: The channel adapter used for the outbound turn pipeline.
    :keyword digital_worker: Selects the claims model for the outbound reply.
    :return: An async Starlette request handler.
    :rtype: callable
    """

    async def _bridge_handler(request: Request) -> Response:
        return await _process_turn(agent_app, adapter, digital_worker, request)

    return _bridge_handler


async def _process_turn(agent_app: Any, adapter: Any, digital_worker: bool, request: Request) -> Response:
    """Process a single inbound activity through the M365 turn pipeline.

    :param agent_app: The bound ``AgentApplication``.
    :param adapter: The bound channel adapter.
    :param digital_worker: Whether to use the digital-worker claims model.
    :param request: The inbound Starlette request carrying the activity on ``state``.
    :type request: ~starlette.requests.Request
    :return: The HTTP response produced by the M365 turn pipeline.
    :rtype: ~starlette.responses.Response
    """
    from microsoft_agents.activity import Activity
    from microsoft_agents.hosting.core import ClaimsIdentity

    activity_dict = request.state.activity
    activity_type = activity_dict.get("type", "unknown")
    session_id = request.state.session_id

    logger.info(
        "Bridge: activity received | type=%s | session=%s",
        activity_type, session_id,
    )
    logger.debug(
        "Bridge: activity details | conversation=%s | serviceUrl=%s | channelId=%s | from=%s",
        activity_dict.get("conversation", {}).get("id", "?")
        if isinstance(activity_dict.get("conversation"), dict)
        else "?",
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

    if digital_worker:
        # Digital-worker model: anonymous claims; the FMI patch supplies the
        # outbound token via the federated-identity exchange.
        claims = ClaimsIdentity({}, is_authenticated=False, authentication_type="Anonymous")
    else:
        # Simple model (default): present authenticated claims whose appid
        # matches the service-connection client id (the agent instance
        # identity). This makes the adapter use the real MSAL UserManagedIdentity
        # connection for the outbound reply instead of an anonymous/empty token.
        bot_app_id = os.environ.get("CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID", "").strip()
        claim_dict = {"appid": bot_app_id, "aud": bot_app_id} if bot_app_id else {}
        claims = ClaimsIdentity(claim_dict, is_authenticated=True, authentication_type="Bearer")

    try:
        invoke_response = await adapter.process_activity(claims, activity, agent_app.on_turn)
    except PermissionError:
        logger.error("Permission denied processing activity | type=%s", activity_type)
        return Response(status_code=401)
    except TypeError as exc:
        logger.warning(
            "TypeError processing activity (likely missing serviceUrl) | type=%s | error=%s",
            activity_type, exc,
        )
        return Response(status_code=202)
    except Exception:  # pylint: disable=try-except-raise
        # Re-raise so the outer _create_activity_endpoint can classify
        # the error and return 500 with proper x-platform-error-source.
        raise

    if activity.type == "invoke" or activity.delivery_mode == "expectReplies":
        if invoke_response is not None:
            return JSONResponse(content=invoke_response.body, status_code=invoke_response.status)
        return JSONResponse(content={}, status_code=200)

    return Response(status_code=202)

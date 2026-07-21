# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""M365 Agents SDK bridge for the Activity protocol host.

Builds the M365 Agents SDK stack (``AgentApplication`` + adapter) from a resolved
``CONNECTIONS__*`` mapping or caller-supplied components, applies the MSAL auth
patch for the Foundry digital-worker model, synthesizes the per-turn outbound
claims, and binds the request handler that drives the Starlette
:class:`~._cloud_adapter.StarletteCloudAdapter`.

Used internally by :class:`ActivityAgentServerHost` for its default (build the
stack) and injected-``agent_app`` construction paths. A host created with a
custom ``request_handler`` bypasses this module entirely.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable, Mapping
from typing import TYPE_CHECKING, Optional, cast

from starlette.requests import Request
from starlette.responses import Response

from ._config import use_anonymous_outbound
from ._constants import MsalPatch, OutboundAuth

if TYPE_CHECKING:  # pragma: no cover - type-only imports (M365 SDK is optional)
    from microsoft_agents.hosting.core import (
        AgentApplication,
        Authorization,
        ClaimsIdentity,
        HttpAdapterBase,
        Storage,
    )
    from microsoft_agents.authentication.msal import MsalConnectionManager

logger = logging.getLogger("azure.ai.agentserver.activity.bridge")

BridgeHandler = Callable[[Request], Awaitable[Response]]


def _apply_msal_patches() -> None:
    """Apply the MSAL auth patch for the Foundry digital-worker (MAIB) model.

    When the auth type is ``UserManagedIdentity`` the stock ``MsalAuth`` uses
    MSAL's ``ManagedIdentityClient``, which does not support ``fmi_path``. This
    patch replaces ``get_agentic_application_token`` with a federated-identity
    (FMI) exchange via azure-identity's ``ManagedIdentityCredential``. It is
    idempotent (guarded by a patch flag) and a no-op when the M365 MSAL package
    is not installed.

    :return: None.
    :rtype: None
    """
    try:
        # pylint: disable=import-error,no-name-in-module
        from microsoft_agents.authentication.msal.msal_auth import MsalAuth
    except ImportError:
        logger.debug("microsoft-agents-authentication-msal not installed; skipping MSAL patches")
        return

    if getattr(MsalAuth, MsalPatch.PATCH_FLAG, False):
        return

    async def get_token_via_managed_identity(
        self: object, _tenant_id: str, agent_app_instance_id: str
    ) -> Optional[str]:
        # ``_tenant_id`` is part of the MsalAuth.get_agentic_application_token
        # signature we are overriding (the SDK passes it positionally). The FMI
        # exchange derives the tenant from the managed identity itself, so it is
        # intentionally unused here.
        from azure.identity.aio import ManagedIdentityCredential

        if not agent_app_instance_id:
            # pylint: disable=import-error,no-name-in-module
            from microsoft_agents.authentication.msal.errors import authentication_errors

            raise ValueError(str(authentication_errors.AgentApplicationInstanceIdRequired))

        msal_configuration = getattr(self, MsalPatch.MSAL_CONFIGURATION_ATTR, None)
        client_id: Optional[str] = getattr(msal_configuration, MsalPatch.MSAL_CLIENT_ID_ATTR, None)

        logger.info(
            "Acquiring agentic application token via ManagedIdentityCredential for agent_app_instance_id=%s",
            agent_app_instance_id,
        )

        # Use ManagedIdentityCredential rather than DefaultAzureCredential: in a
        # hosted container the agentic token must come from the container's managed
        # identity. ManagedIdentityCredential supports the FMI ``identity_config``
        # exchange but has no credential fallback chain, so it cannot silently pick
        # up an unintended identity (for example a developer's Azure CLI login).
        credential = ManagedIdentityCredential(
            client_id=client_id or None,
            identity_config={MsalPatch.FMI_PATH_KEY: agent_app_instance_id},
        )
        try:
            token = await credential.get_token(MsalPatch.TOKEN_EXCHANGE_SCOPE)
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
                logger.debug("Error closing ManagedIdentityCredential", exc_info=True)

    MsalAuth.get_agentic_application_token = get_token_via_managed_identity
    setattr(MsalAuth, MsalPatch.PATCH_FLAG, True)
    logger.info("Patched MsalAuth.get_agentic_application_token -> ManagedIdentityCredential")


def build_m365_app(
    *,
    digital_worker: bool,
    connection_config: Mapping[str, str],
    storage: Optional[Storage] = None,
    connection_manager: Optional[MsalConnectionManager] = None,
    adapter: Optional[HttpAdapterBase] = None,
    authorization: Optional[Authorization] = None,
    agent_app: Optional[AgentApplication] = None,
) -> tuple[AgentApplication, HttpAdapterBase]:
    """Build the M365 Agents SDK ``AgentApplication`` (and adapter) eagerly.

    Constructs the full M365 stack from ``connection_config``, or assembles it
    from caller-supplied components. Any component left as ``None`` is created
    from the resolved connection config.

    :keyword digital_worker: When ``True``, apply the FMI MSAL patch before
        creating the connection manager (digital-worker model).
    :paramtype digital_worker: bool
    :keyword connection_config: The resolved M365 ``CONNECTIONS__*`` mapping.
    :paramtype connection_config: Mapping[str, str]
    :keyword storage: The storage backend for the built stack. Required when
        building (``agent_app`` not supplied); ignored on the injected-``agent_app``
        fast path. :class:`ActivityAgentServerHost` resolves it via
        ``_resolve_storage`` (the single place the default backend is chosen)
        before calling this.
    :paramtype storage: Optional[~microsoft_agents.hosting.core.Storage]
    :keyword connection_manager: Optional connection manager (defaults to
        ``MsalConnectionManager`` built from the connection settings).
    :paramtype connection_manager:
        Optional[~microsoft_agents.authentication.msal.MsalConnectionManager]
    :keyword adapter: Optional channel adapter (defaults to ``HttpAdapterBase``).
    :paramtype adapter: Optional[~microsoft_agents.hosting.core.HttpAdapterBase]
    :keyword authorization: Optional ``Authorization`` instance.
    :paramtype authorization: Optional[~microsoft_agents.hosting.core.Authorization]
    :keyword agent_app: Optional, fully-built ``AgentApplication`` to use as-is.
        When supplied, the other component arguments are ignored and the adapter
        is taken from ``agent_app.adapter``.
    :paramtype agent_app: Optional[~microsoft_agents.hosting.core.AgentApplication]
    :return: A tuple of ``(agent_app, adapter)``.
    :rtype: tuple[~microsoft_agents.hosting.core.AgentApplication,
        ~microsoft_agents.hosting.core.HttpAdapterBase]
    :raises ImportError: If the M365 Agents SDK is not installed.
    """
    # Apply the FMI patch (digital-worker only) before any MsalConnectionManager
    # is created.
    if digital_worker:
        _apply_msal_patches()

    # Fast path: a fully-built agent_app was injected (agent_app=<app>).
    # Host it as-is; the adapter is taken from agent_app.adapter. That property is
    # typed as the ChannelServiceAdapter base; the M365 SDK builds it as an
    # HttpAdapterBase and only ``process_activity`` (defined on the base) is used,
    # so narrowing here is safe.
    if agent_app is not None:
        return agent_app, cast("HttpAdapterBase", agent_app.adapter)

    try:
        # pylint: disable=import-error,no-name-in-module
        from microsoft_agents.activity import load_configuration_from_env
        from microsoft_agents.authentication.msal import MsalConnectionManager
        from microsoft_agents.hosting.core import (
            AgentApplication,
            Authorization,
            HttpAdapterBase,
            RestChannelServiceClientFactory,
            TurnState,
        )
    except ImportError as exc:
        raise ImportError(
            "ActivityAgentServerHost requires the M365 Agents SDK for the default "
            "and injected-agent_app construction paths. Install: pip install "
            "microsoft-agents-hosting-core microsoft-agents-authentication-msal "
            "microsoft-agents-activity azure-identity."
        ) from exc

    logger.info("Initializing M365 Agents SDK...")

    # The connection config is a flat ``CONNECTIONS__*`` mapping; the M365 SDK
    # parses it into its nested configuration structure before the connection
    # manager / authorization / app can consume it.
    resolved_config = load_configuration_from_env(dict(connection_config))
    if storage is None:
        raise ValueError(
            "storage is required to build the M365 stack. Pass a storage backend, or "
            "pass agent_app to host a pre-built AgentApplication as-is."
        )
    resolved_storage: Storage = storage
    resolved_cm: MsalConnectionManager = (
        connection_manager if connection_manager is not None else MsalConnectionManager(**resolved_config)
    )
    if adapter is not None:
        resolved_adapter: HttpAdapterBase = adapter
    else:
        client_factory = RestChannelServiceClientFactory(resolved_cm)
        resolved_adapter = HttpAdapterBase(channel_service_client_factory=client_factory)
    resolved_authorization: Authorization = (
        authorization if authorization is not None else Authorization(resolved_storage, resolved_cm, **resolved_config)
    )
    built_app: AgentApplication = AgentApplication[TurnState](
        storage=resolved_storage,
        adapter=resolved_adapter,
        authorization=resolved_authorization,
        **resolved_config,
    )
    logger.info("M365 Agents SDK initialized successfully.")
    return built_app, resolved_adapter


def build_bridge_handler(
    agent_app: AgentApplication,
    adapter: HttpAdapterBase,
    *,
    digital_worker: bool,
    is_hosted: bool,
    bot_app_id: str,
) -> BridgeHandler:
    """Bind a Starlette request handler to an app + adapter + outbound-auth model.

    The outbound-auth inputs are captured here at build time; the returned handler
    synthesizes the per-turn outbound claims, attaches them to the request, and
    drives the Starlette :class:`~._cloud_adapter.StarletteCloudAdapter`.

    :param agent_app: The ``AgentApplication`` used to process each turn.
    :type agent_app: ~microsoft_agents.hosting.core.AgentApplication
    :param adapter: The HTTP adapter providing ``process_request``.
    :type adapter: ~microsoft_agents.hosting.core.HttpAdapterBase
    :keyword digital_worker: The selected outbound-auth model.
    :paramtype digital_worker: bool
    :keyword is_hosted: Whether the agent runs inside a Foundry-hosted container.
    :paramtype is_hosted: bool
    :keyword bot_app_id: The Bot Connector client id (empty when unset).
    :paramtype bot_app_id: str
    :return: An async Starlette request handler.
    :rtype: Callable[[~starlette.requests.Request], Awaitable[~starlette.responses.Response]]
    """
    from ._cloud_adapter import StarletteCloudAdapter

    cloud_adapter = StarletteCloudAdapter(adapter)

    async def bridge_handler(request: Request) -> Response:
        # pylint: disable=import-error,no-name-in-module
        from microsoft_agents.hosting.core import ClaimsIdentity

        # Synthesize the outbound claims for this turn and attach them to the
        # request so the framework adapter reads them via get_claims_identity
        # (mirrors how the SDK adapters read claims set by auth middleware).
        request.state.claims_identity = _build_outbound_claims(
            ClaimsIdentity,
            digital_worker=digital_worker,
            is_hosted=is_hosted,
            bot_app_id=bot_app_id,
        )
        return await cloud_adapter.process(request, agent_app)

    return bridge_handler


def _build_outbound_claims(
    claims_cls: type[ClaimsIdentity],
    *,
    digital_worker: bool,
    is_hosted: bool,
    bot_app_id: str,
) -> ClaimsIdentity:
    """Build the outbound ``ClaimsIdentity`` for the turn per the resolved values.

    :param claims_cls: The M365 ``ClaimsIdentity`` class (injected to keep the
        M365 import local to the turn path).
    :type claims_cls: type[~microsoft_agents.hosting.core.ClaimsIdentity]
    :keyword digital_worker: The selected outbound-auth model.
    :paramtype digital_worker: bool
    :keyword is_hosted: Whether the agent runs inside a Foundry-hosted container.
    :paramtype is_hosted: bool
    :keyword bot_app_id: The Bot Connector client id (empty when unset).
    :paramtype bot_app_id: str
    :return: The claims identity to present to the adapter for the outbound reply.
    :rtype: ~microsoft_agents.hosting.core.ClaimsIdentity
    """
    if digital_worker:
        # Digital-worker model: anonymous claims; the FMI patch supplies the
        # outbound token via the federated-identity exchange.
        return claims_cls({}, is_authenticated=False, authentication_type=OutboundAuth.AUTH_TYPE_ANONYMOUS)

    if use_anonymous_outbound(digital_worker=digital_worker, is_hosted=is_hosted, bot_app_id=bot_app_id):
        # Simple model, running locally with no Bot Connector credential: no
        # managed identity exists off-box to mint a Bot Connector token, so use
        # anonymous claims (the adapter then skips outbound token minting). This
        # enables local round-trips via local test channels (for example the
        # Microsoft 365 Agents Playground emulator channel) without a Bot
        # registration.
        logger.warning(
            "LOCAL DEV: FOUNDRY_HOSTING_ENVIRONMENT is unset and no Bot Connector "
            "credential (%s) is configured; using anonymous outbound auth. This is "
            "NOT valid for production and only works with local test channels such "
            "as the Microsoft 365 Agents Playground 'emulator' channel.",
            OutboundAuth.CLAIM_APP_ID,
        )
        return claims_cls({}, is_authenticated=False, authentication_type=OutboundAuth.AUTH_TYPE_ANONYMOUS)

    # Simple model (default): present authenticated claims whose appid matches the
    # service-connection client id (the agent instance identity). This makes the
    # adapter use the real MSAL UserManagedIdentity connection for the outbound
    # reply instead of an anonymous/empty token.
    claim_dict = {OutboundAuth.CLAIM_APP_ID: bot_app_id, OutboundAuth.CLAIM_AUDIENCE: bot_app_id} if bot_app_id else {}
    return claims_cls(claim_dict, is_authenticated=True, authentication_type=OutboundAuth.AUTH_TYPE_BEARER)

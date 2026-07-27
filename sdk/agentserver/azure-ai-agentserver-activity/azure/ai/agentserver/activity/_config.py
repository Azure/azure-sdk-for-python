# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Connection-config resolution for the M365 activity host.

The connection config is resolved from the Foundry-native identity into a plain
``CONNECTIONS__*`` mapping (see :func:`get_hosted_agent_env`), and the
outbound-auth decision is a pure function of the resolved values
(:func:`use_anonymous_outbound`). Both are pure helpers: they read ``os.environ``
at call time and never write to it, so the host can resolve the connection config
once at construction without mutating process-global state.
"""

from __future__ import annotations

import os

from azure.ai.agentserver.core._config import (  # pylint: disable=import-error,no-name-in-module
    resolve_agent_blueprint_id,
    resolve_agent_tenant_id,
)

from ._constants import ConnectionSettings, FoundryEnv, OutboundAuth


def get_hosted_agent_env(*, digital_worker: bool = False) -> dict[str, str]:
    """Return a config mapping with the ``CONNECTIONS__*`` settings the M365 SDK needs.

    Builds and returns a **new** mapping — a copy of the process environment
    overlaid with the ``CONNECTIONS__*`` connection settings derived from the
    Foundry-native identity. It **never mutates** ``os.environ``; existing
    explicit values are preserved (never overwritten). Pass the result straight
    to ``load_configuration_from_env(...)``::

        from azure.ai.agentserver.activity import get_hosted_agent_env
        from microsoft_agents.activity import load_configuration_from_env

        env = get_hosted_agent_env()
        agents_sdk_config = load_configuration_from_env(env)

    The identity source differs by auth model:

    * **Simple** (``digital_worker=False``, default): the instance client id
      (``FOUNDRY_AGENT_INSTANCE_CLIENT_ID``), scoped to the Bot Framework.
    * **Digital worker** (``digital_worker=True``): the blueprint client id
      (via ``resolve_agent_blueprint_id``), scoped to the agentic resource.

    :keyword digital_worker: Selects the outbound-auth model to derive settings
        for. Defaults to the simple model.
    :paramtype digital_worker: bool
    :return: A new mapping ``{**os.environ, **derived CONNECTIONS__*}``.
    :rtype: dict[str, str]
    """
    if digital_worker:
        scope = OutboundAuth.AGENTIC_SCOPE
        client_id = resolve_agent_blueprint_id().strip()
    else:
        scope = OutboundAuth.BOTFRAMEWORK_SCOPE
        client_id = os.environ.get(FoundryEnv.INSTANCE_CLIENT_ID, "").strip()

    settings: dict[str, str] = dict(os.environ)

    def set_if_missing(name: str, value: str) -> None:
        if value and not settings.get(name, "").strip():
            settings[name] = value

    set_if_missing(ConnectionSettings.AUTH_TYPE, ConnectionSettings.AUTH_TYPE_USER_MANAGED_IDENTITY)
    set_if_missing(ConnectionSettings.SCOPE_0, scope)
    set_if_missing(ConnectionSettings.MAP_0_SERVICE_URL, ConnectionSettings.MAP_SERVICE_URL_WILDCARD)
    set_if_missing(ConnectionSettings.MAP_0_CONNECTION, ConnectionSettings.SERVICE_CONNECTION_NAME)

    tenant_id = resolve_agent_tenant_id().strip()
    set_if_missing(ConnectionSettings.CLIENT_ID, client_id)
    set_if_missing(ConnectionSettings.TENANT_ID, tenant_id)
    set_if_missing(
        ConnectionSettings.AUTHORITY,
        ConnectionSettings.AUTHORITY_TEMPLATE.format(tenant_id=tenant_id) if tenant_id else "",
    )
    return settings


def use_anonymous_outbound(*, digital_worker: bool, is_hosted: bool, bot_app_id: str) -> bool:
    """Whether outbound replies should use anonymous (empty-token) auth.

    Pure decision over the resolved values (no process-global reads). The
    digital-worker model never uses this path (its FMI patch supplies the
    outbound token). For the simple model, a managed-identity Bot Connector token
    can only be minted inside a hosted container; running outside a hosted
    container **and** with no Bot Connector credential configured falls back to
    anonymous claims so local runs can round-trip through local test channels
    (for example the Microsoft 365 Agents Playground ``emulator`` channel)
    without a Bot registration.

    :keyword digital_worker: The selected outbound-auth model.
    :paramtype digital_worker: bool
    :keyword is_hosted: Whether the agent runs inside a Foundry-hosted container.
    :paramtype is_hosted: bool
    :keyword bot_app_id: The resolved Bot Connector client id (empty when unset).
    :paramtype bot_app_id: str
    :return: ``True`` to use anonymous outbound auth, ``False`` otherwise.
    :rtype: bool
    """
    if digital_worker:
        return False
    return not is_hosted and not bot_app_id

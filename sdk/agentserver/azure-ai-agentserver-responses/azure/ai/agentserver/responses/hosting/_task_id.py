# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Deterministic task ID derivation for resilient responses."""

from __future__ import annotations

import hashlib


def derive_chain_id(
    *,
    conversation_id: str | None,
    previous_response_id: str | None,
    response_id: str,
    steerable: bool = True,
) -> str:
    """Derive the conversation chain id (partition key) for a response.

    The chain id is the stable identifier shared by every response that
    belongs to the same logical multi-turn conversation. It is computed
    from the same priority rules as :func:`derive_task_id` but returns
    the partition value directly (without the agent / session salt or
    hashing), so handlers can use it as a key into their own state
    (e.g., upstream SDK session ids, per-conversation rate limits,
    application-side conversation indexes).

    Priority:

    1. ``conversation_id`` — explicit conversation scope.
    2. ``previous_response_id`` — when ``steerable=True``, the chain id is
       inherited from the parent so sequential turns share an id;
       when ``steerable=False``, each fork gets a distinct id
       (using ``response_id``).
    3. ``response_id`` — fallback for the first (root) response in a chain.

    :keyword conversation_id: Explicit conversation scope.
    :paramtype conversation_id: str | None
    :keyword previous_response_id: Chain parent.
    :paramtype previous_response_id: str | None
    :keyword response_id: This response's unique id (fallback / fork key).
    :paramtype response_id: str
    :keyword steerable: Whether steering is enabled.
    :paramtype steerable: bool
    :returns: The chain partition value (without agent / session salt).
    :rtype: str
    """
    if conversation_id:
        return conversation_id
    if previous_response_id:
        if steerable:
            return previous_response_id
        return response_id
    return response_id


def derive_task_id(
    *,
    conversation_id: str | None,
    previous_response_id: str | None,
    response_id: str,
    agent_name: str,
    session_id: str,
    steerable: bool = True,
) -> str:
    """Derive a deterministic task ID for a conversation chain.

    Priority order for the partition key:
    1. ``conversation_id`` — when present, all turns share one task.
    2. ``previous_response_id`` — when steerable=True, sequential chain
       shares one task; when steerable=False, each fork gets its own ID
       (using response_id).
    3. ``response_id`` — fallback for standalone responses.

    The ID incorporates ``agent_name`` and ``session_id`` to prevent
    cross-agent and cross-session collisions.

    :keyword conversation_id: Explicit conversation scope (highest priority).
    :paramtype conversation_id: str | None
    :keyword previous_response_id: Chain parent (used when no conversation_id).
    :paramtype previous_response_id: str | None
    :keyword response_id: This response's unique ID (fallback / fork key).
    :paramtype response_id: str
    :keyword agent_name: Agent identity for collision avoidance.
    :paramtype agent_name: str
    :keyword session_id: Session scope identifier.
    :paramtype session_id: str
    :keyword steerable: Whether steering is enabled. When False and only
        previous_response_id is present, response_id is used instead
        (enabling parallel forks).
    :paramtype steerable: bool
    :returns: A deterministic string suitable as a resilient task ID.
    :rtype: str
    """
    # Reuse the chain derivation so both helpers stay in lockstep.
    chain = derive_chain_id(
        conversation_id=conversation_id,
        previous_response_id=previous_response_id,
        response_id=response_id,
        steerable=steerable,
    )
    if conversation_id:
        partition_key = f"conv:{chain}"
    elif previous_response_id:
        if steerable:
            partition_key = f"chain:{chain}"
        else:
            partition_key = f"fork:{chain}"
    else:
        partition_key = f"resp:{chain}"

    # Combine with agent + session for global uniqueness
    composite = f"{agent_name}:{session_id}:{partition_key}"

    # Produce a stable hash
    digest = hashlib.sha256(composite.encode("utf-8")).hexdigest()[:32]
    return f"resilient-resp-{digest}"

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Deterministic task ID derivation for durable responses."""

from __future__ import annotations

import hashlib


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

    :param conversation_id: Explicit conversation scope (highest priority).
    :param previous_response_id: Chain parent (used when no conversation_id).
    :param response_id: This response's unique ID (fallback / fork key).
    :param agent_name: Agent identity for collision avoidance.
    :param session_id: Session scope identifier.
    :param steerable: Whether steering is enabled. When False and only
        previous_response_id is present, response_id is used instead
        (enabling parallel forks).
    :returns: A deterministic string suitable as a durable task ID.
    """
    # Determine the partition key based on priority
    if conversation_id:
        partition_key = f"conv:{conversation_id}"
    elif previous_response_id:
        if steerable:
            # Serial chain — all turns with same parent share a task
            partition_key = f"chain:{previous_response_id}"
        else:
            # Parallel fork — each response gets its own task
            partition_key = f"fork:{response_id}"
    else:
        # Standalone response
        partition_key = f"resp:{response_id}"

    # Combine with agent + session for global uniqueness
    composite = f"{agent_name}:{session_id}:{partition_key}"

    # Produce a stable hash
    digest = hashlib.sha256(composite.encode("utf-8")).hexdigest()[:32]
    return f"durable-resp-{digest}"

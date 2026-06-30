# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Resilient-task ID derivation.

The resilient task that backs a conversation is identified by the conversation's
chain identity (:func:`._chain_id.derive_conversation_chain_id`) with a fixed
prefix — ``task_id == f"{_TASK_ID_PREFIX}-{chain_id}"``. The chain identity is the
primary concept and lives in :mod:`._chain_id`; this module only adds the prefix
so the task and the handler-facing ``conversation_chain_id`` can never drift.
"""

from __future__ import annotations

from ._chain_id import derive_conversation_chain_id

#: Prefix for the resilient-task id. The task id is this prefix joined to the
#: ``conversation_chain_id`` hash, so ``task_id == f"{_TASK_ID_PREFIX}-{chain_id}"``.
_TASK_ID_PREFIX = "resilient-resp"


def derive_task_id(
    *,
    conversation_id: str | None,
    previous_response_id: str | None,
    response_id: str,
    agent_name: str,
    session_id: str,
    steerable: bool = True,
) -> str:
    """Derive the resilient-task id for a conversation chain.

    The task id is the :func:`._chain_id.derive_conversation_chain_id` hash with a
    fixed prefix, so the resilient task backing a conversation and the
    handler-facing ``conversation_chain_id`` always share one identity.

    :keyword conversation_id: Explicit conversation scope (highest priority).
    :paramtype conversation_id: str | None
    :keyword previous_response_id: Chain parent (used when no conversation_id).
    :paramtype previous_response_id: str | None
    :keyword response_id: This response's unique id (fallback / fork key).
    :paramtype response_id: str
    :keyword agent_name: Agent identity for collision avoidance.
    :paramtype agent_name: str
    :keyword session_id: Session scope identifier.
    :paramtype session_id: str
    :keyword steerable: Whether steerable conversations are enabled.
    :paramtype steerable: bool
    :returns: A deterministic resilient-task id (``{prefix}-{chain_id}``).
    :rtype: str
    """
    chain_id = derive_conversation_chain_id(
        conversation_id=conversation_id,
        previous_response_id=previous_response_id,
        response_id=response_id,
        agent_name=agent_name,
        session_id=session_id,
        steerable=steerable,
    )
    return f"{_TASK_ID_PREFIX}-{chain_id}"

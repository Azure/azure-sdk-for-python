# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Conversation chain identity.

A conversation's stable identity is the *partition key* embedded in its response
IDs. IDs have the shape ``{prefix}_{partitionKey}{entropy}``; when a response ID
is generated it inherits the partition key of its ``previous_response_id`` /
``conversation_id`` hint (see
:class:`~azure.ai.agentserver.responses._id_generator.IdGenerator`). So every
response in a chain carries the *same* embedded partition key, and extracting it
yields a value that is stable across every turn of the chain.

:func:`derive_conversation_chain_id` is the foundational concept here — the
agent/session-scoped hash of that partition, exposed to handlers as
``ResponseContext.conversation_chain_id`` and reused (with a fixed prefix) as the
resilient task id. See :mod:`._task_id`.

Known limitation: the chain identity is derived from framework-generated IDs. A
client that supplies its own ``response_id`` (via the ``x-agent-response-id``
header or an explicit request field) carrying a mismatched embedded partition can
shift the chain identity for subsequent turns.
"""

from __future__ import annotations

import hashlib

from .._id_generator import IdGenerator

#: Length of the hex digest used for the chain id (and therefore the task id).
_CHAIN_ID_HEX_LENGTH = 32


def _extract_partition_or_raw(id_value: str) -> str:
    """Extract the embedded partition key from *id_value*, or return it unchanged.

    Framework-generated IDs carry an embedded partition key that is shared across
    a chain; extracting it gives the stable chain identity. Values not in the ID
    format (e.g. a raw ``conversation_id``) have no embedded key — they are
    themselves the stable identity, so they are returned as-is.

    :param id_value: An ID (or raw identifier) to reduce to its chain partition.
    :type id_value: str
    :returns: The embedded partition key, or *id_value* unchanged.
    :rtype: str
    """
    try:
        return IdGenerator.extract_partition_key(id_value)
    except (ValueError, TypeError):
        return id_value


def _chain_partition(
    *,
    conversation_id: str | None,
    previous_response_id: str | None,
    response_id: str,
    steerable: bool,
) -> tuple[str, str]:
    """Resolve the ``(discriminator, partition)`` that identifies the chain.

    Priority:

    1. ``conversation_id`` — explicit conversation scope (extract its partition
       key, or use it raw when it is not in ID format).
    2. ``steerable`` — the sequential chain shares one identity: extract the
       partition key from ``previous_response_id`` (or ``response_id`` on the
       first turn). Because chained response IDs inherit one partition key, every
       turn resolves to the same value.
    3. otherwise (non-steerable) — each request is its own fork; the FULL
       ``response_id`` (entropy included) keeps concurrent forks distinct.

    The discriminator namespaces the partition by source type so that, e.g., a
    client-supplied ``conversation_id`` cannot collide with an extracted
    partition key or a response id.

    :keyword conversation_id: Explicit conversation scope.
    :paramtype conversation_id: str | None
    :keyword previous_response_id: Chain parent.
    :paramtype previous_response_id: str | None
    :keyword response_id: This response's unique id.
    :paramtype response_id: str
    :keyword steerable: Whether steerable conversations are enabled.
    :paramtype steerable: bool
    :returns: A ``(discriminator, partition)`` tuple.
    :rtype: tuple[str, str]
    """
    if conversation_id:
        return "conv", _extract_partition_or_raw(conversation_id)
    if steerable:
        source = previous_response_id or response_id
        return "chain", _extract_partition_or_raw(source)
    # Non-steerable: keep parallel forks distinct via the full response_id.
    discriminator = "fork" if previous_response_id else "resp"
    return discriminator, response_id


def derive_conversation_chain_id(
    *,
    conversation_id: str | None,
    previous_response_id: str | None,
    response_id: str,
    agent_name: str,
    session_id: str,
    steerable: bool = True,
) -> str:
    """Derive the stable, agent/session-scoped conversation chain id.

    The id is the same for every turn of a conversation chain (see module
    docstring). It is a hex digest, so it is opaque and fixed-length — suitable
    as a handler-side key (upstream SDK session id, per-conversation indexes).

    :keyword conversation_id: Explicit conversation scope (highest priority).
    :paramtype conversation_id: str | None
    :keyword previous_response_id: Chain parent (used when no conversation_id).
    :paramtype previous_response_id: str | None
    :keyword response_id: This response's unique id (fallback / fork key).
    :paramtype response_id: str
    :keyword agent_name: Agent identity, for cross-agent scoping.
    :paramtype agent_name: str
    :keyword session_id: Session scope identifier.
    :paramtype session_id: str
    :keyword steerable: Whether steerable conversations are enabled.
    :paramtype steerable: bool
    :returns: A stable hex chain id.
    :rtype: str
    """
    discriminator, partition = _chain_partition(
        conversation_id=conversation_id,
        previous_response_id=previous_response_id,
        response_id=response_id,
        steerable=steerable,
    )
    composite = f"{agent_name}:{session_id}:{discriminator}:{partition}"
    return hashlib.sha256(composite.encode("utf-8")).hexdigest()[:_CHAIN_ID_HEX_LENGTH]

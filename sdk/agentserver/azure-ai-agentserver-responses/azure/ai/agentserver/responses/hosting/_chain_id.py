# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Conversation chain identity (Spec 038 — native per-case ids).

The resilient ``task_id`` that backs a response must be **shared** across every
turn of one conversation chain (so a later / steered turn attaches to the same
in-flight suspendable task) and **distinct** across unrelated requests. What
counts as "one chain" is the per-request matrix, giving three cases:

1. ``conversation_id`` present → the chain is the conversation.
2. steerable, no ``conversation_id`` → the chain is the ``previous_response_id``
   linkage (chained response ids share one partition key).
3. everything else → one-shot; each request stands alone.

The id follows the system's :class:`~azure.ai.agentserver.responses._id_generator.IdGenerator`
convention (``{prefix}_{partitionKey}{trailer}``) so it looks native and embeds
the chain's partition key for co-location:

* case 1 → ``cchain_{partition(conversation_id)}{scope}``
* case 2 → ``rchain_{partition(previous_response_id or response_id)}{scope}``
* case 3 → the ``response_id`` verbatim (already globally unique + native).

``scope`` is a deterministic 32-char alnum digest of ``agent_name`` +
``session_id`` (both are too long / too arbitrary to embed — ``agent_name`` is
DNS-style ≤63 chars, ``session_id`` is any string ≤128 chars — so they are
hashed). The digest fills the native "entropy" slot; because ``agent_name``
cannot contain the ``\\x1f`` separator, the ``(agent, session)`` pair encodes
injectively even when ``session_id`` contains arbitrary bytes.

When no private task session scope is available,
``task_id == conversation_chain_id``. Hosted deployments may instead scope the
physical task ID with a system-generated session GUID while preserving this
public chain identity.

Known limitation: the chain identity is derived from framework-generated ids. A
client that supplies its own ``response_id`` / ``conversation_id`` carrying a
mismatched embedded partition can shift the chain identity for subsequent turns.
"""

from __future__ import annotations

import base64
import hashlib

from .._id_generator import IdGenerator

#: Prefix for a conversation-scoped chain id (native IdGenerator convention).
_CONV_CHAIN_PREFIX = "cchain"
#: Prefix for a steerable response-linkage chain id.
_RESP_CHAIN_PREFIX = "rchain"

#: Width of the deterministic (agent, session) scope trailer, matching the
#: native IdGenerator entropy slot.
_SCOPE_LENGTH = 32
#: Unit separator — cannot appear in a DNS ``agent_name``, so the constrained
#: field first makes ``(agent, session)`` an injective encoding.
_SEP = "\x1f"


def _det_alnum(seed: str, length: int) -> str:
    """Return a deterministic alphanumeric digest of *seed* of *length* chars.

    Mirrors :meth:`IdGenerator._generate_entropy`'s charset (``[A-Za-z0-9]``)
    but is seeded deterministically (SHA-256 of ``seed:<counter>``) rather than
    from random bytes, so the resulting id is reproducible across turns and on
    cross-process recovery.

    :param seed: The deterministic seed.
    :type seed: str
    :param length: The number of alphanumeric characters to return.
    :type length: int
    :returns: A deterministic alphanumeric string of the requested length.
    :rtype: str
    """
    out: list[str] = []
    counter = 0
    while len(out) < length:
        block = base64.b64encode(hashlib.sha256(f"{seed}:{counter}".encode("utf-8")).digest()).decode("ascii")
        out.extend(c for c in block if c.isalnum())
        counter += 1
    return "".join(out[:length])


def _scope(agent_name: str, session_id: str) -> str:
    """Return the deterministic (agent, session) scope trailer.

    :param agent_name: Agent identity (DNS-style, ≤63 chars).
    :type agent_name: str
    :param session_id: Session identifier (any string, ≤128 chars).
    :type session_id: str
    :returns: A deterministic 32-char alphanumeric scope.
    :rtype: str
    """
    return _det_alnum(f"{agent_name}{_SEP}{session_id}", _SCOPE_LENGTH)


def _partition_key(source_id: str, agent_name: str, session_id: str) -> str:
    """Return the 18-char partition key for the chain.

    For a framework-generated id the real embedded partition key is extracted
    (so the chain/task co-locates with its responses); for a value that is not
    in id format (e.g. a raw client ``conversation_id``) a partition key is
    derived deterministically.

    :param source_id: The id the partition is resolved from.
    :type source_id: str
    :param agent_name: Agent identity, used in the deterministic fallback seed.
    :type agent_name: str
    :param session_id: Session identifier, used in the deterministic fallback seed.
    :type session_id: str
    :returns: An 18-character partition key (``{16-hex}00``).
    :rtype: str
    """
    try:
        return IdGenerator.extract_partition_key(source_id)
    except (ValueError, TypeError):
        seed = f"{agent_name}{_SEP}{session_id}{_SEP}{source_id}"
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16] + "00"


def derive_conversation_chain_id(
    *,
    conversation_id: str | None,
    previous_response_id: str | None,
    response_id: str,
    agent_name: str,
    session_id: str,
    steerable: bool = True,
) -> str:
    """Derive the stable public conversation chain identity.

    The id is the same for every turn of a chain and reconstructable on recovery
    (a pure function of the persisted inputs). See the module docstring for the
    per-case id shapes. A hosted physical task ID can use a private session-GUID
    scope and therefore differ from this handler-facing identity.

    :keyword conversation_id: Explicit conversation scope (highest priority).
    :paramtype conversation_id: str | None
    :keyword previous_response_id: Chain parent (used when no conversation_id).
    :paramtype previous_response_id: str | None
    :keyword response_id: This response's unique id (fallback / one-shot key).
    :paramtype response_id: str
    :keyword agent_name: Agent identity, for cross-agent scoping.
    :paramtype agent_name: str
    :keyword session_id: Session scope identifier.
    :paramtype session_id: str
    :keyword steerable: Whether steerable conversations are enabled.
    :paramtype steerable: bool
    :returns: The stable conversation chain id.
    :rtype: str
    """
    if conversation_id:
        pk = _partition_key(conversation_id, agent_name, session_id)
        return f"{_CONV_CHAIN_PREFIX}_{pk}{_scope(agent_name, session_id)}"
    if steerable:
        source_id = previous_response_id or response_id
        pk = _partition_key(source_id, agent_name, session_id)
        return f"{_RESP_CHAIN_PREFIX}_{pk}{_scope(agent_name, session_id)}"
    # Case 3 — one-shot: no chain to share; the response id is already globally
    # unique + native, so it IS the task id.
    return response_id

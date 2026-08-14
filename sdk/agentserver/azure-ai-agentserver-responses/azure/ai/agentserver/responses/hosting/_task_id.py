# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Resilient-task ID derivation.

The resilient task that backs a conversation is identified by the conversation's
chain identity (:func:`._chain_id.derive_conversation_chain_id`). Since Spec 038
the chain id is itself a native, self-prefixed id (``cchain_…`` / ``rchain_…`` /
a verbatim ``response_id``), so ``task_id == conversation_chain_id`` exactly —
there is no separate wrapper prefix, and the resilient task and the
handler-facing ``conversation_chain_id`` can never drift.
"""

from __future__ import annotations

import re

from ._chain_id import derive_conversation_chain_id

#: The Public Task API id contract (``^[a-zA-Z0-9_-]{1,128}$``) — stricter than
#: the core primitive's ``_validate_task_id`` (which also permits ``.``/``:``).
#: In case 3 the ``task_id`` is a verbatim ``response_id``, which may be
#: client-supplied via ``x-agent-response-id`` and is only structurally
#: validated upstream (not charset-validated), so we enforce the strict
#: contract here.
_TASK_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")


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

    The task id **is** the :func:`._chain_id.derive_conversation_chain_id`
    value, so the resilient task backing a conversation and the handler-facing
    ``conversation_chain_id`` are one and the same identity.

    :keyword conversation_id: Explicit conversation scope (highest priority).
    :paramtype conversation_id: str | None
    :keyword previous_response_id: Chain parent (used when no conversation_id).
    :paramtype previous_response_id: str | None
    :keyword response_id: This response's unique id (fallback / one-shot key).
    :paramtype response_id: str
    :keyword agent_name: Agent identity for cross-agent scoping.
    :paramtype agent_name: str
    :keyword session_id: Session scope identifier.
    :paramtype session_id: str
    :keyword steerable: Whether steerable conversations are enabled.
    :paramtype steerable: bool
    :returns: A deterministic resilient-task id (== the conversation chain id).
    :rtype: str
    """
    task_id = derive_conversation_chain_id(
        conversation_id=conversation_id,
        previous_response_id=previous_response_id,
        response_id=response_id,
        agent_name=agent_name,
        session_id=session_id,
        steerable=steerable,
    )
    # Fail fast on the strict Public Task API contract. In case 3 the id is a
    # verbatim (possibly client-supplied) ``response_id`` whose charset is not
    # otherwise validated to this stricter rule, so this is a real check (not an
    # ``assert``, which ``python -O`` would strip).
    if not _TASK_ID_RE.match(task_id):
        raise ValueError(f"derived task_id violates the Task API contract [a-zA-Z0-9_-]{{1,128}}: {task_id!r}")
    return task_id

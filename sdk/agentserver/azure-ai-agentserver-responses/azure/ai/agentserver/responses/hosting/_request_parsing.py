# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Request pre-validation, identity resolution, and input extraction helpers."""

from __future__ import annotations

import hashlib
import os
from copy import deepcopy
from typing import Any, Mapping

from .._id_generator import IdGenerator
from ..models._generated import AgentReference, CreateResponse
from ..models.errors import RequestValidationError

_X_AGENT_RESPONSE_ID_HEADER = "x-agent-response-id"

_DEFAULT_AGENT_REFERENCE_NAME = "server-default-agent"

# Intentionally capped at 63 hex characters per spec. A full SHA-256 hex digest
# is 64 characters, but the session ID contract uses 63. Do not change this
# without reviewing the cross-language contract.
_SESSION_ID_LENGTH = 63


def _extract_input_items(raw_payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract and deep-copy the ``input`` items array from a raw request payload.

    :param raw_payload: Raw decoded JSON request body.
    :type raw_payload: dict[str, Any]
    :return: List of deep-copied input item dictionaries, or empty list if absent.
    :rtype: list[dict[str, Any]]
    """
    if not isinstance(raw_payload, dict):
        return []

    value = raw_payload.get("input")
    if not isinstance(value, list):
        return []

    extracted: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, dict):
            extracted.append(deepcopy(item))
    return extracted


def _extract_previous_response_id(raw_payload: dict[str, Any]) -> str | None:
    """Extract the ``previous_response_id`` string from a raw request payload.

    :param raw_payload: Raw decoded JSON request body.
    :type raw_payload: dict[str, Any]
    :return: The previous response ID string, or ``None`` if absent or invalid.
    :rtype: str | None
    """
    if not isinstance(raw_payload, dict):
        return None
    value = raw_payload.get("previous_response_id")
    return value if isinstance(value, str) and value else None


def _extract_item_id(item: dict[str, Any]) -> str | None:
    """Extract the ``id`` field from an input item dictionary.

    :param item: An input item dictionary.
    :type item: dict[str, Any]
    :return: The item ID as a string, or ``None`` if not present.
    :rtype: str | None
    """
    value = item.get("id")
    return str(value) if value is not None else None


def _apply_item_cursors(items: list[dict[str, Any]], *, after: str | None, before: str | None) -> list[dict[str, Any]]:
    """Apply cursor-based pagination to a list of input items.

    :param items: Ordered list of input item dictionaries.
    :type items: list[dict[str, Any]]
    :keyword after: Item ID to start after (exclusive lower bound), or ``None``.
    :keyword type after: str | None
    :keyword before: Item ID to stop before (exclusive upper bound), or ``None``.
    :keyword type before: str | None
    :return: The subset of items within the cursor window.
    :rtype: list[dict[str, Any]]
    """
    scoped = items

    if after is not None:
        after_index = next((index for index, item in enumerate(scoped) if _extract_item_id(item) == after), None)
        if after_index is not None:
            scoped = scoped[after_index + 1 :]

    if before is not None:
        before_index = next((index for index, item in enumerate(scoped) if _extract_item_id(item) == before), None)
        if before_index is not None:
            scoped = scoped[:before_index]

    return scoped


def _validate_response_id(response_id: str) -> None:
    """Validate that a response ID matches the expected canonical format.

    :param response_id: The response ID string to validate.
    :type response_id: str
    :return: None
    :rtype: None
    :raises RequestValidationError: If the ID format is invalid.
    """
    is_valid_id, _ = IdGenerator.is_valid(response_id)
    if not is_valid_id:
        raise RequestValidationError(
            "response_id must be in format caresp_<18-char partition key><32-char alphanumeric entropy>",
            code="invalid_request",
            param="response_id",
        )


def _normalize_agent_reference(value: Any) -> AgentReference | dict[str, Any]:
    """Normalize an agent reference value into a validated model or empty dict.

    If *value* is ``None``, an empty dict is returned as a sentinel for
    "no agent_reference was provided".  Callers use truthiness to detect
    the sentinel and skip auto-stamping output items.

    :param value: Raw agent reference from the request (dict, model, or ``None``).
    :type value: Any
    :return: An :class:`AgentReference` model instance,
        or ``{}`` when no agent_reference was provided.
    :rtype: AgentReference | dict[str, Any]
    :raises RequestValidationError: If the value is not a valid agent reference.
    """
    if value is None:
        return {}

    if hasattr(value, "as_dict"):
        candidate = value.as_dict()
    elif isinstance(value, dict):
        candidate = dict(value)
    else:
        raise RequestValidationError(
            "agent_reference must be an object",
            code="invalid_request",
            param="agent_reference",
        )

    candidate.setdefault("type", "agent_reference")
    name = candidate.get("name")
    reference_type = candidate.get("type")

    if reference_type != "agent_reference":
        raise RequestValidationError(
            "agent_reference.type must be 'agent_reference'",
            code="invalid_request",
            param="agent_reference.type",
        )

    if not isinstance(name, str) or not name.strip():
        raise RequestValidationError(
            "agent_reference.name must be a non-empty string",
            code="invalid_request",
            param="agent_reference.name",
        )

    candidate["name"] = name.strip()
    return AgentReference(candidate)


def _prevalidate_identity_payload(payload: dict[str, Any]) -> None:
    """Pre-validate identity-related fields in the raw request payload.

    Checks ``response_id`` format and ``agent_reference`` structure before full
    model parsing, so that identity errors surface early.

    :param payload: Raw decoded JSON request body.
    :type payload: dict[str, Any]
    :return: None
    :rtype: None
    :raises RequestValidationError: If identity fields are malformed.
    """
    if not isinstance(payload, dict):
        return

    raw_response_id = payload.get("response_id")
    if raw_response_id is not None:
        if not isinstance(raw_response_id, str) or not raw_response_id.strip():
            raise RequestValidationError(
                "response_id must be a non-empty string",
                code="invalid_request",
                param="response_id",
            )
        _validate_response_id(raw_response_id.strip())

    raw_agent_reference = payload.get("agent_reference")
    if raw_agent_reference is None:
        return

    if not isinstance(raw_agent_reference, dict):
        raise RequestValidationError(
            "agent_reference must be an object",
            code="invalid_request",
            param="agent_reference",
        )

    if raw_agent_reference.get("type") != "agent_reference":
        raise RequestValidationError(
            "agent_reference.type must be 'agent_reference'",
            code="invalid_request",
            param="agent_reference.type",
        )

    raw_name = raw_agent_reference.get("name")
    if not isinstance(raw_name, str) or not raw_name.strip():
        raise RequestValidationError(
            "agent_reference.name must be a non-empty string",
            code="invalid_request",
            param="agent_reference.name",
        )


def _resolve_identity_fields(
    parsed: CreateResponse,
    *,
    request_headers: Mapping[str, str] | None = None,
) -> tuple[str, AgentReference | dict[str, Any]]:
    """Resolve the response ID and agent reference from a parsed create request.

    **B38 — Response ID Resolution**: If the incoming request includes an
    ``x-agent-response-id`` HTTP header with a non-empty value, that value is
    used as the response ID.  Otherwise the library generates one using
    ``IdGenerator.new_response_id()``, using the ``previous_response_id`` or
    ``conversation`` ID as partition-key hint when available.

    :param parsed: Parsed ``CreateResponse`` model instance.
    :type parsed: CreateResponse
    :keyword request_headers: HTTP request headers mapping.
    :keyword type request_headers: Mapping[str, str] | None
    :return: A tuple of ``(response_id, agent_reference)``.  The agent reference
        is an :class:`AgentReference` model when provided, or an empty ``dict``
        sentinel when absent.
    :rtype: tuple[str, AgentReference | dict[str, Any]]
    :raises RequestValidationError: If the resolved response ID is invalid.
    """
    # B38: header override takes highest precedence
    header_response_id: str | None = None
    if request_headers is not None:
        raw_header = request_headers.get(_X_AGENT_RESPONSE_ID_HEADER, "")
        if isinstance(raw_header, str) and raw_header.strip():
            header_response_id = raw_header.strip()

    parsed_mapping = parsed.as_dict() if hasattr(parsed, "as_dict") else {}

    if header_response_id:
        response_id = header_response_id
    else:
        explicit_response_id = parsed_mapping.get("response_id") or getattr(parsed, "response_id", None)
        if isinstance(explicit_response_id, str) and explicit_response_id.strip():
            response_id = explicit_response_id.strip()
        else:
            # Use previous_response_id or conversation ID as partition key hint
            # for co-locating related response IDs in the same partition.
            # previous_response_id takes priority because it directly chains
            # responses, while conversation ID groups them more loosely.
            partition_hint = parsed_mapping.get("previous_response_id") or _resolve_conversation_id(parsed) or ""
            response_id = IdGenerator.new_response_id(partition_hint)

    _validate_response_id(response_id)
    agent_reference = _normalize_agent_reference(
        parsed_mapping.get("agent_reference")
        if isinstance(parsed_mapping, dict)
        else getattr(parsed, "agent_reference", None)
    )
    return response_id, agent_reference


def _resolve_conversation_id(parsed: CreateResponse) -> str | None:
    """Extract the conversation ID from a parsed ``CreateResponse`` request.

    Handles both a plain string value and a ``ConversationParam_2`` object
    (which carries the ID in its ``.id`` attribute).

    :param parsed: The parsed ``CreateResponse`` model instance.
    :type parsed: CreateResponse
    :returns: The conversation ID string, or ``None`` if not present.
    :rtype: str | None
    """
    raw = getattr(parsed, "conversation", None)
    if isinstance(raw, str):
        return raw or None
    if isinstance(raw, dict):
        cid = raw.get("id")
        return str(cid) if cid else None
    if raw is not None and hasattr(raw, "id"):
        return str(raw.id) or None
    return None


def _resolve_session_id(
    parsed: CreateResponse,
    payload: dict[str, Any],
    *,
    env_session_id: str = "",
    agent_reference: AgentReference | dict[str, Any] | None = None,
) -> str:
    """Resolve the session ID for a create-response request.

    **B39 — Session ID Resolution**: The library resolves ``agent_session_id``
    using the following priority chain:

    1. ``request.agent_session_id`` — payload field (client-supplied session affinity)
    2. ``env_session_id`` — platform-supplied (from ``AgentConfig.session_id``)
    3. **Deterministic derivation** — SHA-256 hash of ``agent_name:agent_version:partition_hint``
       where *partition_hint* is extracted from ``conversation_id`` or ``previous_response_id``.
    4. Random 63-char lowercase hex (one-shot, no conversational context)

    :param parsed: Parsed ``CreateResponse`` model instance.
    :type parsed: CreateResponse
    :param payload: Raw JSON payload dict.
    :type payload: dict[str, Any]
    :keyword env_session_id: Platform-supplied session ID from ``AgentConfig``
        (sourced from ``FOUNDRY_AGENT_SESSION_ID`` env var).  Defaults to ``""``.
    :keyword type env_session_id: str
    :keyword agent_reference: Agent reference containing name/version for
        deterministic session derivation.
    :keyword type agent_reference: AgentReference | dict[str, Any] | None
    :returns: The resolved session ID string.
    :rtype: str
    """
    # Priority 1: payload field
    session_id = getattr(parsed, "agent_session_id", None)
    if not isinstance(session_id, str) or not session_id.strip():
        # Also check the raw payload for when the field isn't in the model yet
        if isinstance(payload, dict):
            session_id = payload.get("agent_session_id")
    if isinstance(session_id, str) and session_id.strip():
        return session_id.strip()

    # Priority 2: platform-supplied session ID
    if env_session_id.strip():
        return env_session_id.strip()

    # Priority 3: deterministic derivation from conversation context
    conversation_id = _resolve_conversation_id(parsed)
    previous_response_id: str | None = None
    raw_prev = getattr(parsed, "previous_response_id", None)
    if isinstance(raw_prev, str) and raw_prev.strip():
        previous_response_id = raw_prev.strip()

    return derive_session_id(
        conversation_id=conversation_id,
        previous_response_id=previous_response_id,
        agent_reference=agent_reference,
    )


def derive_session_id(
    *,
    conversation_id: str | None = None,
    previous_response_id: str | None = None,
    agent_reference: AgentReference | dict[str, Any] | None = None,
) -> str:
    """Derive a deterministic session ID from conversational context.

    Mirrors the ``SessionIdDerivation.Derive`` logic per spec (minus the
    explicit session ID and env fallbacks which are handled by the caller):

    - If *conversation_id* or *previous_response_id* is available, extract
      the partition hint via :meth:`IdGenerator.extract_partition_key` and
      SHA-256 hash it with the agent identity.
    - Otherwise, generate a random 63-char lowercase hex string.

    :keyword conversation_id: Conversation ID from the request, if any.
    :keyword type conversation_id: str | None
    :keyword previous_response_id: Previous response ID, if any.
    :keyword type previous_response_id: str | None
    :keyword agent_reference: Agent reference containing name/version.
    :keyword type agent_reference: AgentReference | dict[str, Any] | None
    :returns: A 63-char lowercase hex session ID.
    :rtype: str
    """
    # Select partition source: conversation_id first, then previous_response_id
    partition_source = conversation_id or previous_response_id

    if partition_source:
        try:
            partition_hint = IdGenerator.extract_partition_key(partition_source)
        except (ValueError, TypeError):
            partition_hint = partition_source

        agent_name, agent_version = _extract_agent_identity(agent_reference)
        seed = f"{agent_name}:{agent_version}:{partition_hint}"
        return _compute_hex_hash(seed)

    # One-shot: no conversational context → random session
    return _generate_random_hex()


def _extract_agent_identity(
    agent_reference: AgentReference | dict[str, Any] | None,
) -> tuple[str, str]:
    """Extract (agent_name, agent_version) from an agent reference.

    :param agent_reference: Agent reference mapping or model instance.
    :type agent_reference: AgentReference | dict[str, Any] | None
    :returns: Tuple of (name, version) with fallback defaults.
    :rtype: tuple[str, str]
    """
    if agent_reference is None:
        return _DEFAULT_AGENT_REFERENCE_NAME, ""
    if isinstance(agent_reference, dict):
        name = agent_reference.get("name") or _DEFAULT_AGENT_REFERENCE_NAME
        version = agent_reference.get("version") or ""
        return str(name), str(version)
    name = getattr(agent_reference, "name", None) or _DEFAULT_AGENT_REFERENCE_NAME
    version = getattr(agent_reference, "version", None) or ""
    return str(name), str(version)


def _compute_hex_hash(value: str) -> str:
    """SHA-256 hash a string and return the first 63 lowercase hex chars.

    :param value: Input string to hash.
    :type value: str
    :returns: 63-char lowercase hex digest.
    :rtype: str
    """
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return digest[:_SESSION_ID_LENGTH]


def _generate_random_hex() -> str:
    """Generate a random 63-char lowercase hex string.

    :returns: 63-char lowercase hex string.
    :rtype: str
    """
    return os.urandom(32).hex()[:_SESSION_ID_LENGTH]

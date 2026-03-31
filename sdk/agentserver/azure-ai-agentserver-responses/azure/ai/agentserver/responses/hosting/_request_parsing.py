# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Request pre-validation, identity resolution, and input extraction helpers."""

from __future__ import annotations

import os
import uuid
from copy import deepcopy
from typing import Any, Mapping

from .._id_generator import IdGenerator
from ..models.errors import RequestValidationError

_X_AGENT_RESPONSE_ID_HEADER = "x-agent-response-id"
_FOUNDRY_AGENT_SESSION_ID_ENV = "FOUNDRY_AGENT_SESSION_ID"

_DEFAULT_AGENT_REFERENCE_NAME = "server-default-agent"


def _extract_input_items(raw_payload: Any) -> list[dict[str, Any]]:
    """Extract and deep-copy the ``input`` items array from a raw request payload.

    :param raw_payload: Raw decoded JSON request body.
    :type raw_payload: Any
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


def _extract_previous_response_id(raw_payload: Any) -> str | None:
    """Extract the ``previous_response_id`` string from a raw request payload.

    :param raw_payload: Raw decoded JSON request body.
    :type raw_payload: Any
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


def _normalize_agent_reference(value: Any) -> dict[str, Any]:
    """Normalize an agent reference value into a validated dictionary.

    If *value* is ``None``, a default agent reference is returned.

    :param value: Raw agent reference from the request (dict, model, or ``None``).
    :type value: Any
    :return: Normalized agent reference dictionary with ``type`` and ``name`` keys.
    :rtype: dict[str, Any]
    :raises RequestValidationError: If the value is not a valid agent reference.
    """
    if value is None:
        return {
            "type": "agent_reference",
            "name": _DEFAULT_AGENT_REFERENCE_NAME,
        }

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
    return candidate


def _prevalidate_identity_payload(payload: Any) -> None:
    """Pre-validate identity-related fields in the raw request payload.

    Checks ``response_id`` format and ``agent_reference`` structure before full
    model parsing, so that identity errors surface early.

    :param payload: Raw decoded JSON request body.
    :type payload: Any
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
    parsed: Any,
    *,
    request_headers: Mapping[str, str] | None = None,
) -> tuple[str, dict[str, Any]]:
    """Resolve the response ID and agent reference from a parsed create request.

    **S-047 — Response ID Resolution**: If the incoming request includes an
    ``x-agent-response-id`` HTTP header with a non-empty value, that value is
    used as the response ID.  Otherwise the library generates one using
    ``IdGenerator.new_response_id()``, using the ``previous_response_id`` or
    ``conversation`` ID as partition-key hint when available.

    :param parsed: Parsed ``CreateResponse`` model instance.
    :type parsed: Any
    :keyword request_headers: HTTP request headers mapping.
    :keyword type request_headers: Mapping[str, str] | None
    :return: A tuple of ``(response_id, agent_reference)``.
    :rtype: tuple[str, dict[str, Any]]
    :raises RequestValidationError: If the resolved response ID is invalid.
    """
    # S-047: header override takes highest precedence
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
            partition_hint = (
                parsed_mapping.get("previous_response_id")
                or _resolve_conversation_id(parsed)
                or ""
            )
            response_id = IdGenerator.new_response_id(partition_hint)

    _validate_response_id(response_id)
    agent_reference = _normalize_agent_reference(
        parsed_mapping.get("agent_reference") \
            if isinstance(parsed_mapping, dict) \
            else getattr(parsed, "agent_reference", None)
    )
    return response_id, agent_reference


def _resolve_conversation_id(parsed: Any) -> str | None:
    """Extract the conversation ID from a parsed ``CreateResponse`` request.

    Handles both a plain string value and a ``ConversationParam_2`` object
    (which carries the ID in its ``.id`` attribute).

    :param parsed: The parsed ``CreateResponse`` model instance.
    :type parsed: Any
    :returns: The conversation ID string, or ``None`` if not present.
    :rtype: str | None
    """
    raw = getattr(parsed, "conversation", None)
    if isinstance(raw, str):
        return raw or None
    if raw is not None and hasattr(raw, "id"):
        return str(raw.id) or None
    return None


def _resolve_session_id(parsed: Any, payload: Any) -> str:
    """Resolve the session ID for a create-response request.

    **S-048 — Session ID Resolution**: The library resolves ``agent_session_id``
    using the following priority chain:

    1. ``request.agent_session_id`` — payload field (client-supplied session affinity)
    2. ``FOUNDRY_AGENT_SESSION_ID`` environment variable (platform-supplied)
    3. Generated UUID (freshly generated as a string)

    :param parsed: Parsed ``CreateResponse`` model instance.
    :type parsed: Any
    :param payload: Raw JSON payload dict.
    :type payload: Any
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

    # Priority 2: environment variable
    env_session_id = os.environ.get(_FOUNDRY_AGENT_SESSION_ID_ENV, "")
    if env_session_id.strip():
        return env_session_id.strip()

    # Priority 3: generated UUID
    return str(uuid.uuid4())

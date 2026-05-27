# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Acceptance hook for steerable conversations.

When a new turn arrives for an already-active steerable task, the acceptance hook
generates the "queued" response returned to the HTTP caller. Developers can register
a custom hook via ``@app.response_acceptor`` to customize the queued response shape.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .._response_context import ResponseContext
    from ..models._generated import CreateResponse

logger = logging.getLogger("azure.ai.agentserver.responses.acceptance")

AcceptanceHookFn = Callable[["CreateResponse", "ResponseContext"], dict[str, Any]]


def generate_default_acceptance(
    *,
    response_id: str,
    model: str | None = None,
) -> dict[str, Any]:
    """Generate the default queued response envelope.

    Used when no custom acceptance hook is registered, or as fallback
    when a custom hook raises an error.

    :param response_id: The response ID for the queued turn.
    :param model: The model name from the request.
    :returns: A response dict with status="queued".
    """
    return {
        "id": response_id,
        "object": "response",
        "status": "queued",
        "model": model,
        "output": [],
    }


def dispatch_acceptance_hook(
    *,
    hook: AcceptanceHookFn | None,
    request: "CreateResponse",
    context: "ResponseContext",
    model: str | None = None,
) -> dict[str, Any]:
    """Call the acceptance hook or generate default queued response.

    If a custom hook is registered and succeeds, returns its result.
    If it raises, falls back to the default response and logs a warning.

    :param hook: The registered acceptance hook, or None.
    :param request: The parsed create-response request.
    :param context: The response context for this turn.
    :param model: The model name from the request.
    :returns: A queued response envelope dict.
    """
    if hook is not None:
        try:
            result = hook(request, context)
            # Ensure status is queued
            if isinstance(result, dict):
                result.setdefault("status", "queued")
            return result
        except Exception:  # pylint: disable=broad-exception-caught
            logger.warning(
                "Acceptance hook raised — falling back to default (response_id=%s)",
                context.response_id,
                exc_info=True,
            )

    return generate_default_acceptance(
        response_id=context.response_id,
        model=model,
    )

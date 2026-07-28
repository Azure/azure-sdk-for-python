# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Acceptance hook for steerable conversations.

When a new turn arrives for an already-active steerable task, the acceptance hook
generates the "queued" response returned to the HTTP caller. Developers can register
a custom hook via ``@app.response_acceptor`` to customize the queued response shape.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable, cast

from ..models._generated import ResponseObject

if TYPE_CHECKING:
    from .._response_context import ResponseContext
    from ..models._generated import CreateResponse

logger = logging.getLogger("azure.ai.agentserver.responses.acceptance")

# The acceptance hook is the developer-facing boundary, so it speaks the
# strongly-typed public model: it returns the queued ``ResponseObject``
# surfaced to the HTTP caller. The internal HTTP path works in plain dicts
# (see ``to_snapshot``), so ``dispatch_acceptance_hook`` is the single place
# that normalizes the typed result down to a dict.
AcceptanceHookFn = Callable[["CreateResponse", "ResponseContext"], "ResponseObject"]


def generate_default_acceptance(
    *,
    response_id: str,
    model: str | None = None,
) -> ResponseObject:
    """Generate the default queued response envelope.

    Used when no custom acceptance hook is registered, or as fallback
    when a custom hook raises an error.

    :keyword response_id: The response ID for the queued turn.
    :paramtype response_id: str
    :keyword model: The model name from the request.
    :paramtype model: str | None
    :returns: A queued ``ResponseObject`` (``status="queued"``).
    :rtype: ~azure.ai.agentserver.responses.models.ResponseObject
    """
    return ResponseObject(
        {
            "id": response_id,
            "object": "response",
            "status": "queued",
            "model": model,
            "output": [],
        }
    )


def _to_queued_dict(response: Any) -> dict[str, Any]:
    """Normalize a hook result to the internal queued-response dict.

    Accepts a :class:`ResponseObject` (the typed contract) and, defensively,
    a plain ``dict``. Ensures ``status`` defaults to ``"queued"``.

    :param response: The hook's return value.
    :type response: Any
    :returns: A JSON-safe queued-response dict.
    :rtype: dict[str, Any]
    """
    as_dict = getattr(response, "as_dict", None)
    if callable(as_dict):
        result = cast("dict[str, Any]", as_dict())
    elif isinstance(response, dict):
        result = dict(response)
    else:
        result = {"object": "response", "output": []}
    result.setdefault("status", "queued")
    return result


def dispatch_acceptance_hook(
    *,
    hook: AcceptanceHookFn | None,
    request: "CreateResponse",
    context: "ResponseContext",
    model: str | None = None,
) -> dict[str, Any]:
    """Call the acceptance hook or generate the default queued response.

    If a custom hook is registered and succeeds, returns its (normalized)
    result. If it raises, falls back to the default response and logs a
    warning. The return is a dict because the internal HTTP path serializes
    it directly; the developer-facing hook itself returns a typed
    :class:`ResponseObject`.

    :keyword hook: The registered acceptance hook, or None.
    :paramtype hook: AcceptanceHookFn | None
    :keyword request: The parsed create-response request.
    :paramtype request: CreateResponse
    :keyword context: The response context for this turn.
    :paramtype context: ResponseContext
    :keyword model: The model name from the request.
    :paramtype model: str | None
    :returns: A queued response envelope dict.
    :rtype: dict[str, Any]
    """
    if hook is not None:
        try:
            return _to_queued_dict(hook(request, context))
        except Exception:  # pylint: disable=broad-exception-caught
            logger.warning(
                "Acceptance hook raised — falling back to default (response_id=%s)",
                context.response_id,
                exc_info=True,
            )

    return _to_queued_dict(
        generate_default_acceptance(
            response_id=context.response_id,
            model=model,
        )
    )

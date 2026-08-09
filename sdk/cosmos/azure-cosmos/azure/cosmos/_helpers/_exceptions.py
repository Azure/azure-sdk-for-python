# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Map a non-2xx ``BackendResponse`` to the right typed Cosmos exception.

Customer code relies on the typed subclasses (``CosmosResourceExistsError``
for 409, ``CosmosResourceNotFoundError`` for 404, etc.) — for example
``try: create_item(...) except CosmosResourceExistsError:`` as an
idempotency check. This module is the single mapping site so both
backends raise the same typed class for the same status code.

It also exposes a small ``_ResponseAdapter``. When a Cosmos call fails, the
raised exception carries a ``.response`` object, and customer ``except`` blocks
read ``e.response.status_code`` / ``e.response.headers`` / ``e.response.text()``
off it. That object is normally an azure-core ``HttpResponse``, but the Rust
backend hands back a plain ``BackendResponse`` instead. ``_ResponseAdapter``
wraps that ``BackendResponse`` and re-exposes just those same attributes and
methods, so existing customer error-handling keeps working unchanged no matter
which backend produced the response.
"""
from __future__ import annotations

import json
from typing import Mapping, Optional

from .._backend.base import BackendResponse
from ..exceptions import (
    CosmosAccessConditionFailedError,
    CosmosHttpResponseError,
    CosmosResourceExistsError,
    CosmosResourceNotFoundError,
)


class _ResponseAdapter:
    """Minimal ``HttpResponse``-shaped wrapper around a ``BackendResponse``.

    Exposes only the attributes customer code is documented to read
    (``status_code``, ``headers``, ``text()``, ``body()``). Anything
    else would invite reliance on azure-core internals the Rust backend
    cannot reproduce.
    """

    def __init__(self, backend_response: BackendResponse) -> None:
        """Copy the public response fields used by Cosmos exceptions."""
        self._inner = backend_response
        self.status_code = backend_response.status_code
        self.headers = backend_response.headers if backend_response.headers is not None else {}
        # ``HttpResponseError.__init__`` reads ``response.reason``; the
        # Cosmos service rarely sends a meaningful reason phrase, so
        # use an empty string as the neutral value.
        self.reason = ""

    def text(self, encoding: Optional[str] = None) -> str:
        """Return the response body as decoded text.

        Never raises on invalid bytes / unknown encoding — falls back to
        ``errors="replace"`` so a customer's ``except`` block keeps
        running.

        :param encoding: Text encoding (defaults to UTF-8).
        :type encoding: Optional[str]
        :returns: Decoded body, or an empty string for an empty body.
        :rtype: str
        """
        if not self._inner.body:
            return ""
        try:
            return self._inner.body.decode(encoding or "utf-8")
        except UnicodeDecodeError:
            return self._inner.body.decode(encoding or "utf-8", errors="replace")
        except LookupError:
            return self._inner.body.decode("utf-8", errors="replace")

    def body(self) -> bytes:
        """Return the raw response body bytes (may be ``b""``)."""
        return self._inner.body


# Status code -> typed exception class.
_STATUS_TO_EXCEPTION = {
    409: CosmosResourceExistsError,
    404: CosmosResourceNotFoundError,
    412: CosmosAccessConditionFailedError,
}


def map_backend_response_to_exception(
    response: BackendResponse,
    *,
    message: str = "",
) -> CosmosHttpResponseError:
    """Build the typed ``CosmosHttpResponseError`` subclass for a non-2xx response.

    Returns the exception instance; the caller decides when to ``raise``
    (for example after invoking a ``response_hook``).

    :param response: The non-2xx ``BackendResponse``. The caller is
        responsible for ensuring ``status_code`` is actually >= 400.
    :type response: BackendResponse
    :param message: Server-provided error message text.
    :type message: str
    :returns: An instance of the typed subclass for the status code, or
        ``CosmosHttpResponseError`` for unmapped codes.
    :rtype: CosmosHttpResponseError
    """
    exception_class = _STATUS_TO_EXCEPTION.get(response.status_code, CosmosHttpResponseError)
    response_adapter = _ResponseAdapter(response)

    # Pass sub_status via kwargs only when set, in case the backend
    # surfaces it as a typed field without writing it into headers.
    sub_status_kwarg: dict = {}
    if response.sub_status:
        sub_status_kwarg["sub_status"] = response.sub_status

    return exception_class(
        status_code=response.status_code,
        message=message,
        response=response_adapter,
        **sub_status_kwarg,
    )


def extract_message_from_body(body: bytes) -> str:
    """Best-effort extraction of the server's error message from a JSON error body.

    Cosmos error bodies are typically
    ``{"code": "Conflict", "message": "..."}``. Returns the ``message``
    field when the body parses as a JSON object containing it; otherwise
    returns the body decoded as UTF-8 (or its ``repr`` if the bytes are
    not valid UTF-8). Never raises.

    :param body: The response body bytes.
    :type body: bytes
    :returns: A best-effort error message text.
    :rtype: str
    """
    if not body:
        return ""
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        return repr(body)

    try:
        parsed = json.loads(text)
        if isinstance(parsed, Mapping):
            message = parsed.get("message") or parsed.get("Message")
            if isinstance(message, str):
                return message
    except (ValueError, TypeError):
        pass

    return text


def is_success_status(status_code: int) -> bool:
    """Return whether ``status_code`` is in the 2xx success range (200..299)."""
    return 200 <= status_code < 300

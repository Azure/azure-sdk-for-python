# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Map a non-2xx ``BackendResponse`` to the right typed Cosmos exception.

The duplicate-id 409 is the signature error of ``create_item`` and
the entire reason ``create_item`` exists as a separate method from
``upsert_item``: customer code wraps the call in
``try / except CosmosResourceExistsError:`` as a cheap idempotency
check. If a 409 came back as a generic ``CosmosHttpResponseError``,
the ``except`` clause would no longer catch, the duplicate would
propagate as an unhandled error, and the customer's "did I already
create this order?" branch silently breaks.

This module is the one place where status codes are mapped to typed
exception classes for the helper-layer parser. Same mapping table the
legacy ``HttpResponseError`` raise sites in
``_synchronized_request._Request`` would have used; reproducing it
here lets the helper-layer parser raise the same exceptions whether
the response came back through the existing pipeline or through the
future Rust backend.

To keep customer code that reaches into the exception's ``response``
attribute (``e.response.status_code``, ``e.response.headers``,
``e.response.text()``) working with a ``BackendResponse`` (which is a
frozen dataclass, not an azure-core ``HttpResponse``), the module
also defines a tiny ``_BackendResponseShim`` that quacks like enough
of an ``HttpResponse`` to satisfy that surface.
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


class _BackendResponseShim:
    """Minimal ``HttpResponse``-shaped wrapper around a ``BackendResponse``.

    The shim exists so that customer code which reaches into
    ``except CosmosHttpResponseError as e:`` and then reads
    ``e.response.status_code`` / ``e.response.headers`` /
    ``e.response.text()`` keeps working when the response came from a
    backend that does not return a real azure-core ``HttpResponse``
    (today: never; tomorrow: the Rust backend).

    Only the three attributes/methods customer code is documented to
    use are exposed. Adding more would invite customers to depend on
    azure-core ``HttpResponse`` internals that the Rust backend has
    no way to reproduce.
    """

    def __init__(self, backend_response: BackendResponse) -> None:
        # Store the full BackendResponse so the helper can recover any
        # field if needed; the public surface stays narrow.
        self._inner = backend_response
        # Attribute names match azure-core HttpResponse so customer
        # code doing ``e.response.status_code`` works unchanged.
        self.status_code = backend_response.status_code
        self.headers = backend_response.headers if backend_response.headers is not None else {}
        # ``HttpResponseError.__init__`` reads ``response.reason`` when
        # given a response object. The Cosmos service rarely sends a
        # meaningful reason phrase (HTTP/2 dropped them entirely) and
        # the legacy SDK's exception text already carries the status
        # code and message text from the body. An empty string is the
        # right neutral value — None would be returned by
        # ``HttpResponseError`` to its formatter and surface there.
        self.reason = ""

    def text(self, encoding: Optional[str] = None) -> str:
        """Return the response body as decoded text.

        Defensive against bytes that fail to decode in the requested
        encoding: this method runs from inside a customer's
        ``except CosmosHttpResponseError`` block, so raising a
        ``UnicodeDecodeError`` here would mask the original error and
        crash the customer's exception handler. Instead, fall back to
        ``errors="replace"`` so the customer always gets a string back.

        :param encoding: Text encoding to apply. Defaults to UTF-8 to
            match what azure-core's ``HttpResponse.text()`` does for
            JSON content types.
        :type encoding: Optional[str]
        :returns: The decoded body, or an empty string when the
            backend response carried no body bytes. On invalid bytes
            for the chosen encoding, returns the body decoded with
            replacement characters rather than raising.
        :rtype: str
        """
        if not self._inner.body:
            return ""
        try:
            return self._inner.body.decode(encoding or "utf-8")
        except UnicodeDecodeError:
            # Bytes are not valid in the requested encoding. Fall back
            # to replacement characters so the customer's exception
            # handler still gets a string.
            return self._inner.body.decode(encoding or "utf-8", errors="replace")
        except LookupError:
            # Encoding name itself is unknown. Fall back to UTF-8 with
            # replacement characters so we never raise here.
            return self._inner.body.decode("utf-8", errors="replace")

    def body(self) -> bytes:
        """Return the raw response body bytes.

        :returns: The bytes the backend wrapped in the response. May be
            empty (``b""``) for 204 / no-body operations.
        :rtype: bytes
        """
        return self._inner.body


# Status code -> exception class. Ordered by frequency of appearance
# in customer code so the mapping reads top-down by the cases most
# likely to come up in a triage session.
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
    """Build the right ``CosmosHttpResponseError`` subclass for a non-2xx response.

    The function does not raise; it returns the exception instance so
    the caller can choose when to ``raise`` it (for example, after
    invoking a ``response_hook`` first).

    :param response: The non-2xx ``BackendResponse``. The function
        does not check that ``status_code`` is actually >= 400 — that
        is the caller's job. Calling this on a 2xx response is a
        programming error and produces a misleading exception.
    :type response: BackendResponse
    :param message: Server-provided error message text, typically the
        decoded ``Message`` field from a Cosmos error body. Used
        verbatim in the exception's message string.
    :type message: str
    :returns: An instance of the typed subclass for the status code
        (``CosmosResourceExistsError`` for 409, etc.) or a base
        ``CosmosHttpResponseError`` for unmapped status codes.
        ``sub_status``, ``headers``, and ``response`` are populated
        from ``response``.
    :rtype: CosmosHttpResponseError
    """
    exception_class = _STATUS_TO_EXCEPTION.get(response.status_code, CosmosHttpResponseError)

    # Wrap the BackendResponse in a shim so customer code reaching
    # ``e.response.status_code`` etc. keeps working.
    shim = _BackendResponseShim(response)

    # CosmosHttpResponseError reads the sub-status off the headers
    # itself if present; we also pass it via kwargs to handle the
    # case where the headers dict somehow does not carry it (e.g. a
    # backend that surfaces sub_status as a typed field but did not
    # write it back into the headers map).
    sub_status_kwarg: dict = {}
    if response.sub_status:
        sub_status_kwarg["sub_status"] = response.sub_status

    return exception_class(
        status_code=response.status_code,
        message=message,
        response=shim,
        **sub_status_kwarg,
    )


def extract_message_from_body(body: bytes) -> str:
    """Best-effort extraction of the server's error message from a JSON error body.

    Cosmos error responses typically have a JSON body shaped like
    ``{"code": "Conflict", "message": "Resource with specified id ..."}``.
    The legacy SDK includes the entire body or the ``message`` field
    in its exception text. This helper pulls the ``message`` field if
    the body parses as JSON and contains it; otherwise returns the
    body bytes decoded as UTF-8 (or an empty string for an empty
    body). Never raises — a malformed error body should not mask the
    underlying error.

    :param body: The response body bytes.
    :type body: bytes
    :returns: A best-effort error message text.
    :rtype: str
    """
    if not body:
        return ""
    # Decode once; both the JSON parse and the bytes-as-text fallback
    # share the resulting string. Previously we did one decode inside
    # ``json.loads(body)`` and a second ``body.decode("utf-8")`` on
    # the fallback path; folding to a single decode saves the
    # duplicated work on every server-side error.
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        # Body is not valid UTF-8 at all. Skip the JSON-parse attempt
        # (it would fail too) and return a string that at least
        # tells the caller the bytes were exotic.
        return repr(body)

    try:
        parsed = json.loads(text)
        if isinstance(parsed, Mapping):
            message = parsed.get("message") or parsed.get("Message")
            if isinstance(message, str):
                return message
    except (ValueError, TypeError):
        # Body was not valid JSON, or the parsed shape was not a
        # mapping. Fall through to returning the raw decoded text.
        pass

    return text


def is_success_status(status_code: int) -> bool:
    """Return whether ``status_code`` is in the 2xx success range.

    Centralising the check here means a future change (e.g. treating
    304 as success for ``read_item`` with an etag) is a one-line edit
    every consumer of the helper picks up.

    :param status_code: The HTTP status code from a ``BackendResponse``.
    :type status_code: int
    :returns: ``True`` for 200..299 inclusive; ``False`` otherwise.
    :rtype: bool
    """
    return 200 <= status_code < 300

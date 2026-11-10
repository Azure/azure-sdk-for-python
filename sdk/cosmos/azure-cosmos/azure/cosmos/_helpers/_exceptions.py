# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Map error ``BackendResponse`` records to typed Cosmos exceptions.

The customer app relies on the typed subclasses (``CosmosResourceExistsError``
for 409, ``CosmosResourceNotFoundError`` for 404, etc.) — for example
``try: create_item(...) except CosmosResourceExistsError:`` as a
conflict check. Sync and async Python backends share this mapping;
the legacy path has its own response processing.

It also exposes a small ``_ResponseAdapter``. When a Cosmos call fails, the
raised exception carries a ``.response`` object, and customer ``except`` blocks
read ``e.response.status_code`` / ``e.response.headers`` / ``e.response.text()``
off it. That object is normally an azure-core ``HttpResponse``, but
BindingAdapter hands back a ``BackendResponse`` instead. ``_ResponseAdapter``
wraps that ``BackendResponse`` and re-exposes just those same attributes and
methods for Cosmos exception construction and common error handlers. It is not
a complete ``HttpResponse`` implementation or a guarantee of execution-path parity.
"""
from __future__ import annotations

from typing import Any, Mapping, Optional

from azure.core.exceptions import ODataV4Format

from .._backend.contracts import BackendResponse
from .._response_decoding import decode_response_body_for_status
from ..exceptions import (
    CosmosAccessConditionFailedError,
    CosmosHttpResponseError,
    CosmosResourceExistsError,
    CosmosResourceNotFoundError,
)


class _ResponseAdapter:
    """Minimal ``HttpResponse``-shaped wrapper around a ``BackendResponse``.

    Provides ``status_code``, ``headers``, ``reason``, ``text()``, and ``body()``.
    It retains the response and header mapping rather than making a snapshot.
    """

    def __init__(self, backend_response: BackendResponse) -> None:
        """Expose response fields used by Cosmos exception construction."""
        self._inner = backend_response
        self.status_code = backend_response.status_code
        self.headers = backend_response.headers if backend_response.headers is not None else {}
        # ``HttpResponseError.__init__`` reads ``response.reason``; the
        # Cosmos service rarely sends a meaningful reason phrase, so
        # use an empty string as the neutral value.
        self.reason = ""

    def text(self, encoding: Optional[str] = None) -> str:
        """Return the response body as decoded text.

        Replace undecodable bytes; fall back to UTF-8 replacement decoding
        when the requested encoding cannot be found.

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


class _RequestEntityTooLargeFormat(ODataV4Format):
    """Restore the 413 error code for native Errors envelopes without altering the response.

    :param json_object: Decoded error body.
    :type json_object: Mapping[str, Any]
    """

    def __init__(self, json_object: Mapping[str, Any]) -> None:
        if (
            isinstance(json_object, Mapping)
            and "error" not in json_object
            and not json_object.get("code")
        ):
            errors = json_object.get("Errors")
            if (
                isinstance(errors, list)
                and errors
                and all(isinstance(error, str) for error in errors)
            ):
                json_object = {
                    **json_object,
                    "code": "RequestEntityTooLarge",
                    "message": json_object.get("message") or "\n".join(errors),
                }
        super().__init__(json_object)


def map_backend_response_to_exception(
    response: BackendResponse,
    *,
    message: str = "",
) -> CosmosHttpResponseError:
    """Build the typed ``CosmosHttpResponseError`` subclass for an error response.

    Returns the exception instance; the caller decides when to ``raise``
    it. Native 413 ``Errors`` envelopes retain the ``RequestEntityTooLarge``
    code in the formatted exception without rewriting its raw response or
    overriding an explicit service code. This function does not invoke a response hook.

    :param response: The ``BackendResponse`` the caller has classified as an error.
    :type response: BackendResponse
    :keyword str message: Server-provided error message text.
    :returns: An instance of the typed subclass for the status code, or
        ``CosmosHttpResponseError`` for unmapped codes.
    :rtype: CosmosHttpResponseError
    """
    exception_class = _STATUS_TO_EXCEPTION.get(
        response.status_code, CosmosHttpResponseError
    )
    response_adapter = _ResponseAdapter(response)

    # Pass sub_status via kwargs only when set, in case the backend
    # surfaces it as a typed field without writing it into headers.
    exception_kwargs: dict = {}
    if response.sub_status:
        exception_kwargs["sub_status"] = response.sub_status
    if response.status_code == 413:
        exception_kwargs["error_format"] = _RequestEntityTooLargeFormat

    return exception_class(
        status_code=response.status_code,
        message=message,
        response=response_adapter,
        **exception_kwargs,
    )


def error_message_from_body(body: bytes, status_code: int) -> str:
    """Return the error body text used as ``http_error_message``.

    Matches the legacy path, which passes the whole decoded error body (for
    example ``{"code":"NotFound","message":"..."}``) rather than only its
    ``message`` field, so ``json.loads(e.http_error_message)`` keeps working.
    Invalid UTF-8 in an error body is decoded with replacement characters.

    :param body: The response body bytes.
    :type body: bytes
    :param int status_code: The HTTP status code of the error response.
    :returns: The decoded error body, or an empty string for an empty body.
    :rtype: str
    """
    if not body:
        return ""
    return decode_response_body_for_status(body, status_code)


def is_success_status(status_code: int) -> bool:
    """Return whether ``status_code`` is in the 2xx success range (200..299)."""
    return 200 <= status_code < 300

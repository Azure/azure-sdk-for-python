# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""UTF-8 decoding for HTTP response bodies, with an opt-in fallback for
payloads containing bytes that are not valid UTF-8.

By default this module preserves the historical SDK behavior: strict
decode, ``UnicodeDecodeError`` raised on the first invalid byte.
Operators who need to read past corrupt payloads (for example, to
unblock a stuck change-feed processor) can opt in to a permissive
fallback by setting an environment variable.

The recognized environment variable is
``AZURE_COSMOS_CHARSET_DECODER_ERROR_ACTION_ON_MALFORMED_INPUT``:

* ``REPLACE`` -> Python ``errors="replace"`` (substitute U+FFFD)
* ``IGNORE``  -> Python ``errors="ignore"`` (drop the bad bytes)
* anything else, including unset -> strict (raise on bad bytes)

The env var is consulted only on the decode-failure path, so operators
can set or change it at any point during process lifetime and the next
malformed payload will pick up the new value. This follows the Cosmos
SDK's runtime-read pattern for environment-based controls.
"""
import logging
import os
from typing import Optional

from ._constants import _Constants


_MALFORMED_INPUT_ENV_VAR = _Constants.CHARSET_DECODER_ERROR_ACTION_ON_MALFORMED_INPUT

# Mapping from the recognized env var values to Python's bytes.decode
# `errors=` argument. Anything not in this mapping (including the env var
# being unset) resolves to strict decoding, which is the historical default.
_ENV_VALUE_TO_DECODE_ERRORS_MODE = {
    "REPLACE": "replace",
    "IGNORE": "ignore",
}

_logger = logging.getLogger(__name__)


def _resolve_fallback_mode_from_env() -> Optional[str]:
    """Reads the malformed-input env var and returns the Python decode
    ``errors=`` mode to use as a fallback, or ``None`` if the operator
    has not opted in (in which case strict decoding stays in effect)."""
    raw_value = os.environ.get(_MALFORMED_INPUT_ENV_VAR)
    if raw_value is None:
        return None
    return _ENV_VALUE_TO_DECODE_ERRORS_MODE.get(raw_value.strip().upper())



def decode_response_body(data: bytes, operation_context: Optional[str] = None) -> str:
    """Decode an HTTP response body as UTF-8.

    The healthy path is strict decoding, identical in behavior and cost
    to ``data.decode("utf-8")``. The slow path is taken only when the
    payload contains bytes that are not valid UTF-8:

    * If the operator has opted in via the malformed-input env var, the
      decode is retried in the configured permissive mode (``replace`` or
      ``ignore``) and a WARNING is logged with the byte offset, the
      decoder's reason, and the supplied operation context.
    * Otherwise a ``UnicodeDecodeError`` is raised whose ``reason`` field
      carries an actionable hint pointing the operator at the env var.
      The original exception is preserved as ``__cause__``.

    :param data: Response body bytes.
    :type data: bytes
    :param operation_context: Optional short string identifying the call
        site (for example, ``"read_item"`` or ``"query_items page"``);
        included in the WARNING log line when permissive fallback fires.
    :type operation_context: Optional[str]
    :returns: The decoded string.
    :rtype: str
    :raises UnicodeDecodeError: If the body contains invalid UTF-8 and
        the operator has not opted in to a permissive fallback.
    """
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as strict_error:
        fallback_mode = _resolve_fallback_mode_from_env()
        if fallback_mode is None:
            hint = (
                "{original}; set environment variable "
                "{env_var}=REPLACE (or IGNORE) to tolerate invalid UTF-8 "
                "in Cosmos response bodies"
            ).format(
                original=strict_error.reason,
                env_var=_MALFORMED_INPUT_ENV_VAR,
            )
            raise UnicodeDecodeError(
                strict_error.encoding,
                strict_error.object,
                strict_error.start,
                strict_error.end,
                hint,
            ) from strict_error

        _logger.warning(
            "Cosmos response body contained invalid UTF-8 at byte offset %d "
            "(reason: %s); decoding with errors=%r per %s (operation: %s).",
            strict_error.start,
            strict_error.reason,
            fallback_mode,
            _MALFORMED_INPUT_ENV_VAR,
            operation_context or "-",
        )
        return data.decode("utf-8", errors=fallback_mode)


def decode_response_body_for_status(
    data: bytes,
    status_code: int,
    operation_context: Optional[str] = None,
) -> str:
    """Decode an HTTP response body, with a best-effort fallback for HTTP
    error responses whose body happens to contain invalid UTF-8.

    Behaves exactly like :func:`decode_response_body` on success and on
    2xx responses with malformed UTF-8. The difference is the error path:
    if strict decoding fails AND the response is an HTTP error
    (``status_code >= 400``), the body is decoded with ``errors="replace"``
    so the caller can still construct the real status-code exception
    (``CosmosResourceNotFoundError``, ``CosmosHttpResponseError``, etc.).

    The reason: the SDK's retry/refresh logic and customer error handlers
    branch on status code, not on message contents. Masking a 404, 410
    (partition split), 429 (throttle), or 503 with a ``UnicodeDecodeError``
    breaks recovery paths that would otherwise have worked. ``U+FFFD`` in
    an error message is acceptable; a wrong exception class is not.

    For 2xx responses with malformed UTF-8 the exception is still raised —
    a successful response carrying corrupt bytes is a real data-integrity
    problem the caller needs to see.

    :param data: Response body bytes.
    :type data: bytes
    :param status_code: The HTTP status code of the response.
    :type status_code: int
    :param operation_context: Optional short string identifying the call
        site; forwarded to :func:`decode_response_body`.
    :type operation_context: Optional[str]
    :returns: The decoded string.
    :rtype: str
    :raises UnicodeDecodeError: If the body contains invalid UTF-8, the
        operator has not opted in to a permissive fallback, and the
        response is a success (2xx/3xx) rather than an HTTP error.
    """
    try:
        return decode_response_body(data, operation_context)
    except UnicodeDecodeError:
        if status_code >= 400:
            return data.decode("utf-8", errors="replace")
        raise

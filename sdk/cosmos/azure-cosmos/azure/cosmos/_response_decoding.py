# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""UTF-8 decoding for HTTP response bodies, with an opt-in fallback for
payloads containing bytes that are not valid UTF-8.

By default this module preserves the historical SDK behavior: strict
decode, ``UnicodeDecodeError`` raised on the first invalid byte.
Operators who need to read past corrupt payloads (for example, to
unblock a stuck change-feed processor) can opt in to a permissive
fallback by setting an environment variable at process start.

The recognized environment variable is
``AZURE_COSMOS_CHARSET_DECODER_ERROR_ACTION_ON_MALFORMED_INPUT``:

* ``REPLACE`` -> Python ``errors="replace"`` (substitute U+FFFD)
* ``IGNORE``  -> Python ``errors="ignore"`` (drop the bad bytes)
* anything else, including unset -> strict (raise on bad bytes)

The value is read once at module import. Tests can call
``_reset_for_tests()`` to re-snapshot.
"""
import logging
import os
from typing import Optional

from ._constants import _Constants

__all__ = ["decode_response_body", "_reset_for_tests"]

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


# Snapshot at module import. The value is immutable after import unless
# `_reset_for_tests` is called. Reading a module-level string in CPython is
# atomic, so no lock is needed on the per-call read path.
_fallback_errors_mode: Optional[str] = _resolve_fallback_mode_from_env()


def _reset_for_tests() -> None:
    """Re-reads the env var and refreshes the cached fallback mode. Tests
    should call this after mutating ``os.environ`` so the next call to
    ``decode_response_body`` sees the new value."""
    global _fallback_errors_mode  # pylint: disable=global-statement
    _fallback_errors_mode = _resolve_fallback_mode_from_env()


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
    :param operation_context: Optional short string identifying the call
        site (for example, ``"read_item"`` or ``"query_items page"``);
        included in the WARNING log line when permissive fallback fires.
    :returns: The decoded string.
    :raises UnicodeDecodeError: If the body contains invalid UTF-8 and
        the operator has not opted in to a permissive fallback.
    """
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as strict_error:
        fallback_mode = _fallback_errors_mode
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
            "(reason: %s); decoding with errors=%r per %s%s.",
            strict_error.start,
            strict_error.reason,
            fallback_mode,
            _MALFORMED_INPUT_ENV_VAR,
            " (operation: {0})".format(operation_context) if operation_context else "",
        )
        return data.decode("utf-8", errors=fallback_mode)


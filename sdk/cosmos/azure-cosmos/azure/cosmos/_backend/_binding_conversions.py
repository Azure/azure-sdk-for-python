# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Conversions between the Rust binding's plain values and our typed objects.

The binding speaks in tuples and plain dicts. These helpers convert in both
directions -- arguments on the way in, responses on the way out -- so the shape
of each binding call is written once and the sync and async backends cannot
drift apart on it.
"""
from __future__ import annotations

from typing import Any, Mapping, Optional
from dataclasses import replace

from azure.core.utils import CaseInsensitiveDict

from .contracts import BackendResponse, ContainerMetadata, PreparedClientConfig
from .errors import BackendProtocolError
from ..exceptions import CosmosHttpResponseError


def build_container_metadata(raw: Any) -> ContainerMetadata:
    """Validate the native metadata contract once, without JSON or response state."""
    if not isinstance(raw, tuple) or len(raw) != 4:
        raise BackendProtocolError("The binding returned invalid container metadata")
    rid, paths, kind, system_key = raw
    if not isinstance(rid, str) or not rid:
        raise BackendProtocolError("Container metadata requires a non-empty rid")
    if not isinstance(paths, tuple) or any(not isinstance(path, str) or not path for path in paths):
        raise BackendProtocolError("Container metadata requires a tuple of non-empty paths")
    if kind not in (None, "Hash", "MultiHash", "Range") or bool(paths) != (kind is not None):
        raise BackendProtocolError("Container metadata contains an invalid partition-key definition")
    if system_key is not None and not isinstance(system_key, bool):
        raise BackendProtocolError("Container metadata system_key must be bool or None")
    return ContainerMetadata(rid, paths, kind, system_key)


def metadata_exception_from_binding(error: BaseException) -> CosmosHttpResponseError:
    """Convert an actual metadata failure without publishing response headers."""
    from .._helpers._exceptions import extract_message_from_body, map_backend_response_to_exception
    from .._helpers._response_parse import apply_response_diagnostics, apply_request_charge_format

    if len(error.args) != 1 or not isinstance(error.args[0], tuple) or len(error.args[0]) != 5:
        raise BackendProtocolError("The binding returned an invalid metadata error")
    response = build_backend_response(*error.args[0])
    if response.status_code < 400:
        raise BackendProtocolError("The binding returned a non-error metadata failure")
    headers = CaseInsensitiveDict(response.headers or {})
    apply_request_charge_format(headers)
    apply_response_diagnostics(headers, response.diagnostics)
    response = replace(response, headers=headers)
    return map_backend_response_to_exception(response, message=extract_message_from_body(response.body))


# ---------------------------------------------------------------------------
# Response-header normalisation (binding dict -> CaseInsensitiveDict)
# ---------------------------------------------------------------------------
#
# The binding returns a plain dict keyed by the gateway's wire
# header names. The legacy core-python path returns azure-core's
# ``CaseInsensitiveDict`` (it just does ``copy.copy(response.headers)`` --
# the raw gateway headers, no renaming or aliasing). To keep
# ``last_response_headers`` lookups case-insensitive and identical across
# both backends, we wrap the binding's dict in the same type. No keys are
# added or renamed: both backends surface exactly the header names the
# gateway emitted (e.g. ``x-ms-cosmos-llsn``, ``x-ms-item-lsn``, ``lsn``).


def normalize_response_headers(
    headers: Optional[Mapping[str, Any]],
) -> Optional[CaseInsensitiveDict]:
    """Wrap the binding's response-header dict in a ``CaseInsensitiveDict``.

    A pure type-normalisation step: every key from the input is copied
    through unchanged so the rust path returns the same gateway header
    names the legacy path does. ``None`` or empty input returns ``None``.
    """
    if not headers:
        return None
    result = CaseInsensitiveDict()
    for raw_key, value in headers.items():
        result[raw_key] = value
    return result


def acquire_driver_handle_args(
    endpoint: str,
    master_key: Optional[str],
    client_config: Optional[PreparedClientConfig],
    token_credential: Optional[Any],
) -> tuple[Any, ...]:
    """Build the positional args for the Rust ``acquire_driver_handle`` call.

    A token credential rides as the 4th argument; master-key auth uses the
    3-argument form. ``credentials.resolve_credential`` is contracted to set
    exactly one of the two. Shared by both backends so the call shape lives in
    one place.

    The exactly-one invariant is enforced here rather than assumed: if both are
    somehow set, the silent default would pick the token and drop the master
    key with no signal, so instead we raise -- a contract violation upstream is
    a bug, not something to paper over.
    """
    if master_key is not None and token_credential is not None:
        raise ValueError(
            "acquire_driver_handle_args received both master_key and token_credential; "
            "exactly one must be set (credentials.resolve_credential is "
            "responsible for this)."
        )
    if token_credential is not None:
        return (endpoint, None, client_config, token_credential)
    return (endpoint, master_key, client_config)


def build_backend_response(
    status_code: Any,
    sub_status: Any,
    headers: Optional[Mapping[str, Any]],
    body: Any,
    diagnostics: Any = None,
) -> BackendResponse:
    """Wrap the binding's response tuple as a ``BackendResponse``.

    The binding currently returns ``(status, sub_status, headers, body)`` plus
    an optional fifth diagnostics payload. The diagnostics element is optional
    so older test doubles (or older bindings) that still return a 4-tuple keep
    working unchanged.
    """
    return BackendResponse(
        status_code=int(status_code),
        sub_status=int(sub_status),
        headers=normalize_response_headers(headers),
        body=bytes(body) if body else b"",
        diagnostics=diagnostics,
    )

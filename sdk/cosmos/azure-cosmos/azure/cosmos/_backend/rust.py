# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Sync backend that sends operations to the rust driver through the compiled binding.

Terms, consistent across the backend layer: the **binding** is the compiled
``azure.cosmos._rust`` extension Python calls into; the **rust driver** is the
engine the binding builds (it owns the connection pool, request signing, and
region routing); the **driver handle** is the string ``init_client`` returns -- a
key made from ``(endpoint, credential, config)`` that names *which* rust driver a
client uses. The compiled ``_rust`` file contains both the binding and the rust
driver code.

This is one of only two modules allowed to import ``azure.cosmos._rust``
(a unit test enforces that). The binding is not present until it
has been built, so the import is guarded; until then, operations raise
``NotImplementedError`` pointing at the build step.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Iterator, Optional

from azure.core.exceptions import ServiceResponseError

from .base import (
    OP_TO_BINDING_METHOD,
    PageNotSupportedByBackendError,
    QUERY_TO_BINDING_METHOD,
    BackendResponse,
    CosmosBackend,
    PreparedClientConfig,
    PreparedQuery,
    PreparedRequest,
    QueryNotSupportedByBackendError,
    QueryPage,
    build_backend_response,
)
from ._shared import (
    RustBackendShared,
    configure_packaged_query_plan_interop,
    driver_transport_error_type,
    driver_unsupported_query_error_type,
)
from .constants import BACKEND_NAME_RUST

_LOGGER = logging.getLogger(__name__)

# Imported once when this module loads; not changed afterwards.
_rust_module: Optional[Any] = None
try:
    from azure.cosmos import _rust  # type: ignore[attr-defined]
    _rust_module = _rust
    configure_packaged_query_plan_interop(_rust_module)
except ImportError:
    _LOGGER.debug(
        "_rust module not available; RustBackend operations "
        "will raise NotImplementedError until the Rust module is built."
    )

# The binding's response-less transport error, captured once at load. A driver
# op that fails before any wire response raises this; we re-raise it as
# azure-core's ServiceResponseError (see driver_transport_error_type).
_DRIVER_TRANSPORT_ERROR = driver_transport_error_type(_rust_module)
_UNSUPPORTED_QUERY_ERROR = driver_unsupported_query_error_type(_rust_module)


# Look up the binding's function for an operation. Read live from ``_rust_module``
# rather than cached at import, so the tests can swap in a fake binding; the extra
# getattr per call is tiny next to the network round trip.
def _resolve_dispatch(op: str) -> Optional[Any]:
    """Return the binding's ``<op>`` function, or ``None`` if the op is unsupported
    or the compiled module is absent."""
    method = OP_TO_BINDING_METHOD.get(op)
    if method is None or _rust_module is None:
        return None
    return getattr(_rust_module, method, None)


def _resolve_page_dispatch(op: str) -> Optional[Any]:
    """Return the binding function for a paged operation."""
    method = QUERY_TO_BINDING_METHOD.get(op)
    if method is None or _rust_module is None:
        return None
    return getattr(_rust_module, method, None)


def _binding_request_from_page(prepared: PreparedQuery) -> PreparedRequest:
    """Adapt the page contract to the binding's current request object.

    ``query_items`` carries its SQL and parameters as a JSON body;
    ``read_all_items`` and ``list_databases`` are parameterless feeds and send
    none. The typed paging fields become the ``x-ms-continuation`` /
    ``x-ms-max-item-count`` headers the binding forwards to the driver.
    """
    if prepared.op in ("read_all_items", "list_databases"):
        body = b""
    else:
        if prepared.query is None:
            raise ValueError("query_items requires PreparedQuery.query.")
        payload: dict[str, Any] = {"query": prepared.query}
        if prepared.parameters:
            payload["parameters"] = list(prepared.parameters)
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    headers = dict(prepared.headers)
    if prepared.continuation is not None:
        headers["x-ms-continuation"] = prepared.continuation
    if prepared.max_item_count is not None:
        headers["x-ms-max-item-count"] = str(prepared.max_item_count)
    return PreparedRequest(
        op=prepared.op,
        container_link=prepared.container_link,
        body_bytes=body,
        partition_key_header=prepared.partition_key_header or "",
        headers=headers,
    )


class RustBackend(RustBackendShared, CosmosBackend):
    """Sends operations from one ``CosmosClient`` to a shared rust driver.

    The **driver handle** ``init_client`` returns is built on the first operation
    and reused; every operation passes it back. The handle is not the
    ``CosmosClient`` and not the rust driver itself -- it is the driver's key,
    made from ``(endpoint, credential, config)``. The binding keeps one rust driver
    per distinct ``(endpoint, credential, config)`` and reference-counts it, so
    several clients with the same settings share a single rust driver; ``close``
    drops this client's reference and only the last one shuts the driver down.
    Operations route by kind; when the compiled binding is missing, every
    operation raises ``NotImplementedError``.

    Per-client state, guard registration, and teardown live in
    :class:`~azure.cosmos._backend._shared.RustBackendShared`; this class adds only
    the synchronous (blocking) handle build and dispatch.
    """

    name = BACKEND_NAME_RUST

    def __init__(
        self,
        endpoint: str,
        master_key: Optional[str] = None,
        client_config: Optional[PreparedClientConfig] = None,
        token_credential: Optional[Any] = None,
        strict_isolation: bool = False,
    ) -> None:
        # The sync backend has no fields beyond the shared ones, so initialize shared
        # state directly. This also registers against the endpoint and, in strict
        # isolation mode, may raise StrictEngineIsolationError for a config conflict.
        self._init_shared(
            endpoint, master_key, client_config, token_credential, strict_isolation
        )

    def _ensure_handle(self) -> str:
        """Return this client's driver handle, building it once on first use.

        On the first operation the binding's ``init_client`` either builds a new
        rust driver for this ``(endpoint, credential, config)`` or, if one already
        exists, bumps its reference count and returns the same handle. Without this,
        every operation would re-init (churning rust drivers) or two threads racing
        the first call would each build one. A fast no-lock check for the
        already-built case, plus a lock with a second check inside, makes the
        build/ask happen exactly once. Raises ``NotImplementedError`` when the
        compiled binding is absent.
        """
        # If the handle is already built, return it without locking.
        handle = self._handle
        if handle is not None:
            return handle
        if _rust_module is None:
            raise NotImplementedError(
                "RustBackend: the compiled azure.cosmos._rust "
                "module is not present in this environment. Build it with "
                "`maturin develop` from the repo root."
            )
        # Build it once. The lock, with a second check inside, keeps
        # concurrent first callers from each building one.
        with self._handle_lock:
            if self._handle is None:
                self._handle = _rust_module.init_client(*self._init_client_args())
            return self._handle

    def close(self) -> None:
        """Drop this client's reference to the shared rust driver.

        Releases the guard registration once, stops the credential bridge, clears
        the handle, and tells the binding to ``close_client(handle)`` -- which drops
        this client's reference; the rust driver is only torn down when the last
        client sharing it closes. Without this the guard count leaks, the bridge
        thread keeps running, and the rust driver's connection pool is never
        released.
        """
        self._release_config_once()
        self._close_token_credential_bridge()
        with self._handle_lock:
            handle = self._handle
            self._handle = None
        if handle is None or _rust_module is None:
            return
        close_client = getattr(_rust_module, "close_client", None)
        if close_client is None:
            return
        try:
            close_client(handle)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.debug("RustBackend.close failed for handle=%s", handle, exc_info=True)

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:  # pylint: disable=broad-except
            # Never raise from object finalization.
            pass

    def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        """Send one prepared single-response operation."""
        if prepared is None:
            return None
        if _rust_module is None:
            raise NotImplementedError(
                "RustBackend.execute: the compiled "
                "azure.cosmos._rust module is not present in "
                "this environment. Build it with `maturin develop` from "
                "the repo root."
            )

        handle = self._ensure_handle()
        # Look up the binding's function for this op; None if unsupported.
        dispatch = _resolve_dispatch(prepared.op)
        if dispatch is None:
            raise NotImplementedError(
                "RustBackend.execute does not yet support op={!r}.".format(prepared.op)
            )
        # Log which backend and op ran, so a migration can confirm from logs that
        # traffic stays on the Rust path. The handle is omitted (it carries a
        # credential hash).
        _LOGGER.debug(
            "cosmos backend=%s op=%s dispatch=%s",
            BACKEND_NAME_RUST,
            prepared.op,
            OP_TO_BINDING_METHOD.get(prepared.op),
        )
        # A response-less driver failure (transport error, client-side
        # validation, pre-HTTP timeout) is raised as the binding's
        # DriverTransportError; translate it to azure-core's ServiceResponseError
        # so customer handlers and transport-retry policies match the legacy path.
        try:
            raw_response = dispatch(handle, prepared)
        except _DRIVER_TRANSPORT_ERROR as exc:
            raise ServiceResponseError(message=str(exc)) from exc
        return build_backend_response(*raw_response)

    def resolve_container_metadata(self, container_link: str) -> Optional[BackendResponse]:
        """Resolve and cache container metadata through the rust driver."""
        if _rust_module is None:
            raise NotImplementedError(
                "RustBackend.resolve_container_metadata: the compiled "
                "azure.cosmos._rust module is not present in this environment."
            )
        dispatch = getattr(_rust_module, "resolve_container_metadata", None)
        if dispatch is None:
            return None
        handle = self._ensure_handle()
        try:
            raw_response = dispatch(handle, container_link)
        except _DRIVER_TRANSPORT_ERROR as exc:
            raise ServiceResponseError(message=str(exc)) from exc
        return build_backend_response(*raw_response)

    def execute_pages(self, prepared: PreparedQuery) -> Iterator[QueryPage]:
        """Yield the one page returned by a ``query_items`` / ``read_all_items``
        / ``list_databases`` binding call."""
        if _rust_module is None:
            raise PageNotSupportedByBackendError(
                "RustBackend.execute_pages: the compiled azure.cosmos._rust "
                "module is not present in this environment. Build it with "
                "`maturin develop` from the repo root."
            )
        dispatch = _resolve_page_dispatch(prepared.op)
        if dispatch is None:
            raise PageNotSupportedByBackendError(
                "RustBackend.execute_pages does not yet support op={!r}.".format(prepared.op)
            )
        handle = self._ensure_handle()
        binding_request = _binding_request_from_page(prepared)
        _LOGGER.debug(
            "cosmos backend=%s op=%s dispatch=%s",
            BACKEND_NAME_RUST,
            prepared.op,
            QUERY_TO_BINDING_METHOD.get(prepared.op),
        )
        try:
            response = build_backend_response(*dispatch(handle, binding_request))
        except _UNSUPPORTED_QUERY_ERROR as exc:
            raise QueryNotSupportedByBackendError(str(exc)) from exc
        except _DRIVER_TRANSPORT_ERROR as exc:
            raise ServiceResponseError(message=str(exc)) from exc
        continuation = response.headers.get("x-ms-continuation") if response.headers else None
        yield QueryPage(
            status_code=response.status_code,
            continuation=continuation,
            sub_status=response.sub_status,
            headers=response.headers,
            body=response.body,
            diagnostics=response.diagnostics,
        )

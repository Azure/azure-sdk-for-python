# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Public item keyword merging and legacy-only request-option adapters.

The merge_* utilities belong to the Python wrapper and serve both execution
paths. For example, response_hook=callback is copied into the working kwargs;
the public method decides when to call it.

The build_*_request_options functions prepare options for the legacy path.
Rust-path item helpers instead use _request_settings.compose_item_options.
The retained get_selected_backend accessor retrieves an existing Python
backend; it does not select one. Nothing here calls a binding function or
performs network I/O.
"""
from __future__ import annotations

import warnings
from typing import Any, Dict, Optional

from .._availability_strategy_config import _validate_request_hedging_strategy
from .._constants import _Constants as Constants


def _merge_explicit_item_kwargs(kwargs: Dict[str, Any], **values: Any) -> None:
    """Copy non-None options in caller order, validating hedging before assignment.

    ``values`` contains explicit options; None values are skipped and hedging is validated.

    :param kwargs: Working options updated in place.
    :type kwargs: Dict[str, Any]
    :return: None.
    :rtype: None
    """
    for name, value in values.items():
        if value is None:
            continue
        if name == "availability_strategy":
            value = _validate_request_hedging_strategy(value)
        key = Constants.Kwargs.RETRY_WRITE if name == "retry_write" else name
        kwargs[key] = value


def merge_create_item_explicit_kwargs(
    kwargs: Dict[str, Any],
    *,
    pre_trigger_include: Any = None,
    post_trigger_include: Any = None,
    session_token: Any = None,
    initial_headers: Any = None,
    priority: Any = None,
    no_response: Any = None,
    retry_write: Any = None,
    throughput_bucket: Any = None,
    availability_strategy: Any = None,
    response_hook: Any = None,
) -> None:
    """Copy every non-None explicit ``create_item`` kwarg into ``kwargs``.

    Folds the ``if X is not None: kwargs['X'] = X`` boilerplate that both
    ``Container.create_item`` methods would otherwise repeat inline. Public
    create response hooks run after the item helper returns, rather than being
    forwarded into request execution.
    ``availability_strategy`` is passed through the hedging-strategy
    validator.

    :param dict[str, Any] kwargs: Working call keywords updated in place.
    :keyword Any pre_trigger_include: Pre-trigger option copied when not None.
    :keyword Any post_trigger_include: Post-trigger option copied when not None.
    :keyword Any session_token: Session token copied when not None.
    :keyword Any initial_headers: Caller header overrides copied when not None.
    :keyword Any priority: Request priority copied when not None.
    :keyword Any no_response: Write-response suppression option copied when not None.
    :keyword Any retry_write: Write retry override copied under its internal option name.
    :keyword Any throughput_bucket: Throughput bucket copied when not None.
    :keyword Any availability_strategy: Hedging strategy validated before copying.
    :keyword Any response_hook: Response callback retained for the public creation method.
    :return: None.
    :rtype: None
    """
    _merge_explicit_item_kwargs(
        kwargs,
        pre_trigger_include=pre_trigger_include,
        post_trigger_include=post_trigger_include,
        session_token=session_token,
        initial_headers=initial_headers,
        priority=priority,
        no_response=no_response,
        retry_write=retry_write,
        throughput_bucket=throughput_bucket,
        availability_strategy=availability_strategy,
        response_hook=response_hook,
    )


def get_selected_backend(client_connection: Any) -> Any:
    """Retrieve the already-selected Python backend from the client connection.

    Unmigrated connection-owned coordinators use this accessor. Public point
    operations instead receive their backend directly through CosmosClientContext.
    This function does not select or construct a backend.

    Read ``_backend`` from the connection's ``__dict__`` (its stored instance
    attributes) when available; otherwise use attribute lookup.

    :param client_connection: The connection that owns the ``_backend``
        attribute containing the selected Python backend.
    :type client_connection: Any
    :returns: The stored Python backend object.
    :rtype: Any
    :raises RuntimeError: If ``_backend`` is missing or ``None``.
    """
    connection_dict = getattr(client_connection, "__dict__", None)
    if isinstance(connection_dict, dict):
        backend = connection_dict.get("_backend")
    else:
        backend = getattr(client_connection, "_backend", None)
    if backend is None:
        raise RuntimeError("client_connection does not contain a concrete Cosmos backend")
    return backend


def build_create_item_request_options(
    kwargs: Dict[str, Any],
    *,
    enable_automatic_id_generation: bool,
    indexing_directive: Optional[int],
    populate_query_metrics: Optional[bool] = None,
) -> Dict[str, Any]:
    """Build the request-options dict the legacy ``CreateItem`` consumes.

    Pure compatibility function. Public create methods reject query metrics
    before reaching this adapter; its metrics argument is retained only for
    direct internal compatibility callers.

    :param kwargs: Per-call kwargs forwarded to ``build_options``;
        not mutated by this function.
    :type kwargs: Dict[str, Any]
    :keyword enable_automatic_id_generation: Negated into
        ``options["disableAutomaticIdGeneration"]``.
    :type enable_automatic_id_generation: bool
    :keyword indexing_directive: Written to ``options["indexingDirective"]``
        when supplied.
    :type indexing_directive: Optional[int]
    :keyword populate_query_metrics: When truthy, emits the deprecation
        warning and writes ``options["populateQueryMetrics"]``.
    :type populate_query_metrics: Optional[bool]
    :returns: The request-options dict.
    :rtype: Dict[str, Any]
    """
    from .._base import build_options
    request_options = build_options(kwargs)
    request_options["disableAutomaticIdGeneration"] = not enable_automatic_id_generation
    if populate_query_metrics:
        warnings.warn(
            "the populate_query_metrics flag does not apply to this method "
            "and will be removed in the future",
            DeprecationWarning,
        )
        request_options["populateQueryMetrics"] = populate_query_metrics
    if indexing_directive is not None:
        request_options["indexingDirective"] = indexing_directive
    return request_options


def merge_delete_item_explicit_kwargs(
    kwargs: Dict[str, Any],
    *,
    pre_trigger_include: Any = None,
    post_trigger_include: Any = None,
    session_token: Any = None,
    initial_headers: Any = None,
    etag: Any = None,
    match_condition: Any = None,
    priority: Any = None,
    retry_write: Any = None,
    throughput_bucket: Any = None,
    availability_strategy: Any = None,
    response_hook: Any = None,
) -> None:
    """Copy every non-None explicit ``delete_item`` kwarg into ``kwargs``.

    Same shape as ``merge_create_item_explicit_kwargs``. Adds ``etag``
    and ``match_condition`` (meaningful on delete) and omits
    ``no_response`` (delete has no body). ``availability_strategy`` is
    passed through the hedging-strategy validator.

    :param dict[str, Any] kwargs: Working call keywords updated in place.
    :keyword Any pre_trigger_include: Pre-trigger option copied when not None.
    :keyword Any post_trigger_include: Post-trigger option copied when not None.
    :keyword Any session_token: Session token copied when not None.
    :keyword Any initial_headers: Caller header overrides copied when not None.
    :keyword Any etag: ETag copied for conditional request preparation.
    :keyword Any match_condition: Match condition copied for conditional request preparation.
    :keyword Any priority: Request priority copied when not None.
    :keyword Any retry_write: Write retry override copied under its internal option name.
    :keyword Any throughput_bucket: Throughput bucket copied when not None.
    :keyword Any availability_strategy: Hedging strategy validated before copying.
    :keyword Any response_hook: Response callback copied when not None.
    :return: None.
    :rtype: None
    """
    _merge_explicit_item_kwargs(
        kwargs,
        pre_trigger_include=pre_trigger_include,
        post_trigger_include=post_trigger_include,
        session_token=session_token,
        initial_headers=initial_headers,
        etag=etag,
        match_condition=match_condition,
        priority=priority,
        retry_write=retry_write,
        throughput_bucket=throughput_bucket,
        availability_strategy=availability_strategy,
        response_hook=response_hook,
    )


def build_delete_item_request_options(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Build the request-options dict the legacy ``DeleteItem`` consumes.

    Pure function. Delete has no ``disableAutomaticIdGeneration`` /
    ``indexingDirective`` / ``populateQueryMetrics`` knobs, so this is
    just a thin wrapper around ``build_options``. The container method
    already drops ``populate_query_metrics`` (with a deprecation
    warning) before kwargs reach here.

    :param dict[str, Any] kwargs: Working keywords consumed by the legacy options builder.
    :return: Internal deletion request options.
    :rtype: dict[str, Any]
    """
    from .._base import build_options
    return build_options(kwargs)


def merge_read_item_explicit_kwargs(
    kwargs: Dict[str, Any],
    *,
    post_trigger_include: Any = None,
    session_token: Any = None,
    initial_headers: Any = None,
    etag: Any = None,
    match_condition: Any = None,
    max_integrated_cache_staleness_in_ms: Any = None,
    priority: Any = None,
    throughput_bucket: Any = None,
    availability_strategy: Any = None,
    response_hook: Any = None,
) -> None:
    """Copy every non-None explicit ``read_item`` kwarg into ``kwargs``.

    Differences from ``merge_delete_item_explicit_kwargs``:

    * No ``pre_trigger_include`` (read_item has no pre-trigger surface).
    * No ``retry_write`` / ``no_response``: the read API does not expose
      write-retry or write-response suppression options.
    * Adds ``max_integrated_cache_staleness_in_ms``, the dedicated-
      gateway cache-staleness knob that only exists on reads.

    The caller validates ``max_integrated_cache_staleness_in_ms``
    (negative / non-int) so the ``ValueError`` traceback points at the
    customer's call line, not this helper. ``availability_strategy``
    is passed through the hedging-strategy validator.

    :param dict[str, Any] kwargs: Working call keywords updated in place.
    :keyword Any post_trigger_include: Post-trigger option copied when not None.
    :keyword Any session_token: Session token copied when not None.
    :keyword Any initial_headers: Caller header overrides copied when not None.
    :keyword Any etag: ETag copied for conditional request preparation.
    :keyword Any match_condition: Match condition copied for conditional request preparation.
    :keyword Any max_integrated_cache_staleness_in_ms: Cache-staleness bound copied when not None.
    :keyword Any priority: Request priority copied when not None.
    :keyword Any throughput_bucket: Throughput bucket copied when not None.
    :keyword Any availability_strategy: Hedging strategy validated before copying.
    :keyword Any response_hook: Response callback copied when not None.
    :return: None.
    :rtype: None
    """
    _merge_explicit_item_kwargs(
        kwargs,
        post_trigger_include=post_trigger_include,
        session_token=session_token,
        initial_headers=initial_headers,
        etag=etag,
        match_condition=match_condition,
        max_integrated_cache_staleness_in_ms=max_integrated_cache_staleness_in_ms,
        priority=priority,
        throughput_bucket=throughput_bucket,
        availability_strategy=availability_strategy,
        response_hook=response_hook,
    )


def build_read_item_request_options(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Build the request-options dict the legacy ``ReadItem`` consumes.

    Thin wrapper around ``build_options`` -- read has no
    ``disableAutomaticIdGeneration`` / ``indexingDirective`` knobs.
    Both public clients reject ``populate_query_metrics`` by presence
    before reaching this helper.

    :param dict[str, Any] kwargs: Working keywords consumed by the legacy options builder.
    :return: Internal read request options.
    :rtype: dict[str, Any]
    """
    from .._base import build_options
    return build_options(kwargs)


def merge_upsert_replace_item_kwargs(
    kwargs: Dict[str, Any],
    *,
    pre_trigger_include: Any = None,
    post_trigger_include: Any = None,
    session_token: Any = None,
    initial_headers: Any = None,
    etag: Any = None,
    match_condition: Any = None,
    priority: Any = None,
    no_response: Any = None,
    retry_write: Any = None,
    throughput_bucket: Any = None,
    availability_strategy: Any = None,
    response_hook: Any = None,
) -> None:
    """Merge non-None explicit kwargs shared by ``upsert_item`` and ``replace_item``.

    Both operations support ``no_response``, ``etag`` and ``match_condition``.
    This helper does not accept ``indexing_directive`` or
    ``enable_automatic_id_generation``. ``availability_strategy`` is validated
    before it is stored.

    :param dict[str, Any] kwargs: Working call keywords updated in place.
    :keyword Any pre_trigger_include: Pre-trigger option copied when not None.
    :keyword Any post_trigger_include: Post-trigger option copied when not None.
    :keyword Any session_token: Session token copied when not None.
    :keyword Any initial_headers: Caller header overrides copied when not None.
    :keyword Any etag: ETag copied for conditional request preparation.
    :keyword Any match_condition: Match condition copied for conditional request preparation.
    :keyword Any priority: Request priority copied when not None.
    :keyword Any no_response: Write-response suppression option copied when not None.
    :keyword Any retry_write: Write retry override copied under its internal option name.
    :keyword Any throughput_bucket: Throughput bucket copied when not None.
    :keyword Any availability_strategy: Hedging strategy validated before copying.
    :keyword Any response_hook: Response callback copied when not None.
    :return: None.
    :rtype: None
    """
    _merge_explicit_item_kwargs(
        kwargs,
        pre_trigger_include=pre_trigger_include,
        post_trigger_include=post_trigger_include,
        session_token=session_token,
        initial_headers=initial_headers,
        etag=etag,
        match_condition=match_condition,
        priority=priority,
        no_response=no_response,
        retry_write=retry_write,
        throughput_bucket=throughput_bucket,
        availability_strategy=availability_strategy,
        response_hook=response_hook,
    )


def build_upsert_item_request_options(
    kwargs: Dict[str, Any],
    *,
    populate_query_metrics: Optional[bool] = None,
) -> Dict[str, Any]:
    """Build the request-options dict the legacy ``UpsertItem`` consumes.

    Pure function. Like ``build_create_item_request_options`` but with
    two upsert-specific differences:

    * ``disableAutomaticIdGeneration`` is always ``True`` -- an upsert
      never mints an id (it targets a specific id), matching the value
      the legacy ``upsert_item`` writes unconditionally.
    * There is no ``indexing_directive`` knob (not on the public
      signature).

    ``etag`` / ``match_condition`` are kept: ``build_options`` converts them
    into ``accessCondition`` for the legacy path's conditional request headers.
    Rust-path preparation carries the same conditions in typed request settings.

    ``populate_query_metrics`` is only meaningful on the sync container
    method (the async sibling never exposed it); the async caller passes
    ``None`` so the warning and option-key write are skipped. The
    ``is not None`` gate (rather than a truthy check) preserves the exact
    legacy ``upsert_item`` behaviour, which warned for any explicit value
    including ``False``.

    :param dict[str, Any] kwargs: Working keywords consumed by the legacy options builder.
    :keyword bool or None populate_query_metrics: Deprecated metrics flag retained for compatibility callers.
    :return: Internal upsert options with automatic ID generation disabled.
    :rtype: dict[str, Any]
    """
    from .._base import build_options
    request_options = build_options(kwargs)
    request_options["disableAutomaticIdGeneration"] = True
    if populate_query_metrics is not None:
        warnings.warn(
            "the populate_query_metrics flag does not apply to this method "
            "and will be removed in the future",
            DeprecationWarning,
        )
        request_options["populateQueryMetrics"] = populate_query_metrics
    return request_options


def merge_patch_item_explicit_kwargs(
    kwargs: Dict[str, Any],
    *,
    pre_trigger_include: Any = None,
    post_trigger_include: Any = None,
    session_token: Any = None,
    etag: Any = None,
    match_condition: Any = None,
    priority: Any = None,
    no_response: Any = None,
    retry_write: Any = None,
    throughput_bucket: Any = None,
    availability_strategy: Any = None,
    response_hook: Any = None,
) -> None:
    """Copy every non-None explicit ``patch_item`` kwarg into ``kwargs``.

    ``filter_predicate`` and ``patch_operations`` are passed to the helper
    separately, not merged here. ``availability_strategy`` is validated
    before it is stored.

    :param dict[str, Any] kwargs: Working call keywords updated in place.
    :keyword Any pre_trigger_include: Pre-trigger option copied when not None.
    :keyword Any post_trigger_include: Post-trigger option copied when not None.
    :keyword Any session_token: Session token copied when not None.
    :keyword Any etag: ETag copied for conditional request preparation.
    :keyword Any match_condition: Match condition copied for conditional request preparation.
    :keyword Any priority: Request priority copied when not None.
    :keyword Any no_response: Write-response suppression option copied when not None.
    :keyword Any retry_write: Write retry override copied under its internal option name.
    :keyword Any throughput_bucket: Throughput bucket copied when not None.
    :keyword Any availability_strategy: Hedging strategy validated before copying.
    :keyword Any response_hook: Response callback copied when not None.
    :return: None.
    :rtype: None
    """
    _merge_explicit_item_kwargs(
        kwargs,
        pre_trigger_include=pre_trigger_include,
        post_trigger_include=post_trigger_include,
        session_token=session_token,
        etag=etag,
        match_condition=match_condition,
        priority=priority,
        no_response=no_response,
        retry_write=retry_write,
        throughput_bucket=throughput_bucket,
        availability_strategy=availability_strategy,
        response_hook=response_hook,
    )


def build_patch_item_request_options(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Build the ``request_options`` dict the legacy ``PatchItem`` consumes.

    Always disables automatic id generation. ``etag`` / ``match_condition``
    are folded into ``accessCondition`` by ``build_options``. The helper
    sets ``filterPredicate`` itself; it is not a ``build_options`` key.

    :param dict[str, Any] kwargs: Working keywords consumed by the legacy options builder.
    :return: Internal patch options with automatic ID generation disabled.
    :rtype: dict[str, Any]
    """
    from .._base import build_options
    request_options = build_options(kwargs)
    request_options["disableAutomaticIdGeneration"] = True
    return request_options

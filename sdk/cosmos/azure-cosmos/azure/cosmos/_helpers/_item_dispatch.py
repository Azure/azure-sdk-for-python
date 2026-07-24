# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Pure helpers shared by the sync and async item-helper classes.

The sync ``ItemHelper`` and async ``AsyncItemHelper`` only differ in
where they ``await``; the dispatch decision, option-dict build, and
kwarg-stamping logic are identical. This module centralises them so
the two helpers cannot drift. Nothing here performs I/O.
"""
from __future__ import annotations

import warnings
from typing import Any, Dict, Optional, cast

from .._availability_strategy_config import _validate_request_hedging_strategy
from .._backend.base import CosmosBackend
from .._base import build_options
from .._constants import _Constants as Constants


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
    ``Container.create_item`` methods would otherwise repeat inline. Both the
    sync and async ``create_item`` declare ``response_hook`` as an
    explicit keyword-only parameter and forward it here.
    ``availability_strategy`` is passed through the hedging-strategy
    validator.
    """
    if pre_trigger_include is not None:
        kwargs['pre_trigger_include'] = pre_trigger_include
    if post_trigger_include is not None:
        kwargs['post_trigger_include'] = post_trigger_include
    if session_token is not None:
        kwargs['session_token'] = session_token
    if initial_headers is not None:
        kwargs['initial_headers'] = initial_headers
    if priority is not None:
        kwargs['priority'] = priority
    if no_response is not None:
        kwargs['no_response'] = no_response
    if retry_write is not None:
        kwargs[Constants.Kwargs.RETRY_WRITE] = retry_write
    if throughput_bucket is not None:
        kwargs["throughput_bucket"] = throughput_bucket
    if availability_strategy is not None:
        kwargs["availability_strategy"] = _validate_request_hedging_strategy(availability_strategy)
    if response_hook is not None:
        kwargs['response_hook'] = response_hook


def pick_backend(client_connection: Any) -> Optional[CosmosBackend]:
    """Return the stored backend selection: a rust backend, or ``None``.

    ``None`` means core-python was selected. This is the raw, ``Optional``
    selection stored at client construction. Every family coordinator coerces
    this selection to an explicit
    :class:`~azure.cosmos._backend.legacy.LegacyBackend` (via
    :func:`~azure.cosmos._backend.legacy.coerce_backend`) so it holds one backend
    by interface and never branches on ``None``. The selection is made once at
    construction and never reconsidered per call.

    :param client_connection: The connection that owns the ``_backend``
        attribute. A missing attribute is tolerated.
    :returns: The rust backend instance, or ``None`` for core-python.
    """
    connection_dict = getattr(client_connection, "__dict__", None)
    if isinstance(connection_dict, dict):
        return cast(Optional[CosmosBackend], connection_dict.get("_backend"))
    return cast(Optional[CosmosBackend], getattr(client_connection, "_backend", None))


def build_create_item_request_options(
    kwargs: Dict[str, Any],
    *,
    enable_automatic_id_generation: bool,
    indexing_directive: Optional[int],
    populate_query_metrics: Optional[bool] = None,
) -> Dict[str, Any]:
    """Build the request-options dict the legacy ``CreateItem`` consumes.

    Pure function. ``populate_query_metrics`` is only meaningful on the
    sync container method (the async sibling never exposed it); the
    async caller passes ``None`` and the warning + option-key write are
    skipped.

    :param kwargs: Per-call kwargs forwarded to ``build_options``;
        not mutated by this function.
    :type kwargs: Dict[str, Any]
    :param enable_automatic_id_generation: Negated into
        ``options["disableAutomaticIdGeneration"]``.
    :type enable_automatic_id_generation: bool
    :param indexing_directive: Written to ``options["indexingDirective"]``
        when supplied.
    :type indexing_directive: Optional[int]
    :param populate_query_metrics: When truthy, emits the deprecation
        warning and writes ``options["populateQueryMetrics"]``.
    :type populate_query_metrics: Optional[bool]
    :returns: The request-options dict.
    :rtype: Dict[str, Any]
    """
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
    """
    if pre_trigger_include is not None:
        kwargs['pre_trigger_include'] = pre_trigger_include
    if post_trigger_include is not None:
        kwargs['post_trigger_include'] = post_trigger_include
    if session_token is not None:
        kwargs['session_token'] = session_token
    if initial_headers is not None:
        kwargs['initial_headers'] = initial_headers
    if etag is not None:
        kwargs['etag'] = etag
    if match_condition is not None:
        kwargs['match_condition'] = match_condition
    if priority is not None:
        kwargs['priority'] = priority
    if retry_write is not None:
        kwargs[Constants.Kwargs.RETRY_WRITE] = retry_write
    if throughput_bucket is not None:
        kwargs["throughput_bucket"] = throughput_bucket
    if availability_strategy is not None:
        kwargs["availability_strategy"] = _validate_request_hedging_strategy(availability_strategy)
    if response_hook is not None:
        kwargs['response_hook'] = response_hook


def build_delete_item_request_options(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Build the request-options dict the legacy ``DeleteItem`` consumes.

    Pure function. Delete has no ``disableAutomaticIdGeneration`` /
    ``indexingDirective`` / ``populateQueryMetrics`` knobs, so this is
    just a thin wrapper around ``build_options``. The container method
    already drops ``populate_query_metrics`` (with a deprecation
    warning) before kwargs reach here.
    """
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
    * No ``retry_write`` / ``no_response`` (reads are idempotent and
      have no body to suppress).
    * Adds ``max_integrated_cache_staleness_in_ms``, the dedicated-
      gateway cache-staleness knob that only exists on reads.

    The caller validates ``max_integrated_cache_staleness_in_ms``
    (negative / non-int) so the ``ValueError`` traceback points at the
    customer's call line, not this helper. ``availability_strategy``
    is passed through the hedging-strategy validator.
    """
    if post_trigger_include is not None:
        kwargs['post_trigger_include'] = post_trigger_include
    if session_token is not None:
        kwargs['session_token'] = session_token
    if initial_headers is not None:
        kwargs['initial_headers'] = initial_headers
    if etag is not None:
        kwargs['etag'] = etag
    if match_condition is not None:
        kwargs['match_condition'] = match_condition
    if max_integrated_cache_staleness_in_ms is not None:
        kwargs['max_integrated_cache_staleness_in_ms'] = max_integrated_cache_staleness_in_ms
    if priority is not None:
        kwargs['priority'] = priority
    if throughput_bucket is not None:
        kwargs["throughput_bucket"] = throughput_bucket
    if availability_strategy is not None:
        kwargs["availability_strategy"] = _validate_request_hedging_strategy(availability_strategy)
    if response_hook is not None:
        kwargs['response_hook'] = response_hook


def build_read_item_request_options(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Build the request-options dict the legacy ``ReadItem`` consumes.

    Thin wrapper around ``build_options`` -- read has no
    ``disableAutomaticIdGeneration`` / ``indexingDirective`` knobs, and
    ``populate_query_metrics`` is dropped (with a deprecation warning)
    by the sync public method before reaching here. The async sibling
    does not expose ``populate_query_metrics`` at all.
    """
    return build_options(kwargs)


def merge_upsert_item_explicit_kwargs(
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
    """Copy every non-None explicit ``upsert_item`` kwarg into ``kwargs``.

    Upsert is write-with-body like create, so it keeps ``no_response``
    (an upsert returns a body worth suppressing). It also honours
    ``etag`` / ``match_condition`` like delete -- an upsert can be
    narrowed to insert-only or a version-guarded replace -- so those two
    are merged here too. It has neither ``indexing_directive`` nor
    ``enable_automatic_id_generation`` (neither is on the public
    ``upsert_item`` signature). ``availability_strategy`` is passed
    through the hedging-strategy validator.
    """
    if pre_trigger_include is not None:
        kwargs['pre_trigger_include'] = pre_trigger_include
    if post_trigger_include is not None:
        kwargs['post_trigger_include'] = post_trigger_include
    if session_token is not None:
        kwargs['session_token'] = session_token
    if initial_headers is not None:
        kwargs['initial_headers'] = initial_headers
    if etag is not None:
        kwargs['etag'] = etag
    if match_condition is not None:
        kwargs['match_condition'] = match_condition
    if priority is not None:
        kwargs['priority'] = priority
    if no_response is not None:
        kwargs['no_response'] = no_response
    if retry_write is not None:
        kwargs[Constants.Kwargs.RETRY_WRITE] = retry_write
    if throughput_bucket is not None:
        kwargs["throughput_bucket"] = throughput_bucket
    if availability_strategy is not None:
        kwargs["availability_strategy"] = _validate_request_hedging_strategy(availability_strategy)
    if response_hook is not None:
        kwargs['response_hook'] = response_hook


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

    ``etag`` / ``match_condition`` are honoured here, not dropped:
    ``build_options`` consumes them into the ``accessCondition`` shape,
    which both the rust prep and the legacy path emit as ``If-Match`` /
    ``If-None-Match``.

    ``populate_query_metrics`` is only meaningful on the sync container
    method (the async sibling never exposed it); the async caller passes
    ``None`` so the warning and option-key write are skipped. The
    ``is not None`` gate (rather than a truthy check) preserves the exact
    legacy ``upsert_item`` behaviour, which warned for any explicit value
    including ``False``.
    """
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
    """
    if pre_trigger_include is not None:
        kwargs['pre_trigger_include'] = pre_trigger_include
    if post_trigger_include is not None:
        kwargs['post_trigger_include'] = post_trigger_include
    if session_token is not None:
        kwargs['session_token'] = session_token
    if etag is not None:
        kwargs['etag'] = etag
    if match_condition is not None:
        kwargs['match_condition'] = match_condition
    if priority is not None:
        kwargs['priority'] = priority
    if no_response is not None:
        kwargs['no_response'] = no_response
    if retry_write is not None:
        kwargs[Constants.Kwargs.RETRY_WRITE] = retry_write
    if throughput_bucket is not None:
        kwargs["throughput_bucket"] = throughput_bucket
    if availability_strategy is not None:
        kwargs["availability_strategy"] = _validate_request_hedging_strategy(availability_strategy)
    if response_hook is not None:
        kwargs['response_hook'] = response_hook


def build_patch_item_request_options(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Build the ``request_options`` dict the legacy ``PatchItem`` consumes.

    Always disables automatic id generation. ``etag`` / ``match_condition``
    are folded into ``accessCondition`` by ``build_options``. The helper
    sets ``filterPredicate`` itself; it is not a ``build_options`` key.
    """
    request_options = build_options(kwargs)
    request_options["disableAutomaticIdGeneration"] = True
    return request_options

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
from typing import Any, Dict, Optional

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

    Folds the ``if X is not None: kwargs['X'] = X`` boilerplate that
    the two ``Container.create_item`` methods used to inline. Both the
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
    """Return the wired Rust backend, or ``None`` for the legacy path.

    A ``None`` return is the signal to fall through to the legacy
    ``client_connection.CreateItem`` path; there is no "core-python
    backend" class. The decision is made once at client construction
    and never reconsidered per call.

    :param client_connection: The connection that owns the
        ``_rust_backend`` attribute. Missing attribute is tolerated.
    :returns: The Rust backend instance, or ``None``.
    """
    return getattr(client_connection, "_rust_backend", None)


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


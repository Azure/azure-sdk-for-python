# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Pure helpers shared by the sync and async item-helper classes.

The sync ``ItemHelper`` and async ``AsyncItemHelper`` differ only in
where they say ``await``: the dispatch decision, the option-dict
build, and the kwarg-stamping for the user-agent policy are all the
same logic. Putting that logic here means the two classes stay short
and the dispatch / option-build behaviour cannot drift between sync
and async by accident.

Nothing in this module performs I/O or awaits anything; both helpers
operate on plain dicts and return values the caller then routes
through the appropriate sync or async I/O path.
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
    """Move every non-None explicit ``create_item`` kwarg into ``kwargs``.

    The two ``Container.create_item`` methods (sync and async) each
    used to inline ``if X is not None: kwargs['X'] = X`` for ten
    optional kwargs. This helper folds that boilerplate into one
    place so the two methods stay short and the option-name mapping
    cannot drift between sync and async.

    The async sibling does not expose ``response_hook`` as an explicit
    parameter (it rides through ``**kwargs`` directly), so the async
    caller simply leaves the default ``response_hook=None``.

    ``availability_strategy`` is passed through the hedging-strategy
    validator here because both call sites used to do that inline and
    the validator is pure.
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
    """Return the backend the helper should hand operations to.

    The decision was made once when the client was constructed and is
    never reconsidered per call:

    * If a Rust backend is wired on this connection, use it.
    * Otherwise return ``None`` — the helper treats that as the signal
      to fall through to the legacy ``client_connection.CreateItem``
      path. There is no "core-python backend" class wrapping the
      ``None``; the absence of a Rust backend is the absence of any
      backend, by design (see ``_backend/factory.py``).

    The Rust backend's per-feature support level is a property of the
    backend itself, not of the call. If a kwarg the Rust backend does
    not honor reaches the wire, that is either a known limitation or
    a bug to fix in the Rust path; the dispatch site does not silently
    re-route to a different backend.

    :param client_connection: The connection that owns the
        ``_rust_backend`` attribute. The attribute may be missing on a
        connection built outside ``CosmosClient`` (some unit tests);
        the function tolerates that and returns ``None`` so the caller
        falls through to the legacy code path.
    :returns: The Rust backend instance when wired, otherwise ``None``.
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

    Pure function. Same behaviour as the inline option-build that used
    to live in ``Container.create_item``: the legacy
    ``build_options(kwargs)`` produces the base dict, then the three
    explicit container-method kwargs are stamped on top.

    The ``populate_query_metrics`` parameter is only meaningful on
    the sync container method (the async sibling never exposed it).
    Pass ``None`` from the async caller; the warning + option-key
    write are skipped in that case.

    :param kwargs: The per-call kwargs dict. Forwarded to
        ``build_options``; not mutated by this function.
    :type kwargs: Dict[str, Any]
    :param enable_automatic_id_generation: From the container's
        explicit kwarg. The negation lands in
        ``options["disableAutomaticIdGeneration"]``.
    :type enable_automatic_id_generation: bool
    :param indexing_directive: From the container's explicit kwarg.
        Written to ``options["indexingDirective"]`` when supplied.
    :type indexing_directive: Optional[int]
    :param populate_query_metrics: From the sync container's explicit
        kwarg. When truthy, emits the existing deprecation warning
        and writes the option key. ``None`` (the async default)
        skips both.
    :type populate_query_metrics: Optional[bool]
    :returns: The request-options dict, ready to be handed to the
        cache-populate callback and then to ``CreateItem``.
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


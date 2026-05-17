# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Single source of truth for the kwarg -> internal-option-key mapping.

Customer-facing methods like ``Container.create_item`` accept Python-style
keyword arguments (``pre_trigger_include``, ``priority``,
``throughput_bucket``). Inside the SDK those names are translated to the
internal option keys the lower layers expect (``preTriggerInclude``,
``priorityLevel``, ``throughputBucket``), and from there the request-
header builder (``_base.GetHeaders``) reads each option key and writes
the matching ``x-ms-...`` HTTP header on the wire.

The mapping in ``COMMON_OPTIONS`` below is the *first* of those two
translation steps. Putting it here lets both the existing core-python
path and the future rust-backend item helper consume the same table,
which is how we guarantee both backends emit byte-identical request
headers for the same kwargs.

If a customer-facing kwarg is renamed, gains a new value, or starts
mapping to a different internal option key, this is the one place that
changes. ``_base.py`` re-imports ``COMMON_OPTIONS`` under its existing
private name (``_COMMON_OPTIONS``) so legacy call sites are unchanged.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping

from .._constants import _Constants as Constants

# Customer-facing kwarg name (snake_case) -> internal option-dict key
# (camelCase or constant-defined name) the lower SDK layers consume.
#
# NOTE: This dict is deliberately public *within the _helpers package*
# (no leading underscore) because it is consumed from outside this
# module — both ``_base.build_options`` (legacy path) and the future
# item helper read it. The leading-underscore alias ``_COMMON_OPTIONS``
# is kept in ``_base.py`` for source compatibility with anything that
# still grepped the old name.
COMMON_OPTIONS: Dict[str, str] = {
    "initial_headers": "initialHeaders",
    "pre_trigger_include": "preTriggerInclude",
    "post_trigger_include": "postTriggerInclude",
    "access_condition": "accessCondition",
    "session_token": "sessionToken",
    "resource_token_expiry_seconds": "resourceTokenExpirySeconds",
    "offer_enable_ru_per_minute_throughput": "offerEnableRUPerMinuteThroughput",
    "disable_ru_per_minute_usage": "disableRUPerMinuteUsage",
    "continuation": "continuation",
    "content_type": "contentType",
    "is_query_plan_request": "isQueryPlanRequest",
    "supported_query_features": "supportedQueryFeatures",
    "query_version": "queryVersion",
    "priority": "priorityLevel",
    "no_response": "responsePayloadOnWriteDisabled",
    "retry_write": Constants.Kwargs.RETRY_WRITE,
    "max_item_count": "maxItemCount",
    "throughput_bucket": "throughputBucket",
    "excluded_locations": Constants.Kwargs.EXCLUDED_LOCATIONS,
    "availability_strategy": Constants.Kwargs.AVAILABILITY_STRATEGY,
}


def compose_options_from_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Pop every recognised kwarg out of ``kwargs`` into a fresh options dict.

    This is the *pure* sibling of ``_base.build_options``: it handles only
    the kwarg-name -> option-key translation step using
    ``COMMON_OPTIONS`` as the single source of truth. It does not stamp
    an operation start time, does not pull ``read_timeout`` / ``timeout``
    (those are wired separately by the call site that owns the
    timeout policy), and does not handle ``etag`` /
    ``match_condition`` (those route through ``_base._get_match_headers``
    and are deprecated for ``create_item`` regardless).

    The function is intentionally narrow so the future item helper can
    use it without inheriting any of the side effects ``build_options``
    accumulated over the years. Both code paths still see the same
    mapping table, which is what guarantees parity.

    :param kwargs: The caller's ``**kwargs`` dict. **Mutated:** every
        recognised key is popped out so the caller can forward the
        remaining kwargs without double-handling.
    :type kwargs: Dict[str, Any]
    :returns: A new dict whose keys are the internal option-key names
        from ``COMMON_OPTIONS``. If the caller already had a
        ``request_options`` dict in ``kwargs`` it is consumed as the
        starting point (matches ``build_options`` behaviour) so callers
        can pre-seed options that don't have a kwarg shortcut.
    :rtype: Dict[str, Any]
    """
    # Match build_options: a pre-built request_options dict (rare but
    # supported) seeds the result, and any kwarg-shortcut overrides
    # what was in it.
    options: Dict[str, Any] = dict(kwargs.pop("request_options", {}) or {})

    for kwarg_name, option_key in COMMON_OPTIONS.items():
        if kwarg_name in kwargs:
            options[option_key] = kwargs.pop(kwarg_name)

    return options


def get_common_options() -> Mapping[str, str]:
    """Return a read-only view of ``COMMON_OPTIONS`` for inspection / tests.

    Returning a ``Mapping`` rather than the dict itself makes accidental
    mutation by a caller a typing error rather than a silent shared-
    state bug.

    :returns: A mapping of customer-facing kwarg names to internal
        option-key names.
    :rtype: Mapping[str, str]
    """
    return COMMON_OPTIONS

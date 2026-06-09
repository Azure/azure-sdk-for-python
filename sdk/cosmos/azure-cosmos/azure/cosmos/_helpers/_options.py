# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Single source of truth for the kwarg -> internal-option-key mapping.

Customer-facing methods accept snake_case kwargs (``pre_trigger_include``,
``priority``, ``throughput_bucket``); the lower SDK layers expect
internal option-dict keys (``preTriggerInclude``, ``priorityLevel``,
``throughputBucket``). ``COMMON_OPTIONS`` is that mapping.

Both backends consume it so they produce byte-identical request
headers.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping

from .._constants import _Constants as Constants

# snake_case kwarg name -> internal option-dict key.
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
    "max_integrated_cache_staleness_in_ms": "maxIntegratedCacheStaleness",
}


def compose_options_from_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Pop every recognised kwarg out of ``kwargs`` into a fresh options dict.

    Handles only the kwarg-name -> option-key translation. Does not
    stamp timing fields, does not handle ``etag`` / ``match_condition``
    (those go through the legacy match-headers helper), and does not
    pull ``read_timeout`` / ``timeout``.

    A pre-existing ``request_options`` dict in ``kwargs`` is consumed
    as the starting point; kwarg shortcuts override entries from it.

    :param kwargs: Caller's ``**kwargs``. **Mutated:** every recognised
        key (and ``request_options``) is popped.
    :type kwargs: Dict[str, Any]
    :returns: A new dict keyed by internal option-key names.
    :rtype: Dict[str, Any]
    """
    options: Dict[str, Any] = dict(kwargs.pop("request_options", {}) or {})
    for kwarg_name, option_key in COMMON_OPTIONS.items():
        if kwarg_name in kwargs:
            options[option_key] = kwargs.pop(kwarg_name)
    return options


def get_common_options() -> Mapping[str, str]:
    """Return a read-only view of ``COMMON_OPTIONS``.

    Returning a ``Mapping`` makes accidental mutation by a caller a
    typing error rather than a silent shared-state bug.

    :rtype: Mapping[str, str]
    """
    return COMMON_OPTIONS

# The MIT License (MIT)
# Copyright (c) 2025 Microsoft Corporation

from typing import Iterable, Mapping, Optional, Any, Collection


def select_next_ppaf_region(
        available_account_regional_endpoints: Mapping[str, Any],
        endpoint_region: str,
        current_region: Optional[str],
        unavailable_regional_endpoints: Collection[str],
        excluded_locations: Optional[Iterable[str]] = None) -> Optional[str]:
    """Select the next region for PPAF using a deterministic preference order.

    Preference order:
      1. Non-excluded available regions.
      2. Excluded available regions.
      3. Excluded current_region (if different from endpoint_region and still available).
    """
    excluded = set(excluded_locations or [])

    current_region_fallback = None
    if endpoint_region != current_region and current_region is not None:
        if (current_region in available_account_regional_endpoints
                and current_region not in unavailable_regional_endpoints):
            if current_region not in excluded:
                return current_region
            current_region_fallback = current_region

    fallback_excluded_region = None
    for regional_endpoint in available_account_regional_endpoints:
        if regional_endpoint == current_region:
            continue

        if regional_endpoint in unavailable_regional_endpoints:
            continue

        if regional_endpoint in excluded:
            if fallback_excluded_region is None:
                fallback_excluded_region = regional_endpoint
            continue

        return regional_endpoint

    if fallback_excluded_region is not None:
        return fallback_excluded_region

    if current_region_fallback is not None:
        return current_region_fallback

    return None


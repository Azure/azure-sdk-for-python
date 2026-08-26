# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the current preview capability registry."""

from _capabilities import CAPABILITIES, _has_capability_attr, _resolve


def test_all_registered_capabilities_match_current_public_surface():
    unresolved = []

    for name, capability in CAPABILITIES.items():
        try:
            owner = _resolve(capability["owner"])
        except (ImportError, AttributeError):
            unresolved.append(name)
            continue
        if any(not _has_capability_attr(owner, item) for item in capability["kwargs"]):
            unresolved.append(name)

    assert unresolved == []
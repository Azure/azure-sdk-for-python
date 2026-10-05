# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the current preview capability registry."""

import pytest

from azure.search.documents import DEFAULT_VERSION

from _capabilities import CAPABILITIES, _has_capability_attr, _resolve


@pytest.mark.skipif(not DEFAULT_VERSION.value.endswith("-preview"), reason="GA excludes preview-only capabilities")
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


def test_registered_capabilities_have_valid_metadata():
    for capability in CAPABILITIES.values():
        assert capability["owner"].startswith("azure.search.documents.")
        assert isinstance(capability["kwargs"], tuple)
        assert all(isinstance(name, str) and name for name in capability["kwargs"])
        assert capability["available_from"]

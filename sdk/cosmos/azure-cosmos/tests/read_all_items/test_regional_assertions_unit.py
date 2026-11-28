# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Regional tests must fail rather than accept missing or wrong routing evidence."""

from types import SimpleNamespace

import pytest

from read_all_items.test_excluded_locations import assert_serving_regions


@pytest.mark.parametrize("regions", [[], [None], ["West US"], ["East US", "West US"]])
def test_regional_verification_rejects_missing_or_excluded_attempts(regions):
    completion = SimpleNamespace(
        diagnostics=SimpleNamespace(
            request_count=len(regions),
            attempts=[SimpleNamespace(region=region) for region in regions],
        )
    )
    with pytest.raises(AssertionError):
        assert_serving_regions([completion], ["East US"])


def test_regional_verification_accepts_actual_regions_with_normalized_names():
    completion = SimpleNamespace(
        diagnostics=SimpleNamespace(
            request_count=2,
            attempts=[
                SimpleNamespace(region="East US"),
                SimpleNamespace(region="eastus"),
            ],
        )
    )
    assert_serving_regions([completion], ["East US"])


def test_regional_verification_rejects_truncated_attempts():
    completion = SimpleNamespace(
        diagnostics=SimpleNamespace(
            request_count=2,
            attempts=[SimpleNamespace(region="East US")],
        )
    )
    with pytest.raises(AssertionError, match="Truncated"):
        assert_serving_regions([completion], ["East US"])

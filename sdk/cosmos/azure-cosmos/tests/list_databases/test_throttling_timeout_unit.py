# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Prove the supplemental throttling assertions reject misleading outcomes."""

import pytest

from list_databases._throttling_timeout import assert_throttled_timeout


@pytest.mark.parametrize("timeout", [30, 29, 20, 12])
def test_throttling_timeout_assertions_accept_retries_at_the_deadline_rust(timeout):
    assert_throttled_timeout((0, 4, 7), (timeout, 7, 7), timeout)


@pytest.mark.parametrize("timeout", [30, 29, 20, 12])
@pytest.mark.parametrize("failure", ["no-retry", "early", "late", "legacy-replay"])
def test_throttling_timeout_assertions_reject_incomplete_evidence_rust(timeout, failure):
    elapsed = timeout - 2 if failure == "early" else timeout + 5 if failure == "late" else timeout
    hits = 1 if failure == "no-retry" else 3
    fallback = 1 if failure == "legacy-replay" else 0
    with pytest.raises(AssertionError):
        assert_throttled_timeout((0, 4, 7), (elapsed, 4 + hits, 7 + fallback), timeout)

# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Exercise opt-in safety and copied split controls without a service."""

import asyncio
import importlib
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock

import pytest

from get_latest_session_token import _split_support as support


@pytest.mark.parametrize("surface", ["sync", "aio"])
@pytest.mark.parametrize("opt_in", [None, "", "0", "true"])
def test_real_split_setup_rejects_missing_explicit_approval_before_clients_rust(monkeypatch, surface, opt_in):
    if opt_in is None:
        monkeypatch.delenv(support.REAL_SPLIT_ENV, raising=False)
    else:
        monkeypatch.setenv(support.REAL_SPLIT_ENV, opt_in)
    name = "test_latest_session_token_real_split" + ("_async" if surface == "aio" else "")
    module = importlib.import_module(f"get_latest_session_token.{surface}.legacy.{name}")
    constructor = Mock(side_effect=AssertionError("Client must not be constructed without approval"))
    monkeypatch.setattr(module, "CosmosClient", constructor)
    cls = module.TestLatestSessionTokenRealSplitAsync if surface == "aio" else module.TestLatestSessionTokenRealSplit
    case = cls()
    with pytest.raises(unittest.SkipTest, match="environment-gap:.*explicit approval"):
        if surface == "aio":
            asyncio.run(case.asyncSetUp())
        else:
            case.setUp()
    constructor.assert_not_called()


@pytest.mark.parametrize("missing", ["ACCOUNT_HOST", "ACCOUNT_KEY"])
def test_real_split_requires_credentials_even_when_approved_rust(monkeypatch, missing):
    monkeypatch.setenv(support.REAL_SPLIT_ENV, "1")
    monkeypatch.setenv("ACCOUNT_HOST", "unused")
    monkeypatch.setenv("ACCOUNT_KEY", "unused")
    monkeypatch.delenv(missing)
    with pytest.raises(unittest.SkipTest, match="environment-gap:.*ACCOUNT_HOST"):
        support.require_real_split()


def test_real_split_gate_accepts_only_explicit_approval_with_configuration_rust(monkeypatch):
    monkeypatch.setenv(support.REAL_SPLIT_ENV, "1")
    monkeypatch.setenv("ACCOUNT_HOST", "unused")
    monkeypatch.setenv("ACCOUNT_KEY", "unused")
    support.require_real_split()


@pytest.mark.parametrize("asynchronous", [False, True])
def test_throughput_helper_itself_cannot_bypass_opt_in_rust(monkeypatch, asynchronous):
    monkeypatch.delenv(support.REAL_SPLIT_ENV, raising=False)
    container = Mock()
    with pytest.raises(unittest.SkipTest, match="environment-gap:.*explicit approval"):
        if asynchronous:
            asyncio.run(support.trigger_split_async(container, 11000))
        else:
            support.trigger_split(container, 11000)
    assert container.mock_calls == []


def test_rust_routing_internals_are_explicitly_excluded_without_touching_python_cache_rust():
    class NoPythonCache:
        @property
        def client_connection(self):
            raise AssertionError("Rust test must not inspect the legacy connection cache")

    with pytest.warns(UserWarning, match="internals-only:.*do not establish Rust stale-routing recovery"):
        restore = support.snapshot_split_routing_map(NoPythonCache(), "rid", legacy_routing_cache=False)
    restore()


def test_legacy_snapshot_retains_warm_cache_assertion_and_scoped_restore_rust(monkeypatch):
    monkeypatch.setattr(support._base, "GetResourceIdOrFullNameFromLink", lambda link: "name")
    cache = {}
    container = SimpleNamespace(
        container_link="link",
        client_connection=SimpleNamespace(
            _routing_map_provider=SimpleNamespace(_collection_routing_map_by_item=cache)
        ),
    )
    with pytest.raises(AssertionError, match="must warm this container"):
        support.snapshot_split_routing_map(container, "rid", legacy_routing_cache=True)
    cache.update(name="parent", unrelated="keep")
    restore = support.snapshot_split_routing_map(container, "rid", legacy_routing_cache=True)
    cache.update(name="child", rid="child", unrelated="still keep")
    restore()
    assert cache == {"name": "parent", "unrelated": "still keep"}


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("converged", [False, True])
def test_range_polling_preserves_two_child_parent_check_without_service_rust(monkeypatch, asynchronous, converged):
    ranges = [{"id": "1", "parents": ["0"]}, {"id": "2", "parents": ["0"]}]
    if not converged:
        ranges[1]["parents"] = ["other"]
    monkeypatch.setattr(support.time, "monotonic", lambda: 1)
    container = SimpleNamespace(container_link="owned-link", client_connection=Mock())

    async def async_ranges(*args):
        for item in ranges:
            yield item

    container.client_connection._ReadPartitionKeyRanges = Mock(
        side_effect=async_ranges if asynchronous else lambda *args: iter(ranges)
    )

    def poll():
        if asynchronous:
            return asyncio.run(support.wait_for_split_ranges_async(container, "0", 0))
        return support.wait_for_split_ranges(container, "0", 0)

    if converged:
        poll()
    else:
        with pytest.raises(unittest.SkipTest, match="environment-gap: Physical split did not converge"):
            poll()
    container.client_connection._ReadPartitionKeyRanges.assert_called_once_with("owned-link")


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("timeout", [False, True])
def test_split_control_uses_one_throughput_attempt_and_bounded_polling_rust(monkeypatch, asynchronous, timeout):
    monkeypatch.setattr(support, "require_real_split", lambda: None)
    times = iter([0, support.SPLIT_TIMEOUT + 1 if timeout else 1])
    monkeypatch.setattr(support.time, "time", lambda: next(times))
    monkeypatch.setattr(support.time, "sleep", Mock())
    monkeypatch.setattr(support.asyncio, "sleep", AsyncMock())
    offers = [
        SimpleNamespace(properties={"content": {"isOfferReplacePending": True}}),
        SimpleNamespace(properties={"content": {}}),
    ]
    mock_type = AsyncMock if asynchronous else Mock
    container = SimpleNamespace(
        replace_throughput=mock_type(), get_throughput=mock_type(side_effect=offers),
    )

    def trigger():
        if asynchronous:
            return asyncio.run(support.trigger_split_async(container, 11000))
        return support.trigger_split(container, 11000)

    if timeout:
        with pytest.raises(unittest.SkipTest, match="environment-gap: Partition split"):
            trigger()
    else:
        trigger()
    container.replace_throughput.assert_called_once_with(11000)
    assert container.get_throughput.call_count == (1 if timeout else 2)


def test_post_split_failures_accumulate_without_losing_customer_assertions_rust():
    failures = []
    for stage in ("read_items_after", "change_feed_after", "logical_session_token_after", "physical_session_token_after"):
        with support.split_stage(stage, failures) as context:
            context["token_matches"] = False
            raise AssertionError(stage)
    assert [failure["stage"] for failure in failures] == [
        "read_items_after", "change_feed_after", "logical_session_token_after", "physical_session_token_after",
    ]
    with pytest.raises(AssertionError, match="Post-split checks failed:"):
        support.assert_no_stage_failures(failures)
    support.assert_no_stage_failures([])

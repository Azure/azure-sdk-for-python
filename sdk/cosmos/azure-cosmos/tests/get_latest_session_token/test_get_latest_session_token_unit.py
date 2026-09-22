# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Check local token merging without constructing clients or accessing an account."""

import ast
import asyncio
import json
from copy import deepcopy
from itertools import permutations
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from azure.cosmos import ContainerProxy
from azure.cosmos.aio import ContainerProxy as AsyncContainerProxy
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range
from azure.cosmos._session_token_helpers import get_latest_session_token, parse_session_token
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.http_constants import HttpHeaders


PACKAGE = Path(__file__).resolve().parents[2]


def _range(minimum="AA", maximum="DD"):
    return FeedRangeInternalEpk(Range(minimum, maximum, True, False)).to_dict()


def _source_function(path, name, namespace=None):
    """Load a real example/test function without running its account setup."""
    module = ast.parse(path.read_text(encoding="utf-8-sig"))
    function = next(
        node for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
    )
    scope = {} if namespace is None else namespace
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), "exec"), scope)
    return scope[name]


CASES = _source_function(PACKAGE / "tests" / "test_session_token_helpers.py", "create_split_ranges")()


def _call(async_client, pairs, target):
    proxy_type = AsyncContainerProxy if async_client else ContainerProxy
    container = proxy_type.__new__(proxy_type)
    container.client_connection = Mock()
    container._item_context = Mock()
    result = container.get_latest_session_token(pairs, target)
    if async_client:
        result = asyncio.run(result)
    assert container.client_connection.mock_calls == []
    assert container._item_context.mock_calls == []
    return result


@pytest.mark.parametrize("pairs,target,expected", CASES)
def test_split_merge_result_preserves_existing_cases_for_every_input_order(pairs, target, expected):
    original = [(_range(*bounds), token) for bounds, token in pairs]
    assert get_latest_session_token(original, _range(*target)) == expected
    for ordering in permutations(pairs):
        inputs = [(_range(*bounds), token) for bounds, token in ordering]
        before = deepcopy(inputs)
        result = get_latest_session_token(inputs, _range(*target))
        assert sorted(result.split(",")) == sorted(expected.split(","))
        assert inputs == before


@pytest.mark.parametrize("async_client", [False, True])
@pytest.mark.parametrize("pairs,target,expected", CASES)
def test_both_public_clients_merge_locally_without_connection_state(async_client, pairs, target, expected):
    inputs = [(_range(*bounds), token) for bounds, token in reversed(pairs)]
    before = deepcopy(inputs)
    actual = _call(async_client, inputs, _range(*target))
    assert sorted(actual.split(",")) == sorted(expected.split(","))
    assert inputs == before


@pytest.mark.parametrize("async_client", [False, True])
@pytest.mark.parametrize("token", [
    "", "missing-colon", ":1#2", "0:bad", "0:1#2:ignored",
    "0:1#2,", ",0:1#2", "0:1#2,,1:1#3", "0:1#2#bad",
    "0:42",
])
def test_overlapping_malformed_or_unsupported_tokens_fail_explicitly(async_client, token):
    with pytest.raises(ValueError, match="session token"):
        _call(async_client, [(_range(), token)], _range())


@pytest.mark.parametrize("async_client", [False, True])
@pytest.mark.parametrize("token", [None, 123, [], {}])
def test_non_string_tokens_raise_type_error(async_client, token):
    with pytest.raises(TypeError, match="session token"):
        _call(async_client, [(_range(), token)], _range())


@pytest.mark.parametrize("token", ["missing-colon", "0:bad", ":1#1", "0:1#2:ignored"])
def test_single_segment_parser_never_returns_an_invalid_vector(token):
    with pytest.raises(ValueError, match="session token"):
        parse_session_token(token)


@pytest.mark.parametrize("async_client", [False, True])
def test_non_overlapping_tokens_are_not_used_or_validated(async_client):
    pairs = [(_range("EE", "FF"), "unused"), (_range(), "0:1#54#3=50")]
    assert _call(async_client, pairs, _range()) == "0:1#54#3=50"


@pytest.mark.parametrize("async_client", [False, True])
@pytest.mark.parametrize("pairs", [[], [(_range("EE", "FF"), "0:1#1")]])
def test_no_overlap_remains_value_error(async_client, pairs):
    with pytest.raises(ValueError, match="There were no overlapping feed ranges with the target"):
        _call(async_client, pairs, _range())


@pytest.mark.parametrize("async_client", [False, True])
@pytest.mark.parametrize("pairs", [None, 5, "not pairs", {"Range": {}}])
def test_invalid_pair_collection_raises_type_error(async_client, pairs):
    with pytest.raises(TypeError, match="feed_ranges_to_session_tokens"):
        _call(async_client, pairs, _range())


@pytest.mark.parametrize("async_client", [False, True])
@pytest.mark.parametrize("entry", [None, "ab", (_range(),), (_range(), "0:1#2", "extra")])
def test_invalid_pair_entries_fail_explicitly(async_client, entry):
    with pytest.raises((TypeError, ValueError), match="feed_ranges_to_session_tokens"):
        _call(async_client, [entry], _range())


@pytest.mark.parametrize("async_client", [False, True])
@pytest.mark.parametrize("target", [
    {}, {"Range": {}}, {"Range": "not an object"},
    {"Range": {"min": 1, "max": "DD", "isMinInclusive": True, "isMaxInclusive": False}},
    {"Range": {"min": "AA", "max": "DD", "isMinInclusive": "true", "isMaxInclusive": False}},
    {"Range": {"min": "DD", "max": "AA", "isMinInclusive": True, "isMaxInclusive": False}},
])
def test_invalid_range_contents_raise_value_error(async_client, target):
    with pytest.raises(ValueError, match="target_feed_range"):
        _call(async_client, [(_range(), "0:1#1")], target)


@pytest.mark.parametrize("async_client", [False, True])
def test_merge_can_combine_values_instead_of_returning_one_input(async_client):
    inputs = [(_range(), "0:1#54#3=50"), (_range(), "0:1#51#3=52")]
    assert _call(async_client, inputs, _range()) == "0:1#54#3=52"


@pytest.mark.parametrize("async_client", [False, True])
def test_partial_target_coverage_does_not_require_observations_for_missing_ranges(async_client):
    assert _call(async_client, [(_range("AA", "BB"), "0:1#2")], _range()) == "0:1#2"


@pytest.mark.parametrize("async_client", [False, True])
def test_closed_point_ranges_are_accepted_and_inputs_remain_unchanged(async_client):
    target = FeedRangeInternalEpk(Range("AA", "AA", True, True)).to_dict()
    before = deepcopy(target)
    assert _call(async_client, [(target, "0:1#2")], target) == "0:1#2"
    assert target == before


@pytest.mark.parametrize("async_client", [False, True])
@pytest.mark.parametrize("value", [None, "AA", []])
def test_range_value_types_fail_explicitly(async_client, value):
    with pytest.raises(TypeError, match="target_feed_range"):
        _call(async_client, [(_range(), "0:1#2")], value)
    with pytest.raises(TypeError, match="feed_ranges_to_session_tokens"):
        _call(async_client, [(value, "0:1#2")], _range())


@pytest.mark.parametrize("async_client", [False, True])
def test_compound_tokens_merge_repeated_partition_segments(async_client):
    inputs = [(_range(), "0:1#51#3=52,1:1#53#3=50"), (_range(), "0:1#54#3=50")]
    result = _call(async_client, inputs, _range())
    assert sorted(result.split(",")) == ["0:1#54#3=52", "1:1#53#3=50"]


@pytest.mark.parametrize("async_client", [False, True])
@pytest.mark.parametrize("enabled,expected", [("true", "0:2#5#3=99"), ("false", "0:2#100#3=99")])
def test_existing_different_version_merge_setting_is_preserved(async_client, enabled, expected, monkeypatch):
    monkeypatch.setenv("AZURE_COSMOS_SESSION_TOKEN_FALSE_PROGRESS_MERGE", enabled)
    inputs = [(_range(), "0:1#100#3=99"), (_range(), "0:2#5#3=3")]
    assert _call(async_client, inputs, _range()) == expected


@pytest.mark.parametrize("async_client", [False, True])
def test_incompatible_same_version_regions_preserve_local_merge_error(async_client):
    inputs = [(_range(), "0:1#2#3=1"), (_range(), "0:1#3#4=2")]
    with pytest.raises(CosmosHttpResponseError, match="unexpected regions") as caught:
        _call(async_client, inputs, _range())
    assert caught.value.status_code == 500


@pytest.mark.parametrize("async_client", [False, True])
def test_sample_updates_the_target_cache_key_not_the_last_cached_range(async_client):
    proxy_type = AsyncContainerProxy if async_client else ContainerProxy
    proxy = proxy_type.__new__(proxy_type)
    target, other = _range("AA", "BB"), _range("CC", "DD")
    target_key, other_key = json.dumps(target), json.dumps(other)
    cache = {target_key: "0:1#1", other_key: "1:1#1"}
    response = SimpleNamespace(get_response_headers=lambda: {HttpHeaders.SessionToken: "0:1#2"})
    create = (AsyncMock if async_client else Mock)(return_value=response)
    container = SimpleNamespace(
        create_item=create, get_latest_session_token=proxy.get_latest_session_token,
    )
    sample = PACKAGE / "samples" / (
        "session_token_management_async.py" if async_client else "session_token_management.py"
    )
    function = _source_function(
        sample, "perform_create_item_with_cached_session_token",
        {"json": json, "HttpHeaders": HttpHeaders},
    )
    call = function(cache, container, [], {"id": "order-42", "pk": "customer-42"}, target)
    if async_client:
        asyncio.run(call)
    assert cache == {target_key: "0:1#2", other_key: "1:1#1"}

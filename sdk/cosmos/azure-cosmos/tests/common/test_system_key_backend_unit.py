# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""System-key metadata and cache consistency through real dispatch with fake I/O."""

import asyncio
import copy
import inspect
import json
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import pytest

from azure.cosmos._backend._fallback_metrics import rust_compatibility_fallback_count
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos.container import ContainerProxy
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.cosmos.partition_key import NonePartitionKeyValue, _Empty, _Undefined
from .test_delete_container_backend_unit import delete_case
from .test_read_container_backend_unit import read_case


@pytest.fixture
def system_case(read_case):
    case = read_case
    case.connection._container_properties_cache = {}
    case.connection._set_container_properties_cache.side_effect = lambda link, properties: case.connection._container_properties_cache.__setitem__(
        link, properties
    )
    before = rust_compatibility_fallback_count()
    yield case
    assert rust_compatibility_fallback_count() == before


def _resolve(value):
    return asyncio.run(value) if inspect.isawaitable(value) else value


def _set_flag(case, flag):
    if flag == "absent":
        case.properties["partitionKey"].pop("systemKey", None)
    else:
        case.properties["partitionKey"]["systemKey"] = flag
    case.backend.response = replace(
        case.backend.response, body=json.dumps(case.properties).encode()
    )


def _assert_reads(case, count):
    assert case.backend.execute.call_count == (0 if case.legacy else count)
    assert case.connection.ReadContainer.call_count == (count if case.legacy else 0)


def test_access_forms_remain_properties():
    assert isinstance(ContainerProxy.is_system_key, property)
    assert isinstance(AsyncContainerProxy.is_system_key, property)
    assert not inspect.iscoroutinefunction(ContainerProxy.is_system_key.fget)
    assert inspect.iscoroutinefunction(AsyncContainerProxy.is_system_key.fget)
    assert inspect.signature(ContainerProxy.is_system_key.fget) == inspect.signature(
        AsyncContainerProxy.is_system_key.fget
    )


@pytest.mark.parametrize("flag", [True, False, "absent"])
@pytest.mark.parametrize("warm", [True, False])
def test_values_and_repeated_access(system_case, flag, warm):
    case = system_case
    _set_flag(case, flag)
    if warm:
        case.connection._container_properties_cache[case.container.container_link] = (
            copy.deepcopy(case.properties)
        )
    assert _resolve(case.container.is_system_key) is (flag is True)
    assert _resolve(case.container.is_system_key) is (flag is True)
    _assert_reads(case, 0 if warm else 1)


@pytest.mark.parametrize(
    "before,after", [(True, False), (False, True), (True, "absent")]
)
@pytest.mark.parametrize(
    "other_proxy", [False, True], ids=["same-proxy", "shared-cache"]
)
def test_metadata_refresh_updates_property(system_case, before, after, other_proxy):
    case = system_case
    _set_flag(case, before)
    assert _resolve(case.container.is_system_key) is before

    case.properties["_rid"] = "replacement-rid"
    _set_flag(case, after)
    reader = case.database.get_container_client("c1") if other_proxy else case.container
    refreshed = _resolve(reader.read())
    assert refreshed["_rid"] == "replacement-rid"
    assert refreshed["partitionKey"].get("systemKey", False) is (after is True)
    assert _resolve(case.container.is_system_key) is (after is True)
    assert _resolve(case.container.is_system_key) is (after is True)
    _assert_reads(case, 2)


def test_cache_invalidation_causes_a_new_read(system_case):
    case = system_case
    _set_flag(case, True)
    assert _resolve(case.container.is_system_key) is True
    case.connection._container_properties_cache.clear()
    _set_flag(case, False)
    assert _resolve(case.container.is_system_key) is False
    _assert_reads(case, 2)


@pytest.mark.parametrize("invalidate", [False, True], ids=["cold", "invalidated"])
@pytest.mark.parametrize("error_type", [CosmosResourceNotFoundError, RuntimeError])
def test_read_failure_propagates_without_inventing_a_value(
    system_case, invalidate, error_type
):
    case = system_case
    if invalidate:
        _set_flag(case, True)
        assert _resolve(case.container.is_system_key) is True
        case.connection._container_properties_cache.clear()

    selected = case.connection.ReadContainer if case.legacy else case.backend.execute
    original_side_effect = selected.side_effect
    error = (
        error_type(status_code=404, message="missing")
        if error_type is CosmosResourceNotFoundError
        else error_type("failed")
    )
    selected.side_effect = error
    with pytest.raises(error_type) as raised:
        _resolve(case.container.is_system_key)
    assert raised.value is error
    assert case.connection._container_properties_cache == {}

    selected.side_effect = original_side_effect
    _set_flag(case, False)
    assert _resolve(case.container.is_system_key) is False
    _assert_reads(case, 3 if invalidate else 2)


def test_constructor_properties_are_used_without_a_read(system_case):
    case = system_case
    _set_flag(case, True)
    proxy = type(case.container)(
        case.connection, "dbs/db1", "c1", properties=copy.deepcopy(case.properties)
    )
    assert _resolve(proxy.is_system_key) is True
    _assert_reads(case, 0)


@pytest.mark.parametrize(
    "flag,expected", [(True, _Empty), (False, _Undefined), ("absent", _Undefined)]
)
def test_legacy_partition_marker_uses_current_metadata(system_case, flag, expected):
    case = system_case
    _set_flag(case, not (flag is True))
    _resolve(case.container.is_system_key)
    _set_flag(case, flag)
    _resolve(case.container.read())
    assert isinstance(
        _resolve(case.container._set_partition_key(NonePartitionKeyValue)), expected
    )
    _assert_reads(case, 2)


def test_concurrent_access_reuses_metadata(system_case, monkeypatch):
    case = system_case
    _set_flag(case, False)
    original_read = case.container.read
    if case.is_async:

        async def delayed_read():
            await asyncio.sleep(0)
            return await original_read()

        monkeypatch.setattr(case.container, "read", delayed_read)

        async def read_together():
            return await asyncio.gather(
                *(case.container.is_system_key for _ in range(8))
            )

        values = asyncio.run(read_together())
    else:

        def delayed_read():
            time.sleep(0.01)
            return original_read()

        monkeypatch.setattr(case.container, "read", delayed_read)
        with ThreadPoolExecutor(max_workers=8) as pool:
            values = list(pool.map(lambda _: case.container.is_system_key, range(8)))
    assert values == [False] * 8
    _assert_reads(case, 1)

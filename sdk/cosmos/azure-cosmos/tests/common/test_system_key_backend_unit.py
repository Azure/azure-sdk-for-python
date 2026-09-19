# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Unit coverage for the container property saying whether its partition key is managed by
the service, and for the cached metadata that answer comes from.

Some containers have a partition key the service maintains rather than the customer. Two
things depend on knowing which: how a request asking for "no partition key" is expressed,
and therefore which items a call reaches.

The answer lives in the container's metadata, which is fetched once and cached. Most of
this file is about that cache being right at the moments it is easy to get wrong -- after
the container is changed, after the cache is emptied, when the fetch fails, and when
several callers ask at the same time.

Every test runs against both the Rust path and the old one, and each checks how many
reads actually happened. A wrong answer here is never an error; it is a request quietly
scoped differently from what the caller intended.
"""

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
    """Set up a container read with a working cache, and check no call took the old path.

    The shared setup for reading a container is reused, with the metadata cache made to
    actually store what is written to it so caching behavior can be observed at all.

    The count of calls that quietly fell back to the old Python path is taken before and
    compared after. Every test here is meant to run on the path it was given; a silent
    fallback would make the read counts meaningless and would otherwise go unnoticed.
    """
    case = read_case
    case.connection._container_properties_cache = {}
    case.connection._set_container_properties_cache.side_effect = lambda link, properties: case.connection._container_properties_cache.__setitem__(
        link, properties
    )
    before = rust_compatibility_fallback_count()
    yield case
    assert rust_compatibility_fallback_count() == before


def _resolve(value):
    """Get the value whether the path under test returned it directly or needs awaiting.

    Lets one test body serve both the synchronous and asynchronous container, which is
    the point: the two must agree, and writing the test twice invites them to drift.
    """
    return asyncio.run(value) if inspect.isawaitable(value) else value


def _set_flag(case, flag):
    """Set what the service will say about this container: managed, not managed, or silent.

    The third case is not the same as saying no. Older containers simply do not mention
    it, and code that treated a missing answer as a present one would get it wrong for
    every container made before the setting existed.

    The stored reply is updated too, so the next read returns this.
    """
    if flag == "absent":
        case.properties["partitionKey"].pop("systemKey", None)
    else:
        case.properties["partitionKey"]["systemKey"] = flag
    case.backend.response = replace(
        case.backend.response, body=json.dumps(case.properties).encode()
    )


def _assert_reads(case, count):
    """Check the container was read exactly this many times, on whichever path is in use.

    The two paths count in different places, so the check looks at the one in use and
    requires the other to be untouched. That second half is what catches a call going
    somewhere it should not.
    """
    assert case.backend.execute.call_count == (0 if case.legacy else count)
    assert case.connection.ReadContainer.call_count == (count if case.legacy else 0)


def test_access_forms_remain_properties():
    """It is a property on both containers, awaited on one and not the other, same arguments.

    Being a property matters because it is how customers already use it. That it may
    quietly perform a read behind the scenes does not change the way it is written.

    The asynchronous one must be awaited, since it can fetch metadata; the synchronous one
    must not be. Their signatures are compared directly, so the two cannot drift into
    taking different arguments.
    """
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
    """Each of the three answers reads true or false correctly, and asking twice reads once.

    Only an explicit yes counts as yes; both no and silence mean no. Asking a second time
    must not read again, because this is a property and customers will read it in a loop
    without thinking about it.

    With the cache already filled, no read happens at all. That is the case that matters
    for a container fetched a moment earlier, which is most of them.
    """
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
    """Re-reading the container updates the answer, including through a different handle.

    The container is replaced by one with a different setting -- the identifier changes
    too, which is what a deleted and recreated container looks like. Reading it again
    must give the new answer, not the remembered one.

    The second case is the sharper one: the refresh is done through a separate handle to
    the same container. The cache belongs to the connection rather than the handle, so
    the first handle must see the change as well. Otherwise two handles in one program
    would disagree about the same container, and which one a caller held would decide
    what their request meant.
    """
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
    """Emptying the cache makes the next read go to the service again and pick up a change.

    Something else may clear the cache -- a refresh elsewhere, an error path. When that
    happens the remembered answer must be gone, not merely stale, so the setting is read
    fresh and the new value is seen. Two reads in total: one before, one after.
    """
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
    """When the read fails the error reaches the caller and nothing is remembered.

    The tempting mistake is to answer no on failure, since no is the common case. That
    would be worse than the error: it silently changes which items a later request
    reaches, and the caller never learns the setting was never actually known.

    The original error object itself must arrive, not a copy or a wrapper, so the caller
    can catch it by type and read its status. Both a missing container and an unexpected
    failure are covered.

    The cache is checked to be empty afterwards, and a later successful read is checked to
    work, which shows the failure left nothing behind. Started either from cold or from a
    cache that had been filled and then emptied, because a failure after a success is the
    likelier way this happens.
    """
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
    """A container built with its properties already in hand answers without any read.

    Callers who already hold the properties -- from listing containers, say -- pass them
    in. Reading the container again would waste a round trip per handle, and in a program
    that makes many handles that adds up quickly. Zero reads is the whole point.
    """
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
    """Asking for "no partition key" produces the marker that matches the latest metadata.

    A managed partition key gives one marker and an ordinary one gives another, and
    silence is treated as ordinary. The two markers mean different things on the wire, so
    picking the wrong one sends the request to the wrong place.

    The opposite setting is read first and remembered, then the container is changed and
    re-read. The marker has to follow the fresh metadata rather than the answer cached a
    moment earlier, which is the failure this is here to catch.
    """
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
    """Eight callers asking at once cause one read between them, not eight.

    The read is slowed down on purpose so every caller arrives while it is still running.
    Without coordination each would start its own, which is a burst of identical requests
    every time a program first touches a container from several threads or tasks.

    All eight must get the same answer, and exactly one read must reach the service. Run
    with real threads on one side and with tasks gathered together on the other, since the
    two use different machinery to hold callers back and both have to work.
    """
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

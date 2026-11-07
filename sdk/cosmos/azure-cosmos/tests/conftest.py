# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import sys

import pytest

from config import clients, collection, resources

cosmos_sync_client = None
_live_resources_initialized = False


def pytest_addoption(parser):
    parser.getgroup("cosmos").addoption(
        "--include-legacy-tests",
        action="store_true",
        default=False,
        help="Include preserved legacy tests and paired comparisons for local migration work.",
    )


def pytest_ignore_collect(collection_path, config):
    if not config.option.include_legacy_tests and collection.exclude_module(collection_path):
        return True
    return None


@pytest.hookimpl(tryfirst=True)
def pytest_pycollect_makemodule(module_path, parent):
    # Explicit file/node arguments bypass pytest_ignore_collect.
    if not parent.config.option.include_legacy_tests and collection.exclude_module(module_path):
        raise pytest.UsageError(
            f"{module_path.name} is excluded from normal runs. "
            "Use --include-legacy-tests with a specific path for local migration work."
        )
    return None


@pytest.hookimpl(tryfirst=True)
def pytest_pycollect_makeitem(collector, name, obj):
    if collector.config.option.include_legacy_tests:
        return None
    if collection.exclude_test(collector.path, name):
        return []
    # Importing an original class for helpers must not collect its tests again.
    source_module = sys.modules.get(getattr(obj, "__module__", None))
    source_path = getattr(source_module, "__file__", None)
    if source_path and collection.exclude_test(source_path, getattr(obj, "__name__", name)):
        return []
    return None


def pytest_collection_modifyitems(config, items):
    if config.option.include_legacy_tests:
        return
    excluded = [
        item for item in items
        if collection.exclude_parameters(item.path, getattr(getattr(item, "callspec", None), "params", {}))
    ]
    if excluded:
        excluded_set = set(excluded)
        items[:] = [item for item in items if item not in excluded_set]
        config.hook.pytest_deselected(items=excluded)


@pytest.fixture
def credential_owner_loop():
    """Provide a caller-owned running loop for blocking bridge unit tests."""
    import asyncio
    import threading

    loop = asyncio.new_event_loop()
    started = threading.Event()

    def run():
        asyncio.set_event_loop(loop)
        loop.call_soon(started.set)
        try:
            loop.run_forever()
        finally:
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.run_until_complete(loop.shutdown_asyncgens())
            asyncio.set_event_loop(None)
            loop.close()

    thread = threading.Thread(target=run, name="test-credential-owner", daemon=True)
    thread.start()
    try:
        assert started.wait(5), "credential owner loop did not start"
        yield loop
    finally:
        if loop.is_running():
            loop.call_soon_threadsafe(loop.stop)
        thread.join(5)
        assert not thread.is_alive(), "credential owner loop did not stop"


def _get_setup_client():
    """Build the shared setup client the first time something actually needs it.

    Creating a client used to happen when this file was imported, which meant
    every test run tried to reach a Cosmos account -- including runs of the
    unit tests, which do not talk to a service at all and would just hang when
    no account was reachable. Building it on demand keeps those runs offline.
    """
    global cosmos_sync_client  # pylint: disable=global-statement
    if cosmos_sync_client is None:
        cosmos_sync_client = clients.create_setup_client()
    return cosmos_sync_client


def _initialize_legacy_account_info(session):
    """Keep the unsupported account lookup out of maintained Rust-only runs."""
    if not getattr(session.config.option, "include_legacy_tests", False):
        return
    legacy = sys.modules.get("test_config")
    if legacy is None:
        return
    for item in session.items:
        module = getattr(item, "module", None)
        if (
            getattr(module, "test_config", None) is legacy
            or getattr(module, "TestConfig", None) is legacy.TestConfig
        ):
            legacy.initialize_legacy_account_info()
            return


def pytest_collection_finish(session):
    """Create the shared databases and containers only if the run needs them.

    Runs after pytest has worked out which tests it is about to run. If every
    one of them is a unit test (files named ``*_unit.py``), there is nothing to
    set up and no account to reach, so this returns immediately. That is what
    lets the routing tests for ``list_databases`` and the other operations run
    with no Cosmos account and no emulator.
    Do not provision for collection-only or aborted runs. An explicit request
    to continue after collection errors still needs setup for runnable tests.
    """
    if (
        session.config.option.collectonly
        or (session.testsfailed and not session.config.option.continue_on_collection_errors)
        or not session.items
        or all(item.path.name.endswith("_unit.py") for item in session.items)
    ):
        return

    global _live_resources_initialized  # pylint: disable=global-statement
    _initialize_legacy_account_info(session)
    client = _get_setup_client()
    resources.create_database_if_not_exist(client)
    # Track ownership before container setup, so partial setup is also cleaned up.
    _live_resources_initialized = True
    resources.create_single_partition_container_if_not_exist(client)
    resources.create_multi_partition_container_if_not_exist(client)
    resources.create_single_partition_prefix_pk_container_if_not_exist(client)
    resources.create_multi_partition_prefix_pk_container_if_not_exist(client)


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """
    global _live_resources_initialized  # pylint: disable=global-statement
    try:
        if _live_resources_initialized:
            resources.try_delete_database(cosmos_sync_client)
    finally:
        _live_resources_initialized = False
        _close_setup_client()


def _close_setup_client():
    global cosmos_sync_client  # pylint: disable=global-statement
    client, cosmos_sync_client = cosmos_sync_client, None
    if client is not None:
        client.close()


def pytest_unconfigure(config):
    """Close a client even when pytest exits before session cleanup."""
    _close_setup_client()



@pytest.fixture(autouse=True)
def _reset_shared_pk_range_cache():
    """Reset module-level shared partition-key-range cache between tests.

    The shared cache (introduced for the cross-client memory optimisation)
    is process-global state. Without this fixture, state from one test
    (cached routing maps, per-(loop, collection) locks, refcounts) leaks
    into subsequent tests, causing order-dependent failures and flakiness
    in any test that asserts on cache contents or _ReadPartitionKeyRanges
    call counts.

    We clear after the test runs so the test under observation can still
    exercise the normal population behaviour.
    """
    yield
    # Clear the *contents* of each per-endpoint cache dict, not the registry
    # itself. Long-lived test fixtures (class-level CosmosClient) hold strong
    # references to the inner dicts via ``_collection_routing_map_by_item``;
    # if we ``.clear()`` the outer registry, a freshly-constructed client for
    # the same endpoint creates a brand-new inner dict and the dict-identity
    # invariant that test_shared_cache_integration relies on is broken.
    # Same reasoning for ``_shared_collection_locks``.
    # Temporary compatibility: never import retired routing code just for cleanup.
    for name in (
        "azure.cosmos._routing.routing_map_provider",
        "azure.cosmos._routing.aio.routing_map_provider",
    ):
        pmp = sys.modules.get(name)
        if pmp is None:
            continue
        with pmp._shared_cache_lock:  # pylint: disable=protected-access
            for cache in pmp._shared_routing_map_cache.values():  # pylint: disable=protected-access
                cache.clear()
            for locks in pmp._shared_collection_locks.values():  # pylint: disable=protected-access
                locks.clear()

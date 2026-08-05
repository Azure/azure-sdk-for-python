# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import pytest
import test_config
from azure.cosmos import CosmosClient as CosmosSyncClient
from azure.cosmos._backend.constants import BACKEND_NAME_CORE_PYTHON

# Register the in-repo parity-capture pytest plugin. The plugin
# itself is dormant unless the env var COSMOS_PARITY_CAPTURE_OP is
# set to a known operation name. Listed here so pytest auto-loads it
# for every test run without requiring contributors to install
# anything.
pytest_plugins = ["common.parity_capture_plugin"]

cosmos_sync_client = None
_live_resources_initialized = False


def _get_setup_client():
    """Build the shared setup client the first time something actually needs it.

    Creating a client used to happen when this file was imported, which meant
    every test run tried to reach a Cosmos account -- including runs of the
    unit tests, which do not talk to a service at all and would just hang when
    no account was reachable. Building it on demand keeps those runs offline.
    """
    global cosmos_sync_client  # pylint: disable=global-statement
    if cosmos_sync_client is None:
        # Shared test-data setup must remain on core Python because it reads
        # account metadata before Rust-specific tests choose their own backend.
        cosmos_sync_client = CosmosSyncClient(
            test_config.TestConfig.host,
            test_config.TestConfig.masterKey,
            _backend=BACKEND_NAME_CORE_PYTHON,
        )
    return cosmos_sync_client


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """


def pytest_collection_finish(session):
    """Create the shared databases and containers only if the run needs them.

    Runs after pytest has worked out which tests it is about to run. If every
    one of them is a unit test (files named ``*_unit.py``), there is nothing to
    set up and no account to reach, so this returns immediately. That is what
    lets the routing tests for ``list_databases`` and the other operations run
    with no Cosmos account and no emulator.
    """
    if not session.items or all(item.path.name.endswith("_unit.py") for item in session.items):
        return

    global _live_resources_initialized  # pylint: disable=global-statement
    client = _get_setup_client()
    config = test_config.TestConfig
    config.get_account_info(client)
    config.create_database_if_not_exist(client)
    config.create_single_partition_container_if_not_exist(client)
    config.create_multi_partition_container_if_not_exist(client)
    config.create_single_partition_prefix_pk_container_if_not_exist(client)
    config.create_multi_partition_prefix_pk_container_if_not_exist(client)
    _live_resources_initialized = True


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """
    if _live_resources_initialized:
        test_config.TestConfig.try_delete_database(cosmos_sync_client)


def pytest_unconfigure(config):
    """
    called before test process is exited.
    """



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
    # Local import to avoid pulling these modules in at conftest collection
    # time (some environments treat conftest import errors as fatal).
    from azure.cosmos._routing import routing_map_provider as _sync_pmp
    from azure.cosmos._routing.aio import routing_map_provider as _async_pmp

    # Clear the *contents* of each per-endpoint cache dict, not the registry
    # itself. Long-lived test fixtures (class-level CosmosClient) hold strong
    # references to the inner dicts via ``_collection_routing_map_by_item``;
    # if we ``.clear()`` the outer registry, a freshly-constructed client for
    # the same endpoint creates a brand-new inner dict and the dict-identity
    # invariant that test_shared_cache_integration relies on is broken.
    # Same reasoning for ``_shared_collection_locks``.
    for pmp in (_sync_pmp, _async_pmp):
        with pmp._shared_cache_lock:  # pylint: disable=protected-access
            for cache in pmp._shared_routing_map_cache.values():  # pylint: disable=protected-access
                cache.clear()
            for locks in pmp._shared_collection_locks.values():  # pylint: disable=protected-access
                locks.clear()

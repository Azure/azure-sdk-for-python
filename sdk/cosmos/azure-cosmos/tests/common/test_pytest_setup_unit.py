# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit coverage for the rule that a test run only creates live Azure resources when it
is actually going to use them.

Before any test runs, the shared setup can create a database and several containers in a
real Cosmos account. That is needed for the tests that talk to a service, and pure waste
for the ones that do not: it costs money, it needs credentials, and it means a developer
with no account cannot run the offline tests at all.

The rule is that setup is skipped when the run is only listing tests, when it has already
given up, when it collected nothing, or when everything collected is an offline unit test.
This file checks each of those, and checks that a run which does need resources still
gets them, in the right order.
"""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


@pytest.fixture
def setup_module_under_test():
    """Load the shared setup file as a module so its hook can be called directly.

    It is loaded from its path rather than imported by name because pytest has already
    loaded it as the run's own configuration. Loading a fresh copy means this test can
    replace pieces of it and read its state without disturbing the run in progress.
    """
    path = Path(__file__).resolve().parents[1] / "conftest.py"
    spec = importlib.util.spec_from_file_location("_cosmos_setup_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _session(collect_only=False, failures=0, names=("test_crud.py",), continue_on_errors=False):
    """Build a stand-in for a pytest run, holding only the four things the hook reads.

    The default is a run that does need resources: nothing has failed, it is not just
    listing, and the one file collected is not an offline unit test. Each test varies one
    thing from there.
    """
    return SimpleNamespace(
        config=SimpleNamespace(option=SimpleNamespace(
            collectonly=collect_only, continue_on_collection_errors=continue_on_errors,
        )),
        testsfailed=failures,
        items=[SimpleNamespace(path=Path(name)) for name in names],
    )


@pytest.mark.parametrize(
    "session",
    [
        _session(collect_only=True),
        _session(failures=1),
        _session(names=()),
        _session(names=("test_fault_rules_unit.py", "test_known_failures_check_unit.py")),
    ],
)
def test_nonexecuting_runs_do_not_create_live_resources(setup_module_under_test, monkeypatch, session):
    """Four kinds of run that must not touch an account: each is checked here.

    Listing tests without running them, a run that has already given up, a run that
    collected nothing, and a run where everything collected is an offline unit test. The
    last is the one developers feel every day -- it is what lets the whole offline suite
    run with no account and no emulator.

    The function that would fetch a client is replaced with one that fails the test if it
    is called at all, so this proves nothing was attempted rather than that nothing
    succeeded. The flag is checked afterwards so a later run is not told setup is done.
    """
    setup = Mock(side_effect=AssertionError("must not contact a Cosmos account"))
    monkeypatch.setattr(setup_module_under_test, "_get_setup_client", setup)
    setup_module_under_test.pytest_collection_finish(session)
    setup.assert_not_called()
    assert not setup_module_under_test._live_resources_initialized


@pytest.mark.parametrize("session", [_session(), _session(failures=1, continue_on_errors=True)])
def test_live_run_still_creates_shared_resources(setup_module_under_test, monkeypatch, session):
    """A run that needs resources gets all six, in order, from one client.

    The order matters: the account is asked about itself first, then the database is made,
    then the containers that live inside it. Every call has to use the same client, since
    a second one would mean a second connection to the same account.

    The second case is the exception to the rule above. A run that hit collection errors
    normally stops, but if the developer explicitly asked to carry on, the tests that can
    still run need their resources.
    """
    client = object()
    config = Mock()
    monkeypatch.setattr(setup_module_under_test, "_get_setup_client", lambda: client)
    monkeypatch.setattr(setup_module_under_test.test_config, "TestConfig", config)
    setup_module_under_test.pytest_collection_finish(session)
    assert [call[0] for call in config.method_calls] == [
        "get_account_info",
        "create_database_if_not_exist",
        "create_single_partition_container_if_not_exist",
        "create_multi_partition_container_if_not_exist",
        "create_single_partition_prefix_pk_container_if_not_exist",
        "create_multi_partition_prefix_pk_container_if_not_exist",
    ]
    assert all(call.args == (client,) for call in config.method_calls)
    assert setup_module_under_test._live_resources_initialized

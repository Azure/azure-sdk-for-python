# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import base64
import io
import os
import subprocess
import sys
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, call

import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.edgeactions import models
from devtools_testutils import RandomNameResourceGroupPreparer

from edgeactions_test_settings import RESOURCE_GROUP_OPTIONS
from test_edge_actions_mgmt_client_lifecycle_test import (
    HANDLER,
    TestEdgeActionsLifecycle as LifecycleScenarios,
    cleanup_edge_action,
    pytestmark as lifecycle_marks,
    version_code,
)


def test_package_collection_handles_multiple_conftest_files():
    env = os.environ.copy()
    env["AZURE_TEST_RUN_LIVE"] = "false"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "test_edge_actions_mgmt_client_lifecycle_test.py::TestEdgeActionsLifecycle" in result.stdout


def test_resource_group_prefix_is_applied_once(monkeypatch):
    monkeypatch.delenv("AZURE_RESOURCEGROUP_NAME", raising=False)
    preparer = RandomNameResourceGroupPreparer(**RESOURCE_GROUP_OPTIONS)
    name = preparer._prefix_name(preparer.random_name)
    assert name.startswith("rgpy-pythonsdk-edgeaction-test-")
    assert len(name) == 45
    assert preparer.moniker == "pythonsdk-edgeaction-test-rgname"


def test_lifecycle_supports_playback_without_source_edits():
    marks = lifecycle_marks if isinstance(lifecycle_marks, (list, tuple)) else [lifecycle_marks]
    assert all(mark.name != "live_test_only" for mark in marks)
    assert any(mark.name == "usefixtures" and "add_sanitizers" in mark.args for mark in marks)


def test_action_names_are_repeatable_and_distinct_between_scenarios(monkeypatch):
    scenario = LifecycleScenarios()
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "edgeactions::tag_updates (call)")
    name = scenario.get_resource_name("eapython")
    assert name.startswith("eapython")
    assert name != "eapython"
    assert scenario.get_resource_name("eapython") == name

    monkeypatch.setenv("PYTEST_CURRENT_TEST", "edgeactions::file_versions (call)")
    assert scenario.get_resource_name("eapython") != name


@pytest.mark.parametrize("deployment_type", ["file", "zip"])
def test_version_code_is_replayable(deployment_type):
    encoded = version_code(deployment_type)
    assert encoded == version_code(deployment_type)
    decoded = base64.b64decode(encoded)
    if deployment_type == "zip":
        with zipfile.ZipFile(io.BytesIO(decoded)) as archive:
            assert archive.namelist() == ["handler.js"]
            assert archive.read("handler.js") == HANDLER
            assert archive.getinfo("handler.js").date_time == (1980, 1, 1, 0, 0, 0)
    else:
        assert decoded == HANDLER


def make_version(name, is_default):
    return models.EdgeActionVersion(
        {"name": name, "location": "global", "properties": {"deploymentType": "file", "isDefaultVersion": is_default}}
    )


@pytest.mark.parametrize("default_name", ["v1", "v2"])
def test_cleanup_uses_current_default_and_deletes_parent_last(default_name):
    client = Mock()
    client.edge_action_execution_filters.list_by_edge_action.return_value = [
        models.EdgeActionExecutionFilter({"name": "filter", "location": "global"})
    ]
    client.edge_action_versions.list_by_edge_action.return_value = [
        make_version(name, "True" if name == default_name else "False") for name in ("v1", "v2")
    ]
    cleanup_edge_action(client, "rg", "action")
    non_default = "v2" if default_name == "v1" else "v1"
    deletes = [item for item in client.mock_calls if item[0].endswith("begin_delete")]
    assert deletes == [
        call.edge_action_execution_filters.begin_delete("rg", "action", "filter"),
        call.edge_action_versions.begin_delete("rg", "action", non_default),
        call.edge_action_versions.begin_delete("rg", "action", default_name),
        call.edge_actions.begin_delete("rg", "action"),
    ]
    assert client.mock_calls[-1] == call.edge_actions.begin_delete().result()


@pytest.mark.parametrize("states", [("True", "True"), ("True", None)])
def test_cleanup_rejects_ambiguous_default_state(states):
    client = Mock()
    client.edge_action_execution_filters.list_by_edge_action.return_value = []
    client.edge_action_versions.list_by_edge_action.return_value = [
        make_version(f"v{index}", state) for index, state in enumerate(states)
    ]
    with pytest.raises(AssertionError):
        cleanup_edge_action(client, "rg", "action")
    client.edge_action_versions.begin_delete.assert_not_called()
    client.edge_actions.begin_delete.assert_not_called()


def test_existing_action_is_not_overwritten(monkeypatch):
    scenario = LifecycleScenarios()
    client = MagicMock()
    client.__enter__.return_value = client
    monkeypatch.setattr(scenario, "create_mgmt_client", Mock(return_value=client))
    monkeypatch.setattr(scenario, "get_resource_name", Mock(return_value="existing"))
    with pytest.raises(pytest.fail.Exception, match="Refusing to overwrite existing EdgeAction"):
        with scenario.edge_action("rg"):
            pytest.fail("An existing resource must not be yielded to the scenario")
    client.edge_actions.begin_create.assert_not_called()
    client.edge_actions.begin_delete.assert_not_called()


@pytest.mark.parametrize("failure_during_create", [False, True], ids=["scenario-failure", "create-failure"])
def test_failure_still_cleans_owned_action(monkeypatch, failure_during_create):
    scenario = LifecycleScenarios()
    client = MagicMock()
    client.__enter__.return_value = client
    client.edge_actions.get.side_effect = [ResourceNotFoundError("Not found"), models.EdgeAction(location="global")]
    if failure_during_create:
        client.edge_actions.begin_create.return_value.result.side_effect = ValueError("Scenario failure")
    client.edge_action_execution_filters.list_by_edge_action.return_value = []
    client.edge_action_versions.list_by_edge_action.return_value = []
    monkeypatch.setattr(scenario, "create_mgmt_client", Mock(return_value=client))
    monkeypatch.setattr(scenario, "get_resource_name", Mock(return_value="owned"))
    with pytest.raises(ValueError, match="Scenario failure"):
        with scenario.edge_action("rg"):
            raise ValueError("Scenario failure")
    client.edge_actions.begin_delete.assert_called_once_with("rg", "owned")
    client.edge_actions.begin_delete.return_value.result.assert_called_once_with()


def test_cleanup_of_absent_action_does_not_delete_resources():
    client = Mock()
    client.edge_actions.get.side_effect = ResourceNotFoundError("Not found")
    cleanup_edge_action(client, "rg", "absent")
    client.edge_action_execution_filters.list_by_edge_action.assert_not_called()
    client.edge_action_versions.list_by_edge_action.assert_not_called()
    client.edge_actions.begin_delete.assert_not_called()

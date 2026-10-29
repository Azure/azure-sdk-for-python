# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import pytest
from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError

import _execution_prerequisites as setup

SUBSCRIPTION = "00000000-0000-0000-0000-000000000000"
NAME = "pyexecowned"
GROUP = "owned-parent"
CV_ID = (
    f"/subscriptions/{SUBSCRIPTION}/resourceGroups/{GROUP}"
    f"/providers/Microsoft.PlatformValidation/cloudValidations/{NAME}"
)


def not_found(status=404):
    error = ResourceNotFoundError(message="Not found")
    error.status_code = status
    return error


def poller(result=None):
    operation = Mock()
    operation.result.return_value = result
    operation.done.return_value = True
    return operation


@pytest.fixture
def prerequisites(monkeypatch):
    monkeypatch.setattr(setup, "add_general_string_sanitizer", Mock())
    monkeypatch.setattr(setup, "wait_for_managed_group_deletion", Mock())
    monkeypatch.setattr(setup.time, "sleep", Mock())
    preparer = setup.ExecutionPrerequisitesPreparer()
    preparer.test_class_instance = Mock(is_live=True)
    preparer.test_class_instance.get_settings_value.return_value = SUBSCRIPTION
    resources, cv = MagicMock(), MagicMock()
    clients = {
        setup.ResourceManagementClient: resources,
        setup.PlatformValidationMgmtClient: cv,
    }
    for client in clients.values():
        client.__enter__.return_value = client
    preparer.create_mgmt_client = Mock(side_effect=lambda client_type: clients[client_type])
    resources.resource_groups.check_existence.side_effect = [False, True]
    resources.resource_groups.get.return_value = SimpleNamespace(managed_by=CV_ID)
    cv.cloud_validations.get.side_effect = not_found()
    cv.cloud_validations.begin_create_or_update.return_value = poller(
        SimpleNamespace(properties=SimpleNamespace(provisioning_state="Succeeded"))
    )
    arguments = {
        "resource_group": SimpleNamespace(name=GROUP),
        "platformvalidation_location": "eastus",
    }
    return preparer, resources, cv, arguments


def test_setup_verifies_service_managed_group_without_creating_it(prerequisites):
    preparer, resources, cv, arguments = prerequisites
    assert preparer.create_resource(NAME, **arguments) == {"cloud_validation_name": NAME}
    cv.cloud_validations.begin_create_or_update.assert_called_once()
    resources.resource_groups.create_or_update.assert_not_called()
    resources.resource_groups.get.assert_called_once_with(f"{NAME}-mrg")
    assert {call.args[0] for call in preparer.create_mgmt_client.call_args_list} == {
        setup.ResourceManagementClient,
        setup.PlatformValidationMgmtClient,
    }


def test_service_mode_never_falls_back_to_manual(prerequisites):
    preparer, resources, _, arguments = prerequisites
    resources.resource_groups.check_existence.side_effect = [False, False]
    preparer._cleanup = Mock()
    with pytest.raises(AssertionError, match="no fallback"):
        preparer.create_resource(NAME, **arguments)
    resources.resource_groups.create_or_update.assert_not_called()
    preparer._cleanup.assert_called_once()


def test_playback_performs_no_prerequisite_azure_calls(prerequisites):
    preparer, _, _, _ = prerequisites
    preparer.test_class_instance.is_live = False
    assert preparer.create_resource("executioncv") == {"cloud_validation_name": "executioncv"}
    preparer.remove_resource("executioncv")
    preparer.create_mgmt_client.assert_not_called()


def test_existing_group_is_never_adopted(prerequisites):
    preparer, resources, cv, arguments = prerequisites
    resources.resource_groups.check_existence.side_effect = None
    resources.resource_groups.check_existence.return_value = True
    with pytest.raises(AssertionError, match="existing managed group"):
        preparer.create_resource(NAME, **arguments)
    cv.cloud_validations.begin_create_or_update.assert_not_called()
    resources.resource_groups.create_or_update.assert_not_called()
    resources.resource_groups.begin_delete.assert_not_called()


@pytest.mark.parametrize("managed_by", [None, "", f"{CV_ID}-other"])
def test_managed_group_must_belong_to_created_cv(prerequisites, managed_by):
    preparer, resources, _, arguments = prerequisites
    resources.resource_groups.get.return_value.managed_by = managed_by
    preparer._cleanup = Mock()
    with pytest.raises(AssertionError, match="not associated"):
        preparer.create_resource(NAME, **arguments)
    resources.resource_groups.create_or_update.assert_not_called()
    preparer._cleanup.assert_called_once()


def test_managed_group_read_failure_is_propagated_and_cleanup_attempted(prerequisites):
    preparer, resources, _, arguments = prerequisites
    error = HttpResponseError(message="Access denied")
    resources.resource_groups.get.side_effect = error
    preparer._cleanup = Mock()
    with pytest.raises(HttpResponseError) as raised:
        preparer.create_resource(NAME, **arguments)
    assert raised.value is error
    preparer._cleanup.assert_called_once()


def test_failed_cv_creation_is_tracked_for_partial_cleanup(prerequisites):
    preparer, resources, cv, arguments = prerequisites
    error = HttpResponseError(message="CV creation response failed")
    cv.cloud_validations.begin_create_or_update.side_effect = error
    preparer._cleanup = Mock()
    with pytest.raises(HttpResponseError) as raised:
        preparer.create_resource(NAME, **arguments)
    assert raised.value is error
    assert preparer._cv_attempted
    preparer._cleanup.assert_called_once()
    resources.resource_groups.create_or_update.assert_not_called()


def test_cleanup_error_is_logged_without_replacing_setup_error(prerequisites, caplog):
    preparer, resources, _, arguments = prerequisites
    error = HttpResponseError(message="AuthorizationFailed")
    resources.resource_groups.get.side_effect = error
    preparer._cleanup = Mock(side_effect=AssertionError("Cleanup blocked"))
    with pytest.raises(HttpResponseError) as raised:
        preparer.create_resource(NAME, **arguments)
    assert raised.value is error
    assert "Prerequisite cleanup failed" in caplog.text


@pytest.fixture
def cleanup_ready(prerequisites):
    preparer, resources, cv, arguments = prerequisites
    preparer.create_resource(NAME, **arguments)
    parent = SimpleNamespace(
        id=f"/subscriptions/{SUBSCRIPTION}/resourceGroups/{GROUP}/providers/Microsoft.PlatformValidation/cloudValidations/{NAME}",
        tags={"sdk-test": NAME},
        properties=SimpleNamespace(provisioning_state="Succeeded"),
    )
    cv.cloud_validations.get.side_effect = [parent, not_found()]
    cv.validation_execution_plans.list_by_resource_group.return_value = []
    resources.resource_groups.check_existence.side_effect = None
    resources.resource_groups.check_existence.return_value = True
    resources.resource_groups.get.return_value = SimpleNamespace(tags={"sdk-test": NAME})
    resources.resource_groups.begin_delete.return_value = poller()
    cv.cloud_validations.begin_delete.return_value = poller()
    return preparer, resources, cv, parent


def test_cleanup_deletes_cv_and_waits_for_service_managed_group(cleanup_ready):
    preparer, resources, cv, _ = cleanup_ready
    preparer.remove_resource(NAME)
    cv.cloud_validations.begin_delete.assert_called_once_with(GROUP, NAME)
    resources.resource_groups.begin_delete.assert_not_called()
    setup.wait_for_managed_group_deletion.assert_called_once_with(resources, f"{NAME}-mrg")


def test_remaining_plan_blocks_all_parent_cleanup(cleanup_ready):
    preparer, resources, cv, _ = cleanup_ready
    cv.validation_execution_plans.list_by_resource_group.return_value = [Mock()]
    with pytest.raises(AssertionError, match="delete EPRs and VEPs"):
        preparer.remove_resource(NAME)
    resources.resource_groups.begin_delete.assert_not_called()
    cv.cloud_validations.begin_delete.assert_not_called()


def deletion_conflict(code="CannotDeleteResource", status=409):
    error = ResourceExistsError(message="Nested resource index has not converged")
    error.status_code = status
    error.error = SimpleNamespace(code=code)
    return error


def test_cv_cleanup_retries_only_known_nested_resource_conflict(cleanup_ready):
    preparer, resources, cv, _ = cleanup_ready
    cv.cloud_validations.begin_delete.side_effect = [deletion_conflict(), poller()]
    preparer.remove_resource(NAME)
    assert cv.cloud_validations.begin_delete.call_count == 2
    assert cv.validation_execution_plans.list_by_resource_group.call_count == 2
    setup.time.sleep.assert_called_once_with(setup.CV_DELETE_INTERVAL)
    resources.resource_groups.begin_delete.assert_not_called()


def test_cv_cleanup_stops_if_a_plan_appears_during_retry(cleanup_ready):
    preparer, resources, cv, _ = cleanup_ready
    cv.cloud_validations.begin_delete.side_effect = deletion_conflict()
    cv.validation_execution_plans.list_by_resource_group.side_effect = [[], [Mock()]]
    with pytest.raises(AssertionError, match="Execution plans remain"):
        preparer.remove_resource(NAME)
    cv.cloud_validations.begin_delete.assert_called_once()
    resources.resource_groups.begin_delete.assert_not_called()


@pytest.mark.parametrize("code,status", [("Conflict", 409), ("CannotDeleteResource", 400)])
def test_cv_cleanup_does_not_retry_other_errors(cleanup_ready, code, status):
    preparer, _, cv, _ = cleanup_ready
    cv.cloud_validations.begin_delete.side_effect = deletion_conflict(code, status)
    with pytest.raises(ResourceExistsError):
        preparer.remove_resource(NAME)
    cv.cloud_validations.begin_delete.assert_called_once()
    setup.time.sleep.assert_not_called()


def test_cv_cleanup_reports_persistent_nested_resource_conflict(cleanup_ready, monkeypatch):
    preparer, _, cv, _ = cleanup_ready
    monkeypatch.setattr(setup, "CV_DELETE_ATTEMPTS", 2)
    cv.cloud_validations.begin_delete.side_effect = deletion_conflict()
    with pytest.raises(ResourceExistsError):
        preparer.remove_resource(NAME)
    assert cv.cloud_validations.begin_delete.call_count == 2
    setup.wait_for_managed_group_deletion.assert_not_called()


def test_unowned_cv_blocks_cleanup(cleanup_ready):
    preparer, resources, cv, parent = cleanup_ready
    parent.tags = {"sdk-test": "someone-else"}
    with pytest.raises(AssertionError, match="ownership tag"):
        preparer.remove_resource(NAME)
    resources.resource_groups.begin_delete.assert_not_called()
    cv.cloud_validations.begin_delete.assert_not_called()


def test_service_managed_group_cleanup_failure_is_reported(cleanup_ready):
    preparer, resources, cv, _ = cleanup_ready
    setup.wait_for_managed_group_deletion.side_effect = AssertionError("Managed group remains")
    with pytest.raises(AssertionError, match="Managed group remains"):
        preparer.remove_resource(NAME)
    cv.cloud_validations.begin_delete.assert_called_once()
    resources.resource_groups.begin_delete.assert_not_called()


def test_nonterminal_cv_blocks_cleanup(cleanup_ready):
    preparer, resources, cv, parent = cleanup_ready
    parent.properties.provisioning_state = "Accepted"
    with pytest.raises(AssertionError, match="nonterminal"):
        preparer.remove_resource(NAME)
    resources.resource_groups.begin_delete.assert_not_called()
    cv.cloud_validations.begin_delete.assert_not_called()


def test_incomplete_operation_is_not_success():
    operation = poller()
    operation.done.return_value = False
    with pytest.raises(TimeoutError, match="did not finish"):
        setup.complete_prerequisite_operation(operation)


@pytest.mark.parametrize("remaining", [[], [Mock()]])
def test_outer_group_cleanup_does_not_cascade_into_children(remaining, monkeypatch):
    monkeypatch.setattr(setup, "wait_for_managed_group_deletion", Mock())
    preparer = setup.ExecutionResourceGroupPreparer()
    preparer.test_class_instance = Mock(is_live=True)
    preparer._need_creation = True
    preparer.client = Mock()
    preparer.test_class_instance._execution_cv_attempted = False
    preparer.client.resources.list_by_resource_group.return_value = remaining
    preparer.client.resource_groups.begin_delete.return_value = poller()
    preparer.client.resource_groups.check_existence.return_value = False
    if remaining:
        with pytest.raises(AssertionError, match="resources remain"):
            preparer.remove_resource("owned")
        preparer.client.resource_groups.begin_delete.assert_not_called()
    else:
        preparer.remove_resource("owned")
        preparer.client.resource_groups.begin_delete.assert_called_once_with("rgpy-owned")


@pytest.mark.parametrize("remaining", [[], [Mock()]])
def test_outer_group_retained_when_cv_cleanup_failed_even_if_arm_listing_is_empty(remaining):
    preparer = setup.ExecutionResourceGroupPreparer()
    preparer.test_class_instance = Mock(is_live=True)
    preparer.test_class_instance._execution_cv_attempted = True
    preparer.test_class_instance._cleaned_execution_cv = None
    preparer._need_creation = True
    preparer.client = Mock()
    preparer.client.resources.list_by_resource_group.return_value = remaining
    with pytest.raises(AssertionError, match="prerequisite cleanup was not confirmed"):
        preparer.remove_resource("owned")
    preparer.client.resource_groups.begin_delete.assert_not_called()


@pytest.mark.parametrize(
    "provider_state,cleanup_confirmed",
    [("deleted", True), ("present", True), ("forbidden", True), ("deleted", False)],
)
def test_stale_arm_listing_requires_confirmed_cleanup_and_fresh_provider_404(
    provider_state, cleanup_confirmed, monkeypatch
):
    monkeypatch.setattr(setup, "wait_for_managed_group_deletion", Mock())
    preparer = setup.ExecutionResourceGroupPreparer()
    preparer.test_class_instance = Mock(is_live=True)
    preparer.test_class_instance.get_settings_value.return_value = SUBSCRIPTION
    preparer.test_class_instance._execution_cv_attempted = True
    preparer.test_class_instance._cleaned_execution_cv = NAME if cleanup_confirmed else None
    preparer._need_creation = True
    preparer.client = Mock()
    preparer.client.resources.list_by_resource_group.return_value = [
        SimpleNamespace(
            id=f"/subscriptions/{SUBSCRIPTION}/resourceGroups/rgpy-owned"
            f"/providers/Microsoft.PlatformValidation/cloudValidations/{NAME}"
        )
    ]
    preparer.client.resource_groups.begin_delete.return_value = poller()
    cv = MagicMock()
    cv.__enter__.return_value = cv
    preparer.create_mgmt_client = Mock(return_value=cv)
    if provider_state == "deleted":
        cv.cloud_validations.get.side_effect = not_found()
    elif provider_state == "forbidden":
        cv.cloud_validations.get.side_effect = HttpResponseError(message="Access denied")
    if provider_state == "deleted" and cleanup_confirmed:
        preparer.remove_resource("owned")
        cv.cloud_validations.get.assert_called_once_with("rgpy-owned", NAME)
        preparer.client.resource_groups.begin_delete.assert_called_once_with("rgpy-owned")
    else:
        with pytest.raises((AssertionError, HttpResponseError)):
            preparer.remove_resource("owned")
        preparer.client.resource_groups.begin_delete.assert_not_called()
        if not cleanup_confirmed:
            preparer.create_mgmt_client.assert_not_called()

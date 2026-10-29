# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
from functools import partial, wraps
import inspect
import json
import os
import time
from urllib.parse import urlsplit

from azure.core.exceptions import AzureError, ResourceNotFoundError
from devtools_testutils import EnvironmentVariableLoader, add_general_string_sanitizer

from _cloud_validation_testcase import CloudValidationTestCase


ExistingExecutionPreparer = partial(
    EnvironmentVariableLoader,
    "platformvalidation",
    platformvalidation_location="eastus",
    platformvalidation_execution_resource_group="execution-parent",
    platformvalidation_execution_cloud_validation="executioncv",
    platformvalidation_execution_ownership="borrowed-parent",
)
ExistingRunPreparer = partial(
    EnvironmentVariableLoader,
    "platformvalidation",
    platformvalidation_execution_resource_group="execution-parent",
    platformvalidation_execution_cloud_validation="executioncv",
    platformvalidation_execution_plan="existing-plan",
    platformvalidation_execution_run="existing-run",
    platformvalidation_execution_ownership="borrowed-parent",
)
IMAGE_PLACEHOLDER = "https://example.invalid/image.vhd"
EXECUTION_TIMEOUT = 1800
TERMINAL_RUN_STATES = {
    "Succeeded",
    "Completed",
    "Failed",
    "Canceled",
    "Cancelled",
    "TimedOut",
}
TERMINAL_PROVISIONING_STATES = {"Succeeded", "Failed", "Canceled"}


def protect_execution_errors(function):
    """Do not let service errors echo credential-bearing embedded documents."""
    if inspect.iscoroutinefunction(function):

        @wraps(function)
        async def async_wrapper(*args, **kwargs):
            try:
                return await function(*args, **kwargs)
            except AzureError as error:
                raise RuntimeError(
                    f"Execution service request failed: HTTP {getattr(error, 'status_code', None)} "
                    f"({type(error).__name__})."
                ) from None
            except Exception as error:
                # A cleanup failure must not expose an earlier service-error context.
                raise error from None

        # Preparers use getfullargspec to remove their internal keyword arguments.
        async_wrapper.__signature__ = inspect.signature(function)
        return async_wrapper

    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except AzureError as error:
            raise RuntimeError(
                f"Execution service request failed: HTTP {getattr(error, 'status_code', None)} "
                f"({type(error).__name__})."
            ) from None
        except Exception as error:
            raise error from None

    wrapper.__signature__ = inspect.signature(function)
    return wrapper


def plan_configuration(name, source):
    return json.dumps(
        {
            "apiVersion": "microsoft.validate/executionPlan.v0",
            "kind": "ExecutionPlan",
            "metadata": {"name": name},
            "parameters": {
                "certificationPackageReference": {
                    "osType": "Linux",
                    "vmGenerationType": "V1",
                    "architectureType": "X64",
                    "recommendedVMSizes": ["Standard_D4s_v3"],
                    "storageProfile": {
                        "osDiskImage": {"sourceVhdUri": source},
                        "dataDiskImages": [],
                    },
                    "additionalProperties": {},
                }
            },
            "authoring": {
                "steps": [
                    {
                        "name": "vm-boot-test",
                        "type": "test",
                        "testRef": "/providers/Microsoft.PlatformValidation/validationTests/"
                        "compute-vmimagevalidation-vm-boot-test",
                    }
                ]
            },
        },
        separators=(",", ":"),
    )


def image_source(is_live):
    if not is_live:
        return IMAGE_PLACEHOLDER
    source = os.environ.get("PLATFORMVALIDATION_SOURCE_VHD_URI")
    if not source or urlsplit(source).scheme != "https":
        raise ValueError("An approved HTTPS PLATFORMVALIDATION_SOURCE_VHD_URI is required.")
    add_general_string_sanitizer(target=source, value=IMAGE_PLACEHOLDER)
    return source


def operation_status_target(response, target):
    headers = response.http_response.headers
    url = headers.get("Azure-AsyncOperation") or headers.get("Operation-Location")
    if not url or target:
        return
    # Never retain signed query parameters, or attempt another endpoint's route.
    parts = urlsplit(url).path.strip("/").split("/")
    lower = [part.lower() for part in parts]
    if "locations" in lower and len(parts) > 2 and lower[-2] == "operationstatuses":
        target.extend((parts[lower.index("locations") + 1], parts[-1]))


def complete(poller):
    result = poller.result(timeout=EXECUTION_TIMEOUT)
    if not poller.done():
        raise TimeoutError("Execution operation did not finish; do not delete active resources.")
    return result


async def complete_async(poller):
    result = await asyncio.wait_for(poller.result(), timeout=EXECUTION_TIMEOUT)
    if not poller.done():
        raise TimeoutError("Execution operation did not finish; do not delete active resources.")
    return result


def assert_missing(operation, *args):
    try:
        operation(*args)
    except ResourceNotFoundError as error:
        assert error.status_code == 404
    else:
        raise AssertionError("Expected HTTP 404.")


async def assert_missing_async(operation, *args):
    try:
        await operation(*args)
    except ResourceNotFoundError as error:
        assert error.status_code == 404
    else:
        raise AssertionError("Expected HTTP 404.")


def assert_owned_plan(plan, expected_id, name):
    assert plan.id and plan.id.lower() == expected_id.lower()
    assert plan.tags and plan.tags.get("sdk-test") == name, "Refusing to delete an unowned plan."
    assert plan.properties.provisioning_state in TERMINAL_PROVISIONING_STATES


def assert_deletable_run(run, expected_id, description):
    assert run.id and run.id.lower() == expected_id.lower()
    assert run.properties.description == description, "Refusing to delete an unowned run."
    assert run.properties.provisioning_state in TERMINAL_PROVISIONING_STATES
    assert run.properties.status in TERMINAL_RUN_STATES, "Execution is still active; retain its parent."


def cleanup_execution(client, args, plan_id, run_name, description):
    try:
        plan = client.validation_execution_plans.get(*args)
    except ResourceNotFoundError as error:
        assert error.status_code == 404
        return
    assert_owned_plan(plan, plan_id, args[-1])
    runs = list(client.execution_plan_runs.list_by_execution_plan(*args))
    for run in runs:
        assert run.name == run_name, "Unexpected run; refusing parent cascade."
        assert_deletable_run(run, f"{plan_id}/executionPlanRuns/{run_name}", description)
    for run in runs:
        run_args = (*args, run.name)
        tests = list(client.validation_test_runs.list_by_execution_plan_run(*run_args))
        complete(client.execution_plan_runs.begin_delete(*run_args))
        assert_missing(client.execution_plan_runs.get, *run_args)
        for test in tests:
            assert_missing(client.validation_test_runs.get, *run_args, test.name)
    if not runs:
        try:
            orphans = list(client.validation_test_runs.list_by_execution_plan_run(*args, run_name))
        except ResourceNotFoundError as error:
            assert error.status_code == 404
            orphans = []
        assert not orphans, "Orphan test runs remain; refusing parent cascade."
    assert not list(client.execution_plan_runs.list_by_execution_plan(*args))
    complete(client.validation_execution_plans.begin_delete(*args))
    assert_missing(client.validation_execution_plans.get, *args)


async def cleanup_execution_async(client, args, plan_id, run_name, description):
    try:
        plan = await client.validation_execution_plans.get(*args)
    except ResourceNotFoundError as error:
        assert error.status_code == 404
        return
    assert_owned_plan(plan, plan_id, args[-1])
    runs = [run async for run in client.execution_plan_runs.list_by_execution_plan(*args)]
    for run in runs:
        assert run.name == run_name, "Unexpected run; refusing parent cascade."
        assert_deletable_run(run, f"{plan_id}/executionPlanRuns/{run_name}", description)
    for run in runs:
        run_args = (*args, run.name)
        tests = [test async for test in client.validation_test_runs.list_by_execution_plan_run(*run_args)]
        await complete_async(await client.execution_plan_runs.begin_delete(*run_args))
        await assert_missing_async(client.execution_plan_runs.get, *run_args)
        for test in tests:
            await assert_missing_async(client.validation_test_runs.get, *run_args, test.name)
    if not runs:
        try:
            orphans = [test async for test in client.validation_test_runs.list_by_execution_plan_run(*args, run_name)]
        except ResourceNotFoundError as error:
            assert error.status_code == 404
            orphans = []
        assert not orphans, "Orphan test runs remain; refusing parent cascade."
    assert not [run async for run in client.execution_plan_runs.list_by_execution_plan(*args)]
    await complete_async(await client.validation_execution_plans.begin_delete(*args))
    await assert_missing_async(client.validation_execution_plans.get, *args)


class ExecutionTestCase(CloudValidationTestCase):
    def assert_parent(self, parent, group, name, ownership):
        assert ownership in ("borrowed-parent", "owned-parent"), "Explicit parent ownership is required."
        self.assert_identity(parent, group, name)
        assert parent.properties.provisioning_state == "Succeeded"

    def assert_plan(self, plan, plan_id, name, tags, description, configuration):
        assert plan.id and plan.id.lower() == plan_id.lower()
        assert plan.name == name
        assert plan.tags == tags
        assert plan.properties.provisioning_state == "Succeeded"
        assert plan.properties.description == description
        # Avoid pytest assertion introspection printing credential-bearing documents.
        configuration_matches = json.loads(plan.properties.plan_configuration_json) == json.loads(configuration)
        assert configuration_matches, "Plan configuration changed."

    def assert_workload(self, run, run_id, description):
        assert run.id and run.id.lower() == run_id.lower()
        assert run.properties.description == description
        assert run.properties.provisioning_state == "Succeeded"
        assert run.properties.status == "Succeeded"
        assert run.properties.error is None
        summary = run.properties.test_run_summary
        assert summary is not None
        assert summary.overall_result == "Passed"
        assert summary.total_tests == 1
        assert summary.passed_tests == 1
        assert summary.failed_tests == 0
        assert summary.skipped_tests == 0
        assert run.properties.started_at is not None
        assert run.properties.completed_at is not None
        assert run.properties.completed_at >= run.properties.started_at

    def assert_test_run(self, test, run_id):
        assert test.name in ("vm-boot-test", "compute-vmimagevalidation-vm-boot-test")
        assert test.id.lower() == f"{run_id}/validationTestRuns/{test.name}".lower()
        assert test.properties.status == "Completed"
        assert test.properties.provisioning_state == "Succeeded"
        assert test.properties.test_id == (
            "/providers/Microsoft.PlatformValidation/validationTests/compute-vmimagevalidation-vm-boot-test"
        )
        assert test.properties.error is None
        assert test.properties.pass_details
        assert not test.properties.failure_details


def wait_for_run(client, args):
    deadline = time.monotonic() + EXECUTION_TIMEOUT
    while time.monotonic() < deadline:
        run = client.execution_plan_runs.get(*args)
        if run.properties.status in TERMINAL_RUN_STATES:
            return run
        if run.properties.provisioning_state in {"Failed", "Canceled"}:
            raise AssertionError("Run provisioning failed before workload completion.")
        time.sleep(10)
    raise TimeoutError("Workload is not terminal; retain the run and plan for investigation.")


async def wait_for_run_async(client, args):
    deadline = time.monotonic() + EXECUTION_TIMEOUT
    while time.monotonic() < deadline:
        run = await client.execution_plan_runs.get(*args)
        if run.properties.status in TERMINAL_RUN_STATES:
            return run
        if run.properties.provisioning_state in {"Failed", "Canceled"}:
            raise AssertionError("Run provisioning failed before workload completion.")
        await asyncio.sleep(10)
    raise TimeoutError("Workload is not terminal; retain the run and plan for investigation.")

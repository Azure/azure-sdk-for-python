# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import inspect
import re
import traceback
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, Mock

import pytest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

import _execution_testcase as helpers


ARGS = ("group", "cv", "plan")
PLAN_ID = "/subscriptions/test/resourceGroups/group/providers/Microsoft.PlatformValidation/cloudValidations/cv/validationExecutionPlans/plan"
RUN_ID = f"{PLAN_ID}/executionPlanRuns/run"


def missing():
    error = ResourceNotFoundError("Missing")
    error.status_code = 404
    return error


def plan():
    return NS(
        id=PLAN_ID,
        tags={"sdk-test": "plan"},
        properties=NS(provisioning_state="Succeeded"),
    )


def run(status="Succeeded"):
    return NS(
        name="run",
        id=RUN_ID,
        properties=NS(description="owned", provisioning_state="Succeeded", status=status),
    )


def poller():
    result = Mock()
    result.done.return_value = True
    return result


async def items(values):
    for value in values:
        yield value


def test_configuration_uses_public_boot_contract():
    value = json.loads(helpers.plan_configuration("plan", helpers.IMAGE_PLACEHOLDER, "test"))
    assert value["apiVersion"] == "microsoft.validate/executionPlan.v0"
    assert value["kind"] == "ExecutionPlan"
    assert value["parameters"]["certificationPackageReference"]["vmGenerationType"] == "V1"
    assert value["authoring"]["steps"][0]["testRef"] == (
        "/subscriptions/test/providers/Microsoft.PlatformValidation/validationTests/compute-vmimagevalidation-vm-boot-test"
    )


def test_playback_never_uses_live_image(monkeypatch):
    monkeypatch.setenv("PLATFORMVALIDATION_SOURCE_VHD_URI", "private")
    assert helpers.image_source(False) == helpers.IMAGE_PLACEHOLDER


def test_live_image_requires_https(monkeypatch):
    monkeypatch.setenv("PLATFORMVALIDATION_SOURCE_VHD_URI", "http://example.invalid/image")
    with pytest.raises(ValueError, match="approved HTTPS"):
        helpers.image_source(True)


def test_live_image_registers_sanitizer(monkeypatch):
    sanitizer = Mock()
    monkeypatch.setattr(helpers, "add_general_string_sanitizer", sanitizer)
    monkeypatch.setenv("PLATFORMVALIDATION_SOURCE_VHD_URI", helpers.IMAGE_PLACEHOLDER)
    assert helpers.image_source(True) == helpers.IMAGE_PLACEHOLDER
    sanitizer.assert_called_once_with(target=helpers.IMAGE_PLACEHOLDER, value=helpers.IMAGE_PLACEHOLDER)


@pytest.mark.parametrize(
    "source",
    [
        "https://example.invalid/image.vhd?sig=example-secret",
        "https://example-secret@example.invalid/image.vhd",
        "https://example.invalid/image.vhd#example-secret",
        "https://[invalid/image.vhd",
    ],
)
def test_live_image_rejects_embedded_credentials_without_echoing_input(monkeypatch, source):
    monkeypatch.setenv("PLATFORMVALIDATION_SOURCE_VHD_URI", source)
    with pytest.raises(ValueError) as failure:
        helpers.image_source(True)
    assert str(failure.value) == "An approved HTTPS credential-free PLATFORMVALIDATION_SOURCE_VHD_URI is required."


def test_execution_clients_disable_http_body_logging(monkeypatch):
    from devtools_testutils import AzureMgmtRecordedTestCase

    factory = Mock()
    monkeypatch.setattr(AzureMgmtRecordedTestCase, "create_client_from_credential", factory)
    helpers.ExecutionTestCase().create_client_from_credential(Mock(), Mock(), logging_enable=True)
    assert factory.call_args.kwargs["logging_enable"] is False


@pytest.mark.parametrize("subscription", ["test", "other", None])
def test_test_run_requires_the_requested_subscription(monkeypatch, subscription):
    case = helpers.ExecutionTestCase()
    monkeypatch.setattr(case, "get_settings_value", lambda _: "test")
    catalog_id = "/providers/Microsoft.PlatformValidation/validationTests/compute-vmimagevalidation-vm-boot-test"
    test = NS(
        name="vm-boot-test",
        id=f"{RUN_ID}/validationTestRuns/vm-boot-test",
        properties=NS(
            status="Completed",
            provisioning_state="Succeeded",
            test_id=f"/subscriptions/{subscription}{catalog_id}" if subscription else catalog_id,
            error=None,
            pass_details=["Passed"],
            failure_details=[],
        ),
    )
    if subscription == "test":
        case.assert_test_run(test, RUN_ID)
    else:
        with pytest.raises(AssertionError):
            case.assert_test_run(test, RUN_ID)


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.asyncio
async def test_unresolved_creation_blocks_cleanup_even_if_lists_would_be_empty(async_mode):
    client = Mock()
    client.execution_plan_runs.list_by_execution_plan.return_value = []
    with pytest.raises(AssertionError, match="Unresolved execution mutation"):
        if async_mode:
            await helpers.cleanup_execution_async(client, ARGS, PLAN_ID, "run", "owned", mutation_in_progress=True)
        else:
            helpers.cleanup_execution(client, ARGS, PLAN_ID, "run", "owned", mutation_in_progress=True)
    client.validation_execution_plans.get.assert_not_called()
    client.validation_execution_plans.begin_delete.assert_not_called()


@pytest.mark.parametrize(
    "url,expected",
    [
        (
            "https://example.invalid/providers/x/locations/eastus/operationStatuses/id?sig=private",
            ["eastus", "id"],
        ),
        ("https://example.invalid/operationResults/id?sig=private", []),
        (None, []),
    ],
)
def test_operation_target_discards_signed_query(url, expected):
    target = []
    helpers.operation_status_target(NS(http_response=NS(headers={"Azure-AsyncOperation": url})), target)
    assert target == expected


def test_incomplete_sync_poller_is_not_success():
    operation = poller()
    operation.done.return_value = False
    with pytest.raises(TimeoutError):
        helpers.complete(operation)


@pytest.mark.asyncio
async def test_incomplete_async_poller_is_not_success():
    operation = poller()
    operation.result = AsyncMock(return_value=None)
    operation.done.return_value = False
    with pytest.raises(TimeoutError):
        await helpers.complete_async(operation)


@pytest.mark.parametrize("status", ["Accepted", "Running", None])
def test_active_run_cannot_be_deleted(status):
    with pytest.raises(AssertionError, match="still active"):
        helpers.assert_deletable_run(run(status), RUN_ID, "owned")


def test_wrong_run_owner_cannot_be_deleted():
    with pytest.raises(AssertionError, match="unowned"):
        helpers.assert_deletable_run(run(), RUN_ID, "someone else")


def test_wrong_plan_owner_cannot_be_deleted():
    with pytest.raises(AssertionError, match="unowned"):
        helpers.assert_owned_plan(plan(), PLAN_ID, "someone else")


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.asyncio
async def test_cleanup_child_first_and_checks_vtr_cascade(async_mode):
    client = Mock()
    order = []
    if async_mode:
        client.validation_execution_plans.get = AsyncMock(side_effect=[plan(), missing()])
        client.execution_plan_runs.list_by_execution_plan.side_effect = lambda *a: items([run()] if not order else [])
        client.validation_test_runs.list_by_execution_plan_run.side_effect = lambda *a: items([NS(name="boot")])
        for operations, label in (
            (client.execution_plan_runs, "run"),
            (client.validation_execution_plans, "plan"),
        ):

            async def delete(*args, label=label):
                order.append(label)
                operation = poller()
                operation.result = AsyncMock(return_value=None)
                return operation

            operations.begin_delete = AsyncMock(side_effect=delete)
        client.execution_plan_runs.get = AsyncMock(side_effect=missing())
        client.validation_test_runs.get = AsyncMock(side_effect=missing())
        await helpers.cleanup_execution_async(client, ARGS, PLAN_ID, "run", "owned")
        client.validation_test_runs.get.assert_awaited_once_with(*ARGS, "run", "boot")
    else:
        client.validation_execution_plans.get.side_effect = [plan(), missing()]
        client.execution_plan_runs.list_by_execution_plan.side_effect = [[run()], []]
        client.validation_test_runs.list_by_execution_plan_run.return_value = [NS(name="boot")]
        client.execution_plan_runs.begin_delete.side_effect = lambda *a: order.append("run") or poller()
        client.validation_execution_plans.begin_delete.side_effect = lambda *a: order.append("plan") or poller()
        client.execution_plan_runs.get.side_effect = missing()
        client.validation_test_runs.get.side_effect = missing()
        helpers.cleanup_execution(client, ARGS, PLAN_ID, "run", "owned")
        client.validation_test_runs.get.assert_called_once_with(*ARGS, "run", "boot")
    assert order == ["run", "plan"]
    client.cloud_validations.begin_delete.assert_not_called()


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.asyncio
async def test_cleanup_refuses_unexpected_run_before_deleting_anything(async_mode):
    client = Mock()
    if async_mode:
        client.validation_execution_plans.get = AsyncMock(return_value=plan())
        client.execution_plan_runs.list_by_execution_plan.side_effect = lambda *a: items([run()])
        with pytest.raises(AssertionError, match="Unexpected run"):
            await helpers.cleanup_execution_async(client, ARGS, PLAN_ID, "other", "owned")
    else:
        client.validation_execution_plans.get.return_value = plan()
        client.execution_plan_runs.list_by_execution_plan.return_value = [run()]
        with pytest.raises(AssertionError, match="Unexpected run"):
            helpers.cleanup_execution(client, ARGS, PLAN_ID, "other", "owned")
    client.execution_plan_runs.begin_delete.assert_not_called()
    client.validation_execution_plans.begin_delete.assert_not_called()


def test_workload_rejects_partial_success():
    result = run()
    result.properties.error = None
    result.properties.test_run_summary = NS(
        overall_result="Passed",
        total_tests=1,
        passed_tests=0,
        failed_tests=1,
        skipped_tests=0,
    )
    with pytest.raises(AssertionError):
        helpers.ExecutionTestCase().assert_workload(result, RUN_ID, "owned")


def test_proxy_sanitizer_registration(monkeypatch):
    import _sanitizers as sanitizers

    header, body = Mock(), Mock()
    for name in (
        "remove_batch_sanitizers",
        "add_general_string_sanitizer",
        "add_remove_header_sanitizer",
        "add_general_regex_sanitizer",
    ):
        monkeypatch.setattr(sanitizers, name, Mock())
    monkeypatch.setattr(sanitizers, "add_header_regex_sanitizer", header)
    monkeypatch.setattr(sanitizers, "add_body_key_sanitizer", body)
    sanitizers.configure_sanitizers()
    header.assert_called_once_with(key="x-ms-operation-identifier", value="Sanitized")
    assert any(call.kwargs.get("json_path") == "$..planConfigurationJson" for call in body.call_args_list)


def test_subscription_list_sanitizers_preserve_target_identity(monkeypatch):
    import _cloud_validation_testcase as cloud

    body, tags = Mock(), Mock()
    monkeypatch.setattr(cloud, "add_body_key_sanitizer", body)
    monkeypatch.setattr(cloud, "add_body_regex_sanitizer", tags)
    cloud.CloudValidationTestCase().sanitize_subscription_list("owned")
    assert body.call_count == 5
    for call in body.call_args_list:
        assert call.kwargs["json_path"].startswith("$.value[?(@.name != 'owned')]")
        assert call.kwargs["function_scoped"]
        condition = json.loads(call.kwargs["condition"])["uriRegex"]
        assert re.search(
            condition,
            "https://example.invalid/subscriptions/test/providers/Microsoft.PlatformValidation/cloudValidations?api-version=test",
        )
        assert not re.search(
            condition,
            "https://example.invalid/subscriptions/test/resourceGroups/group/providers/Microsoft.PlatformValidation/cloudValidations?api-version=test",
        )
    tags.assert_called_once()
    tagged = json.dumps({"tags": {"private-key": 'value with {"nested"} braces and \\ escapes'}})
    settings = tags.call_args.kwargs
    assert json.loads(re.sub(settings["regex"], settings["value"], tagged)) == {"tags": {}}


@pytest.mark.parametrize("key", ["sig", "se", "st", "sv", "s", "c", "h", "t"])
@pytest.mark.parametrize("depth", [0, 1, 2])
@pytest.mark.parametrize("value", ["private", r"\/private", r"private\/tail", r"\u0070rivate"])
def test_signed_url_sanitizer_removes_escaped_values(monkeypatch, key, depth, value):
    import _sanitizers as sanitizers

    general = Mock()
    for name in (
        "remove_batch_sanitizers",
        "add_general_string_sanitizer",
        "add_remove_header_sanitizer",
        "add_header_regex_sanitizer",
        "add_body_key_sanitizer",
    ):
        monkeypatch.setattr(sanitizers, name, Mock())
    monkeypatch.setattr(sanitizers, "add_general_regex_sanitizer", general)
    sanitizers.configure_sanitizers()
    settings = next(call.kwargs for call in general.call_args_list if call.kwargs.get("group_for_replace") == "2")
    document = '{"url": "https://example.invalid/?' + key + "=" + value + '"}'
    for _ in range(depth):
        document = json.dumps({"planConfigurationJson": document})
    sanitized = re.sub(settings["regex"], lambda match: match[1] + settings["value"], document)
    assert "private" not in sanitized
    for _ in range(depth):
        sanitized = json.loads(sanitized)["planConfigurationJson"]
    assert json.loads(sanitized)["url"].endswith("=Sanitized")


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.asyncio
async def test_cleanup_refuses_orphans_after_prior_run_deletion(async_mode):
    client = Mock()
    if async_mode:
        client.validation_execution_plans.get = AsyncMock(return_value=plan())
        client.execution_plan_runs.list_by_execution_plan.side_effect = lambda *a: items([])
        client.validation_test_runs.list_by_execution_plan_run.side_effect = lambda *a: items([NS(name="orphan")])
        with pytest.raises(AssertionError, match="Orphan"):
            await helpers.cleanup_execution_async(client, ARGS, PLAN_ID, "run", "owned")
    else:
        client.validation_execution_plans.get.return_value = plan()
        client.execution_plan_runs.list_by_execution_plan.return_value = []
        client.validation_test_runs.list_by_execution_plan_run.return_value = [NS(name="orphan")]
        with pytest.raises(AssertionError, match="Orphan"):
            helpers.cleanup_execution(client, ARGS, PLAN_ID, "run", "owned")
    client.validation_execution_plans.begin_delete.assert_not_called()


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.asyncio
async def test_service_error_does_not_echo_embedded_credentials(async_mode):
    message = "sensitive-" + "image-signature"
    if async_mode:

        @helpers.protect_execution_errors
        async def operation():
            raise HttpResponseError(message)

    else:

        @helpers.protect_execution_errors
        def operation():
            raise HttpResponseError(message)

    with pytest.raises(RuntimeError) as failure:
        if async_mode:
            await operation()
        else:
            operation()
    assert inspect.getfullargspec(operation).varkw is None
    assert message not in "".join(traceback.format_exception(failure.value))

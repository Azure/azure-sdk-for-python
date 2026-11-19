# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
import datetime
import hashlib
import hmac
import importlib
import inspect
import json
import io
import os
import re
import unittest
import zipfile
from typing import get_args, get_type_hints
from unittest.mock import AsyncMock, MagicMock, Mock, mock_open, patch

import batch_preparers
from devtools_testutils import AzureTestError
from azure.core.credentials import AzureNamedKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline import PipelineContext, PipelineRequest
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy, BearerTokenCredentialPolicy
from azure.core.rest import HttpRequest, HttpResponse
from azure.batch import BatchClient, models
from azure.batch.aio import BatchClient as AsyncBatchClient
from azure.batch.models import BatchJobTerminateOptions
from azure.batch._operations._operations import _BatchClientOperationsMixin as GeneratedOperations
from azure.batch.aio._operations._operations import _BatchClientOperationsMixin as AsyncGeneratedOperations
from azure.batch._patch import BatchExceptionPolicy, BatchSharedKeyAuthPolicy


ENDPOINT = "https://account.region.batch.azure.com"
OPTIONAL_BODY_POST_OPERATIONS = (
    ("_terminate_job_internal", ("job",), models.BatchJobTerminateOptions),
    ("_deallocate_node_internal", ("pool", "node"), models.BatchNodeDeallocateOptions),
    ("_reboot_node_internal", ("pool", "node"), models.BatchNodeRebootOptions),
    ("_reimage_node_internal", ("pool", "node"), models.BatchNodeReimageOptions),
)


class TestLiveRecordingResources(unittest.TestCase):
    def test_storage_preparer_explicitly_disables_anonymous_blob_access(self):
        preparer = batch_preparers.BatchStorageAccountPreparer(name_prefix="batch4", location="eastus2")
        preparer.client = Mock()
        operation = preparer._create_account("test-group", "teststorage")
        self.assertIs(operation, preparer.client.storage_accounts.begin_create.return_value)
        preparer.client.storage_accounts.begin_create.assert_called_once_with(
            "test-group",
            "teststorage",
            {
                "sku": {"name": "Standard_LRS"},
                "location": "eastus2",
                "kind": "StorageV2",
                "enable_https_traffic_only": True,
                "allow_blob_public_access": False,
            },
        )

    def test_default_application_package_is_valid_zip(self):
        with patch.dict(os.environ, {"BATCH_TEST_APP_ZIP": ""}):
            content = batch_preparers.load_application_package()
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            self.assertEqual(archive.namelist(), ["readme.txt"])
            self.assertIsNone(archive.testzip())

    def test_configured_application_package_is_preserved(self):
        with patch.dict(os.environ, {"BATCH_TEST_APP_ZIP": ""}):
            content = batch_preparers.load_application_package()
        with patch.dict(os.environ, {"BATCH_TEST_APP_ZIP": "test-application.zip"}):
            with patch("builtins.open", mock_open(read_data=content)):
                self.assertEqual(batch_preparers.load_application_package(), content)

    def test_invalid_application_package_fails_explicitly(self):
        with patch.dict(os.environ, {"BATCH_TEST_APP_ZIP": "invalid.zip"}):
            with patch("builtins.open", mock_open(read_data=b"not a zip")):
                with self.assertRaisesRegex(AzureTestError, "valid ZIP"):
                    batch_preparers.load_application_package()

    def test_playback_needs_no_sas_or_sanitizer_registration(self):
        with patch.dict(os.environ, {"BATCH_LOG_CONTAINER_SAS_URL": ""}):
            with patch.object(batch_preparers, "add_general_string_sanitizer") as sanitizer:
                self.assertEqual(
                    batch_preparers.get_log_container_url(False), batch_preparers.PLAYBACK_LOG_CONTAINER_URL
                )
                sanitizer.assert_not_called()

    def test_live_sas_is_sanitized_before_use(self):
        url = "https://example.blob.core.windows.net/logs?sp=w&sr=c&sig=unit-test-signature"
        with patch.dict(os.environ, {"BATCH_LOG_CONTAINER_SAS_URL": url}):
            with patch.object(batch_preparers, "add_general_string_sanitizer") as general:
                with patch.object(batch_preparers, "add_body_key_sanitizer") as body:
                    self.assertEqual(batch_preparers.get_log_container_url(True), url)
        general.assert_called_once_with(target=url, value=batch_preparers.PLAYBACK_LOG_CONTAINER_URL)
        body.assert_called_once_with(json_path="$..containerUrl", value=batch_preparers.PLAYBACK_LOG_CONTAINER_URL)

    def test_missing_or_invalid_sas_fails_without_disclosing_it(self):
        for value in ("", "not-a-url", "https://example.blob.core.windows.net/logs?sp=r&sr=c&sig=test"):
            with self.subTest(case="missing" if not value else "invalid"):
                with patch.dict(os.environ, {"BATCH_LOG_CONTAINER_SAS_URL": value}):
                    with self.assertRaises(AzureTestError) as raised:
                        batch_preparers.get_log_container_url(True)
                self.assertIn("BATCH_LOG_CONTAINER_SAS_URL", str(raised.exception))
                if value:
                    self.assertNotIn(value, str(raised.exception))


def named_key():
    return AzureNamedKeyCredential("account", "ZmFrZQ==")


def file_headers():
    return {
        "ocp-batch-file-url": ENDPOINT + "/files/output.txt",
        "ocp-batch-file-isdirectory": False,
        "Last-Modified": datetime.datetime(2026, 11, 12, tzinfo=datetime.timezone.utc),
        "Content-Length": 42,
        "ocp-creation-time": None,
        "ocp-batch-file-mode": "0644",
    }


def convert_file_response(*_args, **kwargs):
    return kwargs["cls"](None, None, file_headers())


def create_collection_result(*_args, **kwargs):
    return models.BatchCreateTaskCollectionResult(
        result_values=[
            models.BatchTaskCreateResult(task_id=task.id, status=models.BatchTaskAddStatus.SUCCESS)
            for task in kwargs["task_collection"].task_values
        ]
    )


def referenced_model_types(annotation):
    if inspect.isclass(annotation) and annotation.__module__.startswith("azure.batch.models."):
        yield annotation
    children = annotation if isinstance(annotation, (list, tuple)) else get_args(annotation)
    for child in children:
        yield from referenced_model_types(child)


def accepted_post_response(request, **_kwargs):
    response = Mock(spec=HttpResponse)
    response.request = request
    response.status_code = 202
    response.headers = {}
    response.content_type = ""
    response.content = b""
    response.text.return_value = ""
    return response


def termination_body_cases():
    return (
        ("omitted", {}, None),
        ("none", {"options": None}, None),
        ("empty-model", {"options": BatchJobTerminateOptions()}, {}),
        (
            "populated-model",
            {"options": BatchJobTerminateOptions(termination_reason="UserTerminate")},
            {"terminateReason": "UserTerminate"},
        ),
    )


class TestCustomizationExports(unittest.TestCase):
    def test_all_operation_and_nested_model_types_have_public_exports(self):
        pending = []
        for client in (BatchClient, AsyncBatchClient):
            for name, method in inspect.getmembers(client, inspect.isfunction):
                if not name.startswith("_"):
                    for annotation in get_type_hints(method).values():
                        pending.extend(referenced_model_types(annotation))
        checked = set()
        while pending:
            model_type = pending.pop()
            if model_type in checked:
                continue
            checked.add(model_type)
            with self.subTest(model=model_type.__name__):
                self.assertIn(model_type.__name__, models.__all__)
                self.assertIs(getattr(models, model_type.__name__), model_type)
            # Generated model annotations refer to an alias imported only under TYPE_CHECKING.
            namespace = dict(vars(importlib.import_module(model_type.__module__)), _models=models)
            for annotation in get_type_hints(model_type, globalns=namespace).values():
                pending.extend(referenced_model_types(annotation))
        self.assertTrue(checked)

    def test_operation_documentation_uses_public_model_names(self):
        checked = set()
        for client in (BatchClient, AsyncBatchClient):
            for name, method in inspect.getmembers(client, inspect.isfunction):
                if name.startswith("_"):
                    continue
                references = re.findall(r"azure\.batch\.models\.([A-Za-z_]\w*)", inspect.getdoc(method) or "")
                for model_name in references:
                    with self.subTest(client=client, method=name, model=model_name):
                        self.assertIn(model_name, models.__all__)
                        self.assertTrue(inspect.isclass(getattr(models, model_name)))
                        checked.add(model_name)
        self.assertTrue(checked)

    def test_option_annotations_use_the_public_classes(self):
        options = {
            "begin_terminate_job": BatchJobTerminateOptions,
            "begin_deallocate_node": models.BatchNodeDeallocateOptions,
            "begin_reboot_node": models.BatchNodeRebootOptions,
            "begin_reimage_node": models.BatchNodeReimageOptions,
        }
        for client in (BatchClient, AsyncBatchClient):
            for name, model_type in options.items():
                with self.subTest(client=client, method=name):
                    method = getattr(client, name)
                    self.assertIn(model_type, get_args(get_type_hints(method)["options"]))
                    self.assertNotRegex(inspect.getsource(method), r"_models\._(?:models|enums)\.")

    def test_public_customizations_are_available_on_both_clients(self):
        names = (
            "begin_delete_job",
            "begin_disable_job",
            "begin_enable_job",
            "begin_delete_job_schedule",
            "begin_delete_pool",
            "begin_deallocate_node",
            "begin_reboot_node",
            "begin_reimage_node",
            "begin_remove_nodes",
            "begin_resize_pool",
            "begin_start_node",
            "begin_stop_pool_resize",
            "begin_terminate_job",
            "begin_terminate_job_schedule",
            "create_tasks",
            "download_node_file",
            "download_task_file",
            "get_node_file_properties",
            "get_task_file_properties",
        )
        for client in (BatchClient, AsyncBatchClient):
            for name in names:
                with self.subTest(client=client, method=name):
                    self.assertTrue(callable(getattr(client, name)))
        self.assertIn("CreateTasksError", models.__all__)
        self.assertIn("BatchFileProperties", models.__all__)

    def test_intentional_service_api_removals_are_preserved(self):
        for name in ("BatchPoolUsageMetrics", "BatchPoolUsageStatistics"):
            self.assertFalse(hasattr(models, name))
        for client in (BatchClient, AsyncBatchClient):
            self.assertFalse(hasattr(client, "list_pool_usage_metrics"))
        self.assertFalse(hasattr(models.BatchPoolStatistics, "usage_statistics"))
        for enum in (
            models.BatchNodeDeallocationOption,
            models.BatchNodeDeallocateOption,
            models.BatchNodeRebootKind,
            models.BatchNodeReimageOption,
        ):
            self.assertFalse(hasattr(enum, "RETAINED_DATA"))

    def test_shared_key_signing_on_both_clients(self):
        for client_type in (BatchClient, AsyncBatchClient):
            with self.subTest(client=client_type):
                client = client_type(ENDPOINT, named_key())
                policy = client._config.authentication_policy
                self.assertIsInstance(policy, BatchSharedKeyAuthPolicy)
                date = "Thu, 12 Nov 2026 00:00:00 GMT"
                request = PipelineRequest(
                    HttpRequest("GET", ENDPOINT + "/pools?api-version=2026-10-01", headers={"ocp-date": date}),
                    PipelineContext(None),
                )
                policy.on_request(request)
                canonical = "GET\n" + "\n" * 11 + "ocp-date:" + date + "\n/account/pools\napi-version:2026-10-01"
                signature = base64.b64encode(hmac.new(b"fake", canonical.encode(), hashlib.sha256).digest()).decode()
                self.assertEqual(request.http_request.headers["Authorization"], "SharedKey account:" + signature)
                self.assertEqual(request.http_request.headers["ocp-date"], date)

    def test_token_credentials_and_explicit_policy_are_preserved(self):
        for client_type, policy_type in (
            (BatchClient, BearerTokenCredentialPolicy),
            (AsyncBatchClient, AsyncBearerTokenCredentialPolicy),
        ):
            with self.subTest(client=client_type):
                client = client_type(ENDPOINT, Mock(spec=["get_token"]))
                self.assertIsInstance(client._config.authentication_policy, policy_type)
                explicit_policy = Mock()
                client = client_type(ENDPOINT, named_key(), authentication_policy=explicit_policy)
                self.assertIs(client._config.authentication_policy, explicit_policy)
                self.assertTrue(
                    any(isinstance(policy, BatchExceptionPolicy) for policy in client._client._pipeline._impl_policies)
                    or any(
                        isinstance(getattr(policy, "_policy", None), BatchExceptionPolicy)
                        for policy in client._client._pipeline._impl_policies
                    )
                )


class TestSyncCustomizationBehavior(unittest.TestCase):
    def setUp(self):
        self.client = BatchClient(ENDPOINT, named_key())
        self.addCleanup(self.client.close)

    def test_api_version_default_and_overrides_are_forwarded(self):
        self.assertEqual(self.client._config.api_version, "2026-10-01")
        for version in ("2025-06-01", None):
            with self.subTest(version=version):
                with BatchClient(ENDPOINT, named_key(), api_version=version) as client:
                    self.assertEqual(client._config.api_version, version)

    def test_terminate_job_accepts_public_options(self):
        options = BatchJobTerminateOptions(termination_reason="UserTerminate")
        completed_job = models.BatchJob(state=models.BatchJobState.COMPLETED)
        with patch.object(self.client, "_terminate_job_internal", return_value=Mock()) as operation:
            with patch.object(self.client, "get_job", return_value=completed_job):
                poller = getattr(self.client, "begin_terminate_job")("job", options=options, polling_interval=0)
                self.assertIsNone(poller.result(timeout=5))
        self.assertIs(operation.call_args.kwargs["options"], options)
        self.assertEqual(options.termination_reason, "UserTerminate")
        self.assertTrue(poller.done())

    def test_terminate_job_empty_options_reach_transport(self):
        for case, arguments, expected_body in termination_body_cases():
            with self.subTest(case=case):
                transport = MagicMock()
                transport.send.side_effect = accepted_post_response
                with BatchClient(ENDPOINT, named_key(), transport=transport) as client:
                    completed_job = models.BatchJob(state=models.BatchJobState.COMPLETED)
                    with patch.object(client, "get_job", return_value=completed_job):
                        poller = getattr(client, "begin_terminate_job")("job", polling_interval=0, **arguments)
                        self.assertIsNone(poller.result(timeout=5))
                    transport.send.assert_called_once()
                    request = transport.send.call_args.args[0]
                    self.assertEqual(request.method, "POST")
                    self.assertEqual(request.url, ENDPOINT + "/jobs/job/terminate?api-version=2026-10-01")
                    if expected_body is None:
                        self.assertIsNone(request.content)
                        self.assertNotIn("content-type", request.headers)
                    else:
                        self.assertEqual(json.loads(request.content), expected_body)
                        if expected_body:
                            self.assertEqual(
                                request.headers["content-type"], "application/json; odata=minimalmetadata"
                            )

    def test_optional_body_post_operations_handle_absent_and_empty_models(self):
        for name, args, model_type in OPTIONAL_BODY_POST_OPERATIONS:
            for options in (None, model_type()):
                with self.subTest(operation=name, options=options):
                    transport = MagicMock()
                    transport.send.side_effect = accepted_post_response
                    with BatchClient(ENDPOINT, named_key(), transport=transport) as client:
                        self.assertIsNone(getattr(client, name)(*args, options=options))
                    transport.send.assert_called_once()
                    request = transport.send.call_args.args[0]
                    self.assertEqual(request.method, "POST")
                    if options is None:
                        self.assertIsNone(request.content)
                        self.assertNotIn("content-type", request.headers)
                    else:
                        self.assertEqual(json.loads(request.content), {})

    def test_file_properties_and_integer_timeout(self):
        for method in ("get_node_file_properties", "get_task_file_properties"):
            generated = "_" + method + "_internal"
            args = ("pool", "node", "output.txt") if "node" in method else ("job", "task", "output.txt")
            with self.subTest(method=method):
                with patch.object(GeneratedOperations, generated, side_effect=convert_file_response) as operation:
                    result = getattr(self.client, method)(*args, service_timeout=17)
                self.assertIsInstance(result, models.BatchFileProperties)
                self.assertEqual(result.content_length, 42)
                self.assertEqual(result.url, file_headers()["ocp-batch-file-url"])
                self.assertFalse(result.is_directory)
                self.assertEqual(operation.call_args.kwargs["service_timeout"], datetime.timedelta(seconds=17))

    def test_bulk_tasks_are_batched_and_aggregated(self):
        tasks = [models.BatchTaskCreateOptions(id=str(index), command_line="echo test") for index in range(101)]
        with patch.object(self.client, "create_task_collection", side_effect=create_collection_result) as operation:
            result = getattr(self.client, "create_tasks")("job", tasks, service_timeout=19)
        self.assertEqual(operation.call_count, 2)
        self.assertEqual({value.task_id for value in result.result_values}, {task.id for task in tasks})
        for call in operation.call_args_list:
            self.assertLessEqual(len(call.kwargs["task_collection"].task_values), 100)
            self.assertEqual(call.kwargs["service_timeout"], datetime.timedelta(seconds=19))

    def test_bulk_task_failures_keep_custom_exception(self):
        failure = models.BatchTaskCreateResult(
            task_id="task",
            status=models.BatchTaskAddStatus.CLIENT_ERROR,
            error=models.BatchError(code="InvalidTask", message=models.BatchErrorMessage(value="Invalid task")),
        )
        response = models.BatchCreateTaskCollectionResult(result_values=[failure])
        with patch.object(self.client, "create_task_collection", return_value=response):
            with self.assertRaises(models.CreateTasksError) as raised:
                getattr(self.client, "create_tasks")(
                    "job", [models.BatchTaskCreateOptions(id="task", command_line="echo test")]
                )
        self.assertEqual(list(raised.exception.failure_tasks), [failure])

    def test_delete_pool_poller_completes_when_pool_disappears(self):
        with patch.object(self.client, "_delete_pool_internal", return_value=Mock()) as operation:
            with patch.object(self.client, "get_pool", side_effect=ResourceNotFoundError("gone")):
                poller = getattr(self.client, "begin_delete_pool")("pool", service_timeout=23, polling_interval=0)
                self.assertIsNone(poller.result(timeout=5))
        self.assertTrue(poller.done())
        self.assertEqual(operation.call_args.kwargs["service_timeout"], datetime.timedelta(seconds=23))


class TestAsyncCustomizationBehavior(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = AsyncBatchClient(ENDPOINT, named_key())
        self.addAsyncCleanup(self.client.close)

    async def test_api_version_default_and_overrides_are_forwarded(self):
        self.assertEqual(self.client._config.api_version, "2026-10-01")
        for version in ("2025-06-01", None):
            with self.subTest(version=version):
                async with AsyncBatchClient(ENDPOINT, named_key(), api_version=version) as client:
                    self.assertEqual(client._config.api_version, version)

    async def test_terminate_job_accepts_public_options(self):
        options = BatchJobTerminateOptions(termination_reason="UserTerminate")
        completed_job = models.BatchJob(state=models.BatchJobState.COMPLETED)
        with patch.object(
            self.client, "_terminate_job_internal", new_callable=AsyncMock, return_value=Mock()
        ) as operation:
            with patch.object(self.client, "get_job", new_callable=AsyncMock, return_value=completed_job):
                poller = await getattr(self.client, "begin_terminate_job")("job", options=options, polling_interval=0)
                self.assertIsNone(await poller.result())
        self.assertIs(operation.call_args.kwargs["options"], options)
        self.assertEqual(options.termination_reason, "UserTerminate")
        self.assertTrue(poller.done())

    async def test_terminate_job_empty_options_reach_transport(self):
        for case, arguments, expected_body in termination_body_cases():
            with self.subTest(case=case):
                transport = MagicMock()
                transport.send = AsyncMock(side_effect=accepted_post_response)
                transport.close = AsyncMock()
                async with AsyncBatchClient(ENDPOINT, named_key(), transport=transport) as client:
                    completed_job = models.BatchJob(state=models.BatchJobState.COMPLETED)
                    with patch.object(client, "get_job", new_callable=AsyncMock, return_value=completed_job):
                        poller = await getattr(client, "begin_terminate_job")("job", polling_interval=0, **arguments)
                        self.assertIsNone(await poller.result())
                    transport.send.assert_awaited_once()
                    request = transport.send.call_args.args[0]
                    self.assertEqual(request.method, "POST")
                    self.assertEqual(request.url, ENDPOINT + "/jobs/job/terminate?api-version=2026-10-01")
                    if expected_body is None:
                        self.assertIsNone(request.content)
                        self.assertNotIn("content-type", request.headers)
                    else:
                        self.assertEqual(json.loads(request.content), expected_body)
                        if expected_body:
                            self.assertEqual(
                                request.headers["content-type"], "application/json; odata=minimalmetadata"
                            )

    async def test_optional_body_post_operations_handle_absent_and_empty_models(self):
        for name, args, model_type in OPTIONAL_BODY_POST_OPERATIONS:
            for options in (None, model_type()):
                with self.subTest(operation=name, options=options):
                    transport = MagicMock()
                    transport.send = AsyncMock(side_effect=accepted_post_response)
                    transport.close = AsyncMock()
                    async with AsyncBatchClient(ENDPOINT, named_key(), transport=transport) as client:
                        self.assertIsNone(await getattr(client, name)(*args, options=options))
                    transport.send.assert_awaited_once()
                    request = transport.send.call_args.args[0]
                    self.assertEqual(request.method, "POST")
                    if options is None:
                        self.assertIsNone(request.content)
                        self.assertNotIn("content-type", request.headers)
                    else:
                        self.assertEqual(json.loads(request.content), {})

    async def test_file_properties_and_integer_timeout(self):
        for method in ("get_node_file_properties", "get_task_file_properties"):
            generated = "_" + method + "_internal"
            args = ("pool", "node", "output.txt") if "node" in method else ("job", "task", "output.txt")
            with self.subTest(method=method):
                with patch.object(
                    AsyncGeneratedOperations, generated, new_callable=AsyncMock, side_effect=convert_file_response
                ) as operation:
                    result = await getattr(self.client, method)(*args, service_timeout=17)
                self.assertIsInstance(result, models.BatchFileProperties)
                self.assertEqual(result.content_length, 42)
                self.assertEqual(result.url, file_headers()["ocp-batch-file-url"])
                self.assertFalse(result.is_directory)
                self.assertEqual(operation.call_args.kwargs["service_timeout"], datetime.timedelta(seconds=17))

    async def test_bulk_tasks_are_batched_and_aggregated(self):
        tasks = [models.BatchTaskCreateOptions(id=str(index), command_line="echo test") for index in range(101)]
        with patch.object(
            self.client, "create_task_collection", new_callable=AsyncMock, side_effect=create_collection_result
        ) as operation:
            result = await getattr(self.client, "create_tasks")("job", tasks, service_timeout=19)
        self.assertEqual(operation.await_count, 2)
        self.assertEqual({value.task_id for value in result.result_values}, {task.id for task in tasks})
        for call in operation.call_args_list:
            self.assertLessEqual(len(call.kwargs["task_collection"].task_values), 100)
            self.assertEqual(call.kwargs["service_timeout"], datetime.timedelta(seconds=19))

    async def test_bulk_task_failures_keep_custom_exception(self):
        failure = models.BatchTaskCreateResult(
            task_id="task",
            status=models.BatchTaskAddStatus.CLIENT_ERROR,
            error=models.BatchError(code="InvalidTask", message=models.BatchErrorMessage(value="Invalid task")),
        )
        response = models.BatchCreateTaskCollectionResult(result_values=[failure])
        with patch.object(self.client, "create_task_collection", new_callable=AsyncMock, return_value=response):
            with self.assertRaises(models.CreateTasksError) as raised:
                await getattr(self.client, "create_tasks")(
                    "job", [models.BatchTaskCreateOptions(id="task", command_line="echo test")]
                )
        self.assertEqual(list(raised.exception.failure_tasks), [failure])

    async def test_delete_pool_poller_completes_when_pool_disappears(self):
        with patch.object(
            self.client, "_delete_pool_internal", new_callable=AsyncMock, return_value=Mock()
        ) as operation:
            with patch.object(
                self.client, "get_pool", new_callable=AsyncMock, side_effect=ResourceNotFoundError("gone")
            ):
                poller = await getattr(self.client, "begin_delete_pool")(
                    "pool", service_timeout=23, polling_interval=0
                )
                self.assertIsNone(await poller.result())
        self.assertTrue(poller.done())
        self.assertEqual(operation.call_args.kwargs["service_timeout"], datetime.timedelta(seconds=23))

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
import datetime
import hashlib
import hmac
import unittest
from unittest.mock import AsyncMock, Mock, patch

from azure.core.credentials import AzureNamedKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline import PipelineContext, PipelineRequest
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy, BearerTokenCredentialPolicy
from azure.core.rest import HttpRequest
from azure.batch import BatchClient, models
from azure.batch.aio import BatchClient as AsyncBatchClient
from azure.batch._operations._operations import _BatchClientOperationsMixin as GeneratedOperations
from azure.batch.aio._operations._operations import _BatchClientOperationsMixin as AsyncGeneratedOperations
from azure.batch._patch import BatchExceptionPolicy, BatchSharedKeyAuthPolicy


ENDPOINT = "https://account.region.batch.azure.com"


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


def convert_file_response(*args, **kwargs):
    return kwargs["cls"](None, None, file_headers())


def create_collection_result(*args, **kwargs):
    return models.BatchCreateTaskCollectionResult(
        result_values=[
            models.BatchTaskCreateResult(task_id=task.id, status=models.BatchTaskAddStatus.SUCCESS)
            for task in kwargs["task_collection"].task_values
        ]
    )


class TestCustomizationExports(unittest.TestCase):
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
            result = self.client.create_tasks("job", tasks, service_timeout=19)
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
                self.client.create_tasks("job", [models.BatchTaskCreateOptions(id="task", command_line="echo test")])
        self.assertEqual(list(raised.exception.failure_tasks), [failure])

    def test_delete_pool_poller_completes_when_pool_disappears(self):
        with patch.object(self.client, "_delete_pool_internal", return_value=Mock()) as operation:
            with patch.object(self.client, "get_pool", side_effect=ResourceNotFoundError("gone")):
                poller = self.client.begin_delete_pool("pool", service_timeout=23, polling_interval=0)
                self.assertIsNone(poller.result(timeout=5))
        self.assertTrue(poller.done())
        self.assertEqual(operation.call_args.kwargs["service_timeout"], datetime.timedelta(seconds=23))


class TestAsyncCustomizationBehavior(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = AsyncBatchClient(ENDPOINT, named_key())
        self.addAsyncCleanup(self.client.close)

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
            result = await self.client.create_tasks("job", tasks, service_timeout=19)
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
                await self.client.create_tasks(
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
                poller = await self.client.begin_delete_pool("pool", service_timeout=23, polling_interval=0)
                self.assertIsNone(await poller.result())
        self.assertTrue(poller.done())
        self.assertEqual(operation.call_args.kwargs["service_timeout"], datetime.timedelta(seconds=23))

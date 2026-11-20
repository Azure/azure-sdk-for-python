# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Offline tests for the deployment scripts; no Azure credentials or network."""

import importlib.util
from io import BytesIO
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch
from urllib.parse import urlsplit

from azure.core.credentials import AccessToken
from azure.search.documents.indexes.models import SearchIndexerStatus
from requests import Response
from urllib3 import HTTPResponse

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BundleAssetTests(unittest.TestCase):
    def test_function_implements_shared_weather_queue_contract(self):
        class FunctionApp:
            def __init__(self):
                self.bindings = {}

            def queue_trigger(self, **kwargs):
                self.bindings["input"] = kwargs
                return lambda function: function

            def queue_output(self, **kwargs):
                self.bindings["output"] = kwargs
                return lambda function: function

        azure = types.ModuleType("azure")
        functions = types.ModuleType("azure.functions")
        functions.FunctionApp = FunctionApp
        functions.QueueMessage = object
        functions.Out = list
        azure.functions = functions
        with patch.dict(sys.modules, {"azure": azure, "azure.functions": functions}):
            module = load_module("bundle_function", ROOT / "function_app" / "function_app.py")
        message = types.SimpleNamespace(
            get_body=lambda: json.dumps(
                {
                    "function_args": {"location": "Seattle"},
                    "CorrelationId": "unit-correlation",
                }
            ).encode()
        )
        responses = []
        module.queue_trigger(message, types.SimpleNamespace(set=responses.append))
        self.assertEqual(
            json.loads(responses[0]),
            {
                "Value": "Weather is 7 degrees and sunny in Seattle",
                "CorrelationId": "unit-correlation",
            },
        )
        self.assertEqual(module.app.bindings["input"]["queue_name"], "%STORAGE_INPUT_QUEUE_NAME%")
        self.assertEqual(module.app.bindings["output"]["queue_name"], "%STORAGE_OUTPUT_QUEUE_NAME%")
        root = (ROOT / "infra" / "main.bicep").read_text()
        self.assertNotIn("inputQueueName:", root)
        self.assertNotIn("outputQueueName:", root)
        function_template = (ROOT / "infra" / "function-app.bicep").read_text()
        self.assertIn("param inputQueueName string = 'weather-input-queue'", function_template)
        self.assertIn("param outputQueueName string = 'weather-output-queue'", function_template)

    def test_search_provisions_shared_documents_without_rerunning_indexers(self):
        module = load_module("bundle_search", ROOT / "infra" / "search-indexing.py")
        calls = []

        def request(session, method, url, **kwargs):
            self.assertFalse(kwargs["allow_redirects"])
            parsed = urlsplit(url)
            self.assertIn(parsed.hostname, ("unit.search.windows.net", "unit.blob.core.windows.net"))
            body = kwargs.get("data")
            if kwargs.get("json") is not None:
                body = json.dumps(kwargs["json"])
            calls.append((method, url, body))
            response = Response()
            response.status_code = 201 if method == "PUT" else 200
            response.headers["Content-Type"] = "application/json"
            body = b"{}"
            if parsed.hostname == "unit.blob.core.windows.net":
                body = b""
            elif "/docs/search" in parsed.path:
                body = b'{"value": [{"chunk": "Contoso SmartView Glasses"}]}'
            response._content = body
            response._content_consumed = True
            response.raw = HTTPResponse(body=BytesIO(body or b""))
            return response

        configuration = {
            "searchEndpoint": "https://unit.search.windows.net",
            "storageEndpoint": "https://unit.blob.core.windows.net/",
            "containerName": "documents",
            "blobs": [
                {
                    "name": "product_info.md",
                    "content": (ROOT / "search_documents" / "product_info.md").read_text(),
                }
            ],
            "index": {"name": "index-sample"},
            "datasource": {
                "name": "datasource",
                "type": "azureblob",
                "credentials": {"connectionString": "ResourceId=/subscriptions/unit;"},
                "container": {"name": "documents"},
                "identity": {
                    "@odata.type": "#Microsoft.Azure.Search.DataUserAssignedIdentity",
                    "userAssignedIdentity": "/subscriptions/unit/identity",
                },
            },
            "skillset": {"name": "skillset", "skills": []},
            "indexers": [
                {"name": "markdown", "parameters": {"configuration": {"parsingMode": "markdown"}}},
                {"name": "documents", "parameters": {"configuration": {"parsingMode": "default"}}},
            ],
        }
        credential = Mock(spec=["get_token"])
        credential.get_token.return_value = AccessToken("offline-token", 4_000_000_000)
        with patch("requests.Session.request", autospec=True, side_effect=request), patch.object(
            module, "wait_for_indexer"
        ) as wait:
            module.provision(configuration, credential)
        self.assertEqual([call.args[1] for call in wait.call_args_list], ["markdown", "documents"])
        self.assertIn(b"SmartView Glasses", calls[0][2])
        self.assertEqual(len(calls), 7)
        for _, url, _ in calls[1:]:
            self.assertIn("api-version=2026-04-01", url)
        self.assertEqual(json.loads(calls[2][2])["identity"], configuration["datasource"]["identity"])
        self.assertEqual([call[0] for call in calls[4:6]], ["PUT", "PUT"])
        self.assertEqual(
            [json.loads(call[2])["parameters"]["configuration"]["parsingMode"] for call in calls[4:6]],
            ["markdown", "default"],
        )
        self.assertIn(
            "https://search.azure.com/.default", [call.args[0] for call in credential.get_token.call_args_list]
        )
        self.assertIn(
            "https://storage.azure.com/.default", [call.args[0] for call in credential.get_token.call_args_list]
        )
        template = (ROOT / "infra" / "ai-search.bicep").read_text()
        self.assertIn("param indexName string = 'index-sample'", template)
        self.assertIn("What features do Contoso SmartView Glasses offer?", template)
        self.assertNotIn("name: 'category'", template)

    def test_search_waits_for_automatic_initial_indexer_run(self):
        module = load_module("bundle_search", ROOT / "infra" / "search-indexing.py")
        client = Mock()
        client.get_indexer_status.side_effect = [
            SearchIndexerStatus({"lastResult": None}),
            SearchIndexerStatus({"lastResult": {"status": "inProgress", "itemsProcessed": 0}}),
            SearchIndexerStatus({"lastResult": {"status": "success", "itemsProcessed": 1}}),
        ]
        with patch.object(module.time, "sleep") as sleep:
            module.wait_for_indexer(client, "indexer")
        self.assertEqual(client.get_indexer_status.call_count, 3)
        for call in client.get_indexer_status.call_args_list:
            self.assertEqual(call.args, ("indexer",))
            self.assertTrue(0 < call.kwargs["timeout"] <= 600)
        self.assertEqual(sleep.call_count, 2)

    def test_search_accepts_initial_run_completed_before_first_poll(self):
        module = load_module("bundle_search", ROOT / "infra" / "search-indexing.py")
        client = Mock()
        client.get_indexer_status.return_value = SearchIndexerStatus(
            {"lastResult": {"status": "success", "itemsProcessed": 1}}
        )
        with patch.object(module.time, "sleep") as sleep:
            module.wait_for_indexer(client, "indexer")
        client.get_indexer_status.assert_called_once()
        sleep.assert_not_called()

    def test_search_rejects_empty_or_partially_failed_initial_runs(self):
        module = load_module("bundle_search", ROOT / "infra" / "search-indexing.py")
        for result in (
            {"status": "success", "itemsProcessed": 0},
            {"status": "success", "itemsProcessed": 1, "itemsFailed": 1},
            {
                "status": "success",
                "itemsProcessed": 1,
                "errors": [{"message": "failure"}],
            },
            {
                "status": "success",
                "itemsProcessed": 1,
                "warnings": [{"message": "warning"}],
            },
            {"status": "persistentFailure"},
        ):
            with self.subTest(result=result):
                client = Mock()
                client.get_indexer_status.return_value = SearchIndexerStatus({"lastResult": result})
                with patch.object(module.time, "sleep") as sleep:
                    with self.assertRaises(RuntimeError):
                        module.wait_for_indexer(client, "indexer")
                sleep.assert_not_called()

    def test_search_initial_run_has_bounded_readiness_wait(self):
        module = load_module("bundle_search", ROOT / "infra" / "search-indexing.py")
        client = Mock()
        client.get_indexer_status.return_value = SearchIndexerStatus({"lastResult": None})
        with patch.object(module.time, "monotonic", side_effect=[0, 0, 601]):
            with patch.object(module.time, "sleep"):
                with self.assertRaises(TimeoutError):
                    module.wait_for_indexer(client, "indexer")
        client.get_indexer_status.assert_called_once()


if __name__ == "__main__":
    unittest.main()

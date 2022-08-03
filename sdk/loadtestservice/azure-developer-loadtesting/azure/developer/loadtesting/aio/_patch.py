# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Any, TYPE_CHECKING

from azure.core import AsyncPipelineClient

from ._client import LoadTestingClient as LoadTestingClientGenerated
from ._configuration import LoadTestingClientConfiguration
from .operations import AppComponentOperations, ServerMetricsOperations, TestOperations, TestRunOperations
from .._serialization import Deserializer, Serializer

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Dict

    from azure.core.credentials_async import AsyncTokenCredential


class LoadTestingAdministration(AppComponentOperations, ServerMetricsOperations, TestOperations):
    """
    class to hold LoadTestAdministration
    """

    def __init__(self, client, config, serialize, deserialize):
        self._client = client
        self._config = config

        self._serialize = serialize
        self._deserialize = deserialize
        self._serialize.client_side_validation = False

        AppComponentOperations.__init__(self, self._client, self._config, self._serialize, self._deserialize)
        ServerMetricsOperations.__init__(self, self._client, self._config, self._serialize, self._deserialize)
        TestOperations.__init__(self, self._client, self._config, self._serialize, self._deserialize)


class LoadTestingClient(LoadTestingClientGenerated):  # pylint: disable=client-accepts-api-version-keyword
    """These APIs allow end users to create, view and run load tests using Azure Load Test Service.

    :ivar app_component: AppComponentOperations operations
    :vartype app_component: azure.developer.loadtesting.aio.operations.AppComponentOperations
    :ivar server_metrics: ServerMetricsOperations operations
    :vartype server_metrics: azure.developer.loadtesting.aio.operations.ServerMetricsOperations
    :ivar test: TestOperations operations
    :vartype test: azure.developer.loadtesting.aio.operations.TestOperations
    :ivar test_run: TestRunOperations operations
    :vartype test_run: azure.developer.loadtesting.aio.operations.TestRunOperations
    :param endpoint: URL to perform data plane API operations on the resource. Required.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure. Required.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: Api Version. Default value is "2022-06-01-preview". Note that overriding
     this default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: "AsyncTokenCredential", **kwargs: Any) -> None:
        self._config = LoadTestingClientConfiguration(endpoint=endpoint, credential=credential, **kwargs)
        self._client = AsyncPipelineClient(base_url=endpoint, config=self._config, **kwargs)

        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False

        self.load_test_runs = TestRunOperations(self._client, self._config, self._serialize, self._deserialize)
        self.load_test_administration = LoadTestingAdministration(
            self._client, self._config, self._serialize, self._deserialize
        )


__all__: List[str] = ["LoadTestingClient"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

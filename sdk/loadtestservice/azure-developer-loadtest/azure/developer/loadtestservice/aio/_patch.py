# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Any
from ._client import LoadTestClient as LoadTestClientGenerated


from azure.core import PipelineClient

from ._configuration import LoadTestClientConfiguration
from .._serialization import Deserializer, Serializer
from .operations import AppComponentOperations, ServerMetricsOperations, TestOperations, TestRunOperations


class LoadTestAdministration:
    """
    class to hold LoadTestAdministration
    """

    def __init__(self, client, config, serializer, deserializer):
        self._client = client
        self._config = config
        
        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False

        self.app_component = AppComponentOperations(self._client, self._config, self._serialize, self._deserialize)
        self.server_metrics = ServerMetricsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.test = TestOperations(  # type: ignore  # pylint: disable=abstract-class-instantiated
            self._client, self._config, self._serialize, self._deserialize
        )


class LoadTestClient(LoadTestClientGenerated):  # pylint: disable=client-accepts-api-version-keyword
    """These APIs allow end users to create, view and run load tests using Azure Load Test Service.

    :ivar app_component: AppComponentOperations operations
    :vartype app_component: azure.developer.loadtestservice.operations.AppComponentOperations
    :ivar server_metrics: ServerMetricsOperations operations
    :vartype server_metrics: azure.developer.loadtestservice.operations.ServerMetricsOperations
    :ivar test: TestOperations operations
    :vartype test: azure.developer.loadtestservice.operations.TestOperations
    :ivar test_run: TestRunOperations operations
    :vartype test_run: azure.developer.loadtestservice.operations.TestRunOperations
    :param endpoint: URL to perform data plane API operations on the resource. Required.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure. Required.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword api_version: Api Version. Default value is "2022-06-01-preview". Note that overriding
     this default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: "TokenCredential", **kwargs: Any) -> None:
        self._config = LoadTestClientConfiguration(endpoint=endpoint, credential=credential, **kwargs)
        self._client = PipelineClient(base_url=endpoint, config=self._config, **kwargs)

        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False

        self.runs = TestRunOperations(self._client, self._config, self._serialize, self._deserialize)
        self.administration = LoadTestAdministration(self._client, self._config, self._serialize, self._deserialize)


__all__: List[str] = ["LoadTestClient"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

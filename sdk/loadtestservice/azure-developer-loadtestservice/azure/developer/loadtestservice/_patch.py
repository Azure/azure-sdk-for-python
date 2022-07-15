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
from azure.core.rest import HttpRequest, HttpResponse

from ._configuration import LoadTestClientConfiguration
from ._serialization import Deserializer, Serializer
from .operations import AppComponentOperations, ServerMetricsOperations, TestOperations, TestRunOperations

class LoadTestClient(LoadTestClientGenerated):

    def __init__(self, endpoint: str, credential: "TokenCredential", **kwargs: Any) -> None:
        self._config = LoadTestClientConfiguration(endpoint=endpoint, credential=credential, **kwargs)
        self._client = PipelineClient(base_url=endpoint, config=self._config, **kwargs)

        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False
        self.app_component = AppComponentOperations(self._client, self._config, self._serialize, self._deserialize)
        self.server_metrics = ServerMetricsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.test = TestOperations(  # type: ignore  # pylint: disable=abstract-class-instantiated
            self._client, self._config, self._serialize, self._deserialize
        )
        self.test_run = TestRunOperations(self._client, self._config, self._serialize, self._deserialize)


__all__: List[str] = ["LoadTestClient"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

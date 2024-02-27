# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import uuid

from typing import Iterable
from azure.core.polling import LROPoller
from azure.ai.ml import MLClient

from .._restclient._azure_open_ai._client import MachineLearningServicesClient
from ..entities import AzureOpenAIDeployment

class AzureOpenAIDeploymentOperations():
    def __init__(self, ml_client: MLClient, ai_client: MachineLearningServicesClient, **kwargs): # pylint: disable=unused-argument
        self._ml_client = ml_client
        self._ai_client = ai_client

    def begin_create_or_update(self, deployment_name: str, deployment: AzureOpenAIDeployment) -> LROPoller[AzureOpenAIDeployment]:
        deployment_dict = deployment.serialize()
        deployment_dict["properties"]["sku"] = deployment_dict.pop("sku")

        import json
        byte_payload = json.dumps(deployment_dict).encode("utf-8")

        return self._ai_client.azure_open_ai_deployments.begin_create_or_update(
            self._ml_client.resource_group_name,
            self._ml_client.workspace_name,
            "Azure.OpenAI",
            deployment_name,
            byte_payload,
        )

    def get(self, deployment_name: str):
        return self._ai_client.azure_open_ai_deployments.get(
            self._ml_client.resource_group_name,
            self._ml_client.workspace_name,
            "Azure.OpenAI",
            deployment_name
        )

    def list(self) -> Iterable["AzureOpenAIDeployment"]:
        return self._ai_client.azure_open_ai_deployments.list_by_endpoint(
            self._ml_client.resource_group_name,
            self._ml_client.workspace_name,
            "Azure.OpenAI",
        )

    def begin_delete(self, deployment_name: str) -> LROPoller:
        return self._ai_client.azure_open_ai_deployments.begin_delete(
            self._ml_client.resource_group_name,
            self._ml_client.workspace_name,
            "Azure.OpenAI",
            deployment_name,
        )

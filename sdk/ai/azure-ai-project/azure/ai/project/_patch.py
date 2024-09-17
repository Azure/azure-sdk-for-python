# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

from ._client import ProjectClient as ProjectClientGenerated


class ProjectClient(ProjectClientGenerated):

    def get_azure_openai_client(self, *, connection_name: str, **kwargs) -> AzureOpenAI:

        response = super()._list_secrets(
            connection_name_in_url=connection_name,
            connection_name=connection_name,
            subscription_id=self._config.subscription_id,
            resource_group_name=self._config.resource_group_name,
            workspace_name=self._config.workspace_name,
            api_version_in_body=self._config.api_version,
        )

        if response.properties.auth_type == "ApiKey":
            client = AzureOpenAI(
                api_key=response.properties.credentials.key,
                api_version="2024-08-01-preview", # See https://learn.microsoft.com/en-us/azure/ai-services/openai/reference-preview#api-specs
                azure_endpoint=response.properties.target,
            )
        else:
            raise ValueError("Only API Key authentication is supported.")

        return client

__all__: List[str] = ["ProjectClient"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

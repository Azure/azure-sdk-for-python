# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import TypedDict


class AzureOpenAIModelConfigurationBase(TypedDict):
    azure_deployment: str
    azure_endpoint: str
    api_key: str


class AzureOpenAIModelConfiguration(AzureOpenAIModelConfigurationBase, total=False):
    api_version: str


class OpenAIModelConfiguration(TypedDict):
    api_key: str
    base_url: str
    organization: str


class AzureAIProject(TypedDict):
    subscription_id: str
    resource_group_name: str
    project_name: str

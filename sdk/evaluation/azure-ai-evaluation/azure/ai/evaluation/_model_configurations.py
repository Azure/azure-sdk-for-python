# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import TypedDict


class AzureOpenAIModelConfigurationBase(TypedDict):
    type: Literal["azure_openai"]
    azure_deployment: str
    azure_endpoint: str
    api_key: str


class AzureOpenAIModelConfiguration(AzureOpenAIModelConfigurationBase, total=False):
    """Model Configuration for Azure OpenAI"""
    api_version: str


class OpenAIModelConfigurationBase(TypedDict):
    type: Literal["openai"]
    api_key: str
    model: str


class OpenAIModelConfiguration(OpenAIModelConfigurationBase, total=False):
    base_url: str
    organization: str


class AzureAIProject(TypedDict):
    subscription_id: str
    resource_group_name: str
    project_name: str

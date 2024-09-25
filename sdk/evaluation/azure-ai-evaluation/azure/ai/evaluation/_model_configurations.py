# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Literal, TypedDict

from typing_extensions import NotRequired


class AzureOpenAIModelConfiguration(TypedDict, total=False):
    """Model Configuration for Azure OpenAI Model"""

    """The type of the model configuration. Should be 'azure_openai' for AzureOpenAIModelConfiguration"""
    type: Literal["azure_openai"]
    """Name of Azure OpenAI deployment to make request to"""
    azure_deployment: str
    """Endpoint of Azure OpenAI resource to make request to"""
    azure_endpoint: str
    "API key of Azure OpenAI resource"
    api_key: str
    """(Optional) API version to use in request to Azure OpenAI deployment"""
    api_version: NotRequired[str]


class OpenAIModelConfiguration(TypedDict, total=False):
    """Model Configuration for OpenAI Model"""

    """The type of the model configuration. Should be 'openai' for OpenAIModelConfiguration"""
    type: Literal["openai"]
    "API key needed to make request to model"
    api_key: str
    """Name of model to be used in OpenAI request"""
    model: str
    """(Optional) Base URL to be used in OpenAI request"""
    base_url: NotRequired[str]
    """(Optional) OpenAI organization"""
    organization: NotRequired[str]


class AzureAIProject(TypedDict):
    """Azure AI Project Information"""

    """Azure subscription id of the project"""
    subscription_id: str
    """Azure resource group name of the project"""
    resource_group_name: str
    """Azure project name"""
    project_name: str

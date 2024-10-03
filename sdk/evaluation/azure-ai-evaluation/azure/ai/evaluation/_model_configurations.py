# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Literal, TypedDict

from typing_extensions import NotRequired


class AzureOpenAIModelConfiguration(TypedDict, total=False):
    """Model Configuration for Azure OpenAI Model"""

    type: Literal["azure_openai"]
    """The type of the model configuration. Should be 'azure_openai' for AzureOpenAIModelConfiguration"""
    azure_deployment: str
    """Name of Azure OpenAI deployment to make request to"""
    azure_endpoint: str
    """Endpoint of Azure OpenAI resource to make request to"""
    api_key: str
    """API key of Azure OpenAI resource"""
    api_version: NotRequired[str]
    """(Optional) API version to use in request to Azure OpenAI deployment"""


class OpenAIModelConfiguration(TypedDict, total=False):
    """Model Configuration for OpenAI Model"""

    type: Literal["openai"]
    """The type of the model configuration. Should be 'openai' for OpenAIModelConfiguration"""
    api_key: str
    "API key needed to make request to model"
    model: str
    """Name of model to be used in OpenAI request"""
    base_url: NotRequired[str]
    """(Optional) Base URL to be used in OpenAI request"""
    organization: NotRequired[str]
    """(Optional) OpenAI organization"""


class AzureAIProject(TypedDict):
    """Azure AI Project Information"""

    subscription_id: str
    """Azure subscription id of the project"""
    resource_group_name: str
    """Azure resource group name of the project"""
    project_name: str
    """Azure project name"""

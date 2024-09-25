# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Literal, TypedDict

from typing_extensions import NotRequired


class AzureOpenAIModelConfiguration(TypedDict, total=False):
    """Model Configuration for Azure OpenAI"""
    type: Literal["azure_openai"]
    azure_deployment: str
    azure_endpoint: str
    api_key: str
    api_version: NotRequired[str]


class OpenAIModelConfiguration(TypedDict, total=False):
    type: Literal["openai"]
    api_key: str
    model: str
    base_url: NotRequired[str]
    organization: NotRequired[str]


class AzureAIProject(TypedDict):
    subscription_id: str
    resource_group_name: str
    project_name: str

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, List, Literal, TypedDict, Union

from typing_extensions import NotRequired


class AzureOpenAIModelConfiguration(TypedDict):
    """Model configuration for Azure OpenAI models

    :param type: The type of the model configuration. Should be 'azure_openai' for AzureOpenAIModelConfiguration
    :type type: NotRequired[Literal["azure_openai"]]
    :param azure_deployment: Name of Azure OpenAI deployment to make requests to
    :type azure_deployment: str
    :param azure_endpoint: Endpoint of Azure OpenAI resource to make requests to
    :type azure_endpoint: str
    :param api_key: API key of Azure OpenAI resource
    :type api_key: str
    :param api_version: API version to use in request to Azure OpenAI deployment. Optional.
    :type api_version: NotRequired[str]

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_common.py
            :start-after: [START create_AOAI_model_config]
            :end-before: [END create_AOAI_model_config]
            :language: python
            :dedent: 8
            :caption: Creating an AzureOpenAIModelConfiguration object.

    """

    type: NotRequired[Literal["azure_openai"]]
    azure_deployment: str
    azure_endpoint: str
    """Endpoint of Azure OpenAI resource to make request to"""
    api_key: NotRequired[str]
    """API key of Azure OpenAI resource"""
    api_version: NotRequired[str]


class OpenAIModelConfiguration(TypedDict):
    """Model configuration for OpenAI models

    :param type: The type of the model configuration. Should be 'openai' for OpenAIModelConfiguration
    :type type: NotRequired[Literal["openai"]]
    :param api_key: API key needed to make requests to model
    :type api_key: str
    :param model: Name of model to be used in OpenAI request
    :type model: str
    :param base_url: Base URL to be used in OpenAI request. Optional.
    :type base_url: NotRequired[str]
    :param organization: OpenAI organization. Optional.
    :type organization: NotRequired[str]

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_common.py
            :start-after: [START create_OAI_model_config]
            :end-before: [END create_OAI_model_config]
            :language: python
            :dedent: 8
            :caption: Creating an OpenAIModelConfiguration object.

    """

    type: NotRequired[Literal["openai"]]
    api_key: str
    model: str
    base_url: NotRequired[str]
    organization: NotRequired[str]


class AzureAIProject(TypedDict):
    """Information about the Azure AI project

    :param subscription_id: ID of the Azure subscription the project is in
    :type subscription_id: str
    :param resource_group_name: Name of the Azure resource group the project is in
    :type resource_group_name: str
    :param project_name: Name of the Azure project
    :type project_name: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_common.py
            :start-after: [START create_azure_ai_project_object]
            :end-before: [END create_azure_ai_project_object]
            :language: python
            :dedent: 8
            :caption: Creating an AzureAIProject object.

    """

    subscription_id: str
    resource_group_name: str
    project_name: str


class EvaluatorConfig(TypedDict, total=False):
    """Configuration for an evaluator"""

    column_mapping: Dict[str, str]
    """Dictionary mapping evaluator input name to column in data"""


class Message(TypedDict):
    role: str
    content: Union[str, List[Dict]]
    context: NotRequired[Dict[str, Any]]


class Conversation(TypedDict):
    messages: Union[List[Message], List[Dict]]
    context: NotRequired[Dict[str, Any]]


class EvaluationResult(TypedDict):
    metrics: Dict
    studio_url: NotRequired[str]
    rows: List[Dict]

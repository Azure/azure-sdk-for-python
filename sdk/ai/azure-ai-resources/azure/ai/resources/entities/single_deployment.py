# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from dataclasses import dataclass
from typing import Dict, Union, Optional

from azure.ai.ml.entities import OnlineEndpoint, OnlineDeployment

from .models import Model, PromptflowModel


@dataclass
class SingleDeployment:
    """
    A model deployment.

    :param name: The name of the deployment.
    :type name: str
    :param model: The model to be deployed. This can be a model ID, a Model object, or a promptflow model.
    :type model: Union[str, ~azure.ai.resources.entities.models.Model, ~azure.ai.resources.entities.models.PromptflowModel]
    :param app_insights_enabled: Whether to enable application insights. Defaults to True.
    :type app_insights_enabled: bool
    :param data_collector_enabled: Whether to enable data collection. Defaults to True.
    :type data_collector_enabled: bool
    :param endpoint_name: The name of the endpoint to deploy to.
    :type endpoint_name: Optional[str]
    :param environment_variables: The environment variables for the deployment.
    :type environment_variables: Optional[Dict[str, str]]
    :param instance_type: The instance type for the deployment.
    :type instance_type: Optional[str]
    :param instance_count: The number of instances for the deployment. Defaults to "1".
    :type instance_count: str
    :param scoring_uri: The scoring URI for the deployment.
    :type scoring_uri: Optional[str]
    :param properties: The properties of the deployment.
    :type properties: Optional[Dict[str, str]]
    :param tags: The tags of the deployment.
    :type tags: Optional[Dict[str, str]]
    """
    name: str
    model: Union[str, Model, PromptflowModel]
    app_insights_enabled: bool = True
    data_collector_enabled: bool = True
    endpoint_name: Optional[str] = None
    environment_variables: Optional[Dict[str, str]] = None
    instance_type: Optional[str] = None
    instance_count: str = "1"
    scoring_uri: Optional[str] = None
    properties: Optional[Dict[str, str]] = None
    tags: Optional[Dict[str, str]] = None


    @classmethod
    def _from_v2_endpoint_deployment(cls, endpoint: OnlineEndpoint, deployment: OnlineDeployment) -> "SingleDeployment":
        return cls(
            name=deployment.name,
            model=deployment.model,
            endpoint_name=deployment.endpoint_name,
            environment_variables=deployment.environment_variables,
            instance_type=deployment.instance_type,
            instance_count=deployment.instance_count,
            app_insights_enabled=deployment.app_insights_enabled,
            tags=deployment.tags,
            properties=deployment.properties,
            scoring_uri=endpoint.scoring_uri,
        )

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from dataclasses import dataclass
from typing import Dict, Union

from azure.ai.ml.entities import OnlineEndpoint, OnlineDeployment

from .models import Model, PromptflowModel


@dataclass
class Deployment:
    name: str
    model: Union[str, Model, PromptflowModel]
    app_insights_enabled: bool = True
    data_collector_enabled: bool = True
    endpoint_name: str = None
    environment_variables: Dict[str, str] = None
    instance_type: str = None
    instance_count: str = 1
    scoring_uri: str = None
    properties: Dict[str, str] = None
    tags: Dict[str, str] = None


    @classmethod
    def _from_v2_endpoint_deployment(cls, endpoint: OnlineEndpoint, deployment: OnlineDeployment) -> "Deployment":
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

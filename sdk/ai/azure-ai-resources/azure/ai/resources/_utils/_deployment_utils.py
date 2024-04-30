# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
from typing import Any, Dict, Tuple, Optional, List

from azure.ai.ml.entities import Model

from ._registry_utils import get_registry_model


def get_empty_deployment_arm_template():
    return {
        "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "onlineEndpointProperties": {
                "defaultValue": {
                    "authMode": "Key",
                    "publicNetworkAccess": "Enabled",
                    "properties": {
                        "enforce_access_to_default_secret_stores": "enabled"
                    },
                },
                "type": "Object",
            },
            "onlineEndpointPropertiesTrafficUpdate": {
                "defaultValue": {
                    "traffic": {"[parameters('onlineDeploymentName')]": 100},
                    "authMode": "Key",
                    "publicNetworkAccess": "Enabled",
                    "properties": {
                        "enforce_access_to_default_secret_stores": "enabled"
                    },
                },
                "type": "Object",
            },
        },
        "resources": [
            {
                "type": "Microsoft.MachineLearningServices/workspaces/onlineEndpoints",
                "apiVersion": "2023-04-01-Preview",
                "name": "[concat(parameters('workspaceName'), '/', parameters('onlineEndpointName'))]",
                "location": "[parameters('location')]",
                "identity": {"type": "SystemAssigned"},
                "properties": "[parameters('onlineEndpointProperties')]",
                "copy": {"name": "onlineEndpointCopy", "count": 1, "mode": "serial"},
            },
            {
                "type": "Microsoft.MachineLearningServices/workspaces/onlineEndpoints/deployments",
                "apiVersion": "2023-04-01-Preview",
                "name": "[concat(parameters('workspaceName'), '/', parameters('onlineEndpointName'), '/', parameters('onlineDeploymentName'))]",
                "location": "[parameters('location')]",
                "dependsOn": [
                    "onlineEndpointCopy",
                ],
                "sku": {"capacity": "[parameters('deploymentInstanceCount')]", "name": "default"},
                "identity": {"type": "None"},
                "properties": "[parameters('onlineDeploymentProperties')]",
                "copy": {"name": "onlineDeploymentCopy", "count": 1, "mode": "serial"},
            },
            {
                "type": "Microsoft.Resources/deployments",
                "apiVersion": "2015-01-01",
                "name": "[concat('updateEndpointWithTraffic', '-', parameters('onlineEndpointName'))]",
                "dependsOn": ["onlineDeploymentCopy"],
                "properties": {
                    "mode": "Incremental",
                    "template": {
                        "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
                        "contentVersion": "1.0.0.0",
                        "resources": [
                            {
                                "type": "Microsoft.MachineLearningServices/workspaces/onlineEndpoints",
                                "apiVersion": "2023-04-01-Preview",
                                "location": "[parameters('location')]",
                                "name": "[concat(parameters('workspaceName'), '/', parameters('onlineEndpointName'))]",
                                "properties": "[parameters('onlineEndpointPropertiesTrafficUpdate')]",
                                "identity": {"type": "SystemAssigned"},
                            }
                        ],
                    },
                },
            },
        ],
        "outputs": {
            "online_endpoint_name": {
                "type": "string",
                "value": "[parameters('onlineEndpointName')]",
            },
            "online_deployment_name": {
                "type": "string",
                "value": "[parameters('onlineDeploymentName')]",
            },
        },
    }


def get_default_allowed_instance_type_for_hugging_face(
    model_details: Model, credential: Any
) -> Tuple[Optional[Any], List[Any]]:
    hf_engines = model_details.properties.get("skuBasedEngineIds", None)
    deployment_config = model_details.properties.get("modelDeploymentConfig", None)
    default_instance_type = None
    allowed_instance_types = []
    if hf_engines:
        # hf engines and deployment_config are mutually exclusive
        # the presence of one implies the other does not exist
        hf_engines = hf_engines.split(",")
        if len(hf_engines) > 1:
            for engine_id in hf_engines:
                (
                    instance_type,
                    instance_type_list,
                ) = get_default_allowed_instance_type_from_model_engine(
                    engine_id, credential
                )
                if "cpu" in engine_id:
                    default_instance_type = instance_type
                allowed_instance_types.append(instance_type_list)
        else:
            # if the model has only one engine, we can proceed with that as the default engine for SKU
            # selection
            (
                default_instance_type,
                allowed_instance_types,
            ) = get_default_allowed_instance_type_from_model_engine(
                hf_engines[0], credential
            )
    else:
        default_instance_type, allowed_instance_types = parse_deployment_config(
            deployment_config
        )
    return (default_instance_type, allowed_instance_types)


def parse_deployment_config(deployment_config: str):
    deployment_config_dict: Dict[str, Any] = json.loads(deployment_config)
    allowed_instance_types = deployment_config_dict["PipelineMetadata"][
        "PipelineDefinition"
    ]["ec"]["AllowedInstanceTypes"]
    default_instance_type = deployment_config_dict["PipelineMetadata"]["PipelineDefinition"][
        "ec"
    ]["DefaultInstanceType"]

    return (default_instance_type, allowed_instance_types)


def get_default_allowed_instance_type_from_model_engine(
    engine_id: str, credential: Any
):
    model_details = get_registry_model(credential, id=engine_id)
    deployment_config = model_details.properties.get("modelDeploymentConfig", None)
    return parse_deployment_config(deployment_config)

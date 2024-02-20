# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import path
from typing import Any, Dict

from azure.ai.ml._utils.utils import load_json
from azure.ai.ml.constants._common import ArmConstants, AzureMLResourceType
from azure.ai.ml.exceptions import ErrorTarget, ValidationException

template_mapping = {
    ArmConstants.BASE_TYPE: "base_template.json",
    ArmConstants.CODE_TYPE: "code.json",
    ArmConstants.CODE_VERSION_TYPE: "code_version.json",
    ArmConstants.ENVIRONMENT_VERSION_TYPE: "environment_version.json",
    ArmConstants.MODEL_VERSION_TYPE: "model_version.json",
    ArmConstants.MODEL_TYPE: "model.json",
    ArmConstants.ONLINE_ENDPOINT_TYPE: "online_endpoint.json",
    ArmConstants.ONLINE_DEPLOYMENT_TYPE: "online_deployment.json",
    ArmConstants.UPDATE_ONLINE_ENDPOINT_TYPE: "update_online_endpoint.json",
    ArmConstants.WORKSPACE_BASE: "workspace_base.json",
    ArmConstants.WORKSPACE_PARAM: "workspace_param.json",
    ArmConstants.FEATURE_STORE_ROLE_ASSIGNMENTS: "feature_store_role_assignments.json",
    ArmConstants.FEATURE_STORE_ROLE_ASSIGNMENTS_PARAM: "feature_store_role_assignments_param.json",
    ArmConstants.WORKSPACE_PROJECT: "workspace_project.json",
}


deployment_message_mapping = {
    ArmConstants.CODE_TYPE: "Registering code: ({0})",
    AzureMLResourceType.CODE: "Registering code version: ({0})",
    ArmConstants.CODE_VERSION_TYPE: "Registering code version: ({0})",
    ArmConstants.ENVIRONMENT_VERSION_TYPE: "Registering environment version: ({0})",
    AzureMLResourceType.ENVIRONMENT: "Registering environment version: ({0})",
    ArmConstants.MODEL_VERSION_TYPE: "Registering model version: ({0})",
    ArmConstants.MODEL_TYPE: "Registering model: ({0})",
    AzureMLResourceType.MODEL: "Registering model version: ({0})",
    ArmConstants.ONLINE_ENDPOINT_TYPE: "Creating endpoint: {0}",
    ArmConstants.ONLINE_DEPLOYMENT_TYPE: "Creating or updating deployment: {0}",
    AzureMLResourceType.DEPLOYMENT: "Creating or updating deployment: {0}",
    ArmConstants.UPDATE_ONLINE_ENDPOINT_TYPE: "Updating traffic",
    ArmConstants.KEY_VAULT_PARAMETER_NAME: "Creating Key Vault: ({0})",
    ArmConstants.LOG_ANALYTICS: "Creating Log Analytics Workspace: ({0})",
    ArmConstants.APP_INSIGHTS_PARAMETER_NAME: "Creating Application Insights: ({0})",
    ArmConstants.CONTAINER_REGISTRY_PARAMETER_NAME: "Creating Container Registry: ({0})",
    ArmConstants.STORAGE_ACCOUNT_PARAMETER_NAME: "Creating Storage Account: ({0})",
    AzureMLResourceType.WORKSPACE: "Creating AzureML Workspace: ({0})",
    AzureMLResourceType.CONNECTIONS: "Creating connection: ({0})",
    ArmConstants.USER_ASSIGNED_IDENTITIES: "Creating User Assigned Identities: ({0})",
}


def get_template(resource_type: str) -> Dict[str, Any]:
    if resource_type not in template_mapping:
        msg = "can't find the template for the resource {}".format(resource_type)
        raise ValidationException(message=msg, no_personal_data_message=msg, target=ErrorTarget.ARM_RESOURCE)
    template_path = path.join(path.dirname(__file__), "arm_templates", template_mapping[resource_type])
    return load_json(file_path=template_path)

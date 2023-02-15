# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from azure.ai.ml._azure_environments import _get_base_url_from_metadata
from azure.ai.ml._vendor.azure_resources._resource_management_client import ResourceManagementClient
from azure.ai.ml.constants._common import ArmConstants
from azure.core.credentials import TokenCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.ml.constants._workspace import AppInsightsDefaults

module_logger = logging.getLogger(__name__)


def default_resource_group_for_app_insights_exists(
    credentials: TokenCredential, subscription_id: str, location: str
) -> bool:
    client = ResourceManagementClient(
        credential=credentials,
        subscription_id=subscription_id,
        base_url=_get_base_url_from_metadata(),
        api_version=ArmConstants.AZURE_MGMT_RESOURCE_API_VERSION,
    )
    default_rgName = AppInsightsDefaults.DEFAULT_RESOURCE_GROUP_NAME.format(location=location)
    try:
        client.resource_groups.get(resource_group_name=default_rgName)
        return True
    except HttpResponseError:
        return False


def default_log_analytics_workspace_exists(credentials: TokenCredential, subscription_id: str, location: str) -> bool:
    client = ResourceManagementClient(
        credential=credentials,
        subscription_id=subscription_id,
        base_url=_get_base_url_from_metadata(),
        api_version=ArmConstants.AZURE_MGMT_RESOURCE_API_VERSION,
    )
    default_resource_group = AppInsightsDefaults.DEFAULT_RESOURCE_GROUP_NAME.format(location=location)
    default_workspace = client.resources.list_by_resource_group(
        default_resource_group,
        filter=f"substringof('{AppInsightsDefaults.DEFAULT_LOG_ANALYTICS_NAME.format(location=location)}',name)",
    )
    for item in default_workspace:  # pylint: disable=unused-variable
        # return true for is_existing
        return True
    # else return false for is_existing
    return False


def get_default_log_analytics_arm_id(subscription_id: str, location: str) -> str:
    return (
        f"/subscriptions/{subscription_id}/"
        f"resourceGroups/{AppInsightsDefaults.DEFAULT_RESOURCE_GROUP_NAME.format(location=location)}/"
        "providers/Microsoft.OperationalInsights/workspaces/"
        f"{AppInsightsDefaults.DEFAULT_LOG_ANALYTICS_NAME.format(location=location)}"
    )


def get_default_resource_group_deployment(deployment_name: str, location: str, subscription_id: str) -> dict:
    return {
        "type": "Microsoft.Resources/deployments",
        "apiVersion": "2019-10-01",
        "name": deployment_name,
        "subscriptionId": subscription_id,
        "location": location,
        "properties": {
            "mode": "Incremental",
            "template": {
                "$schema": (
                    "https://schema.management.azure.com/schemas/2018-05-01/" + "subscriptionDeploymentTemplate.json#"
                ),
                "contentVersion": "1.0.0.1",
                "parameters": {},
                "variables": {},
                "resources": [
                    {
                        "type": "Microsoft.Resources/resourceGroups",
                        "apiVersion": "2018-05-01",
                        "location": location,
                        "name": AppInsightsDefaults.DEFAULT_RESOURCE_GROUP_NAME.format(location=location),
                        "properties": {},
                    }
                ],
            },
        },
    }


def get_default_log_analytics_deployment(deployment_name: str, location: str, subscription_id: str) -> dict:
    return {
        "type": "Microsoft.Resources/deployments",
        "apiVersion": "2019-10-01",
        "name": deployment_name,
        "resourceGroup": AppInsightsDefaults.DEFAULT_RESOURCE_GROUP_NAME.format(location=location),
        "subscriptionId": subscription_id,
        "properties": {
            "mode": "Incremental",
            "template": {
                "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
                "contentVersion": "1.0.0.0",
                "parameters": {},
                "variables": {},
                "resources": [
                    {
                        "apiVersion": "2020-08-01",
                        "name": AppInsightsDefaults.DEFAULT_LOG_ANALYTICS_NAME.format(location=location),
                        "type": "Microsoft.OperationalInsights/workspaces",
                        "location": location,
                        "properties": {},
                    }
                ],
            },
        },
    }

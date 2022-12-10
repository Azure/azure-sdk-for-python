# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import random
import uuid
from typing import Tuple

from azure.ai.ml._azure_environments import _get_base_url_from_metadata
from azure.ai.ml._vendor.azure_resources._resource_management_client import ResourceManagementClient
from azure.ai.ml.constants._common import ArmConstants
from azure.core.credentials import TokenCredential

module_logger = logging.getLogger(__name__)


def get_default_resource_group_for_app_insights(credentials: TokenCredential, subscription_id: str, location: str):
    client = ResourceManagementClient(
        credential=credentials,
        subscription_id=subscription_id,
        base_url=_get_base_url_from_metadata(),
        api_version=ArmConstants.AZURE_MGMT_RESOURCE_API_VERSION,
    )
    default_rgName = get_default_resource_group_name(location)
    # rgs = client.resource_groups.get("""try to get the default resource group""")
    try:
        rgs = client.resource_groups.get(resource_group_name=default_rgName)
        return rgs.name
    except:
        created_rg = client.resource_groups.create_or_update(default_rgName, {"location":location})
        return created_rg.name


def get_default_log_analytics_workspace(credentials: TokenCredential, subscription_id: str, location: str) -> Tuple[str, bool]:
    client = ResourceManagementClient(
        credential=credentials,
        subscription_id=subscription_id,
        base_url=_get_base_url_from_metadata(),
        api_version=ArmConstants.AZURE_MGMT_RESOURCE_API_VERSION,
    )
    default_resource_group = get_default_resource_group_for_app_insights(credentials, subscription_id, location)
    default_workspace = client.resources.list_by_resource_group(
        default_resource_group,
        filter="substringof('%s',name)"%get_default_log_analytics_name(subscription_id, location)
    )
    for item in default_workspace:
        # return arm id of log analytics workspace, true for is_existing
        return (item.id, True)
    # else return arm id for to be created log analytics workspace, false for is_existing
    return (
        '/subscriptions/%s/resourceGroups/%s/providers/Microsoft.OperationalInsights/workspaces/%s'%(subscription_id, default_resource_group, get_default_log_analytics_name(subscription_id, location)), 
        False)


def get_log_analytics_deployment(deployment_name: str, location: str, subscription_id: str) -> dict:
    return {
            "type": "Microsoft.Resources/deployments",
            "apiVersion": "2019-10-01",
            "name": deployment_name,
            "resourceGroup": get_default_resource_group_name(location),
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
                            "name": get_default_log_analytics_name(subscription_id, location),
                            "type": "Microsoft.OperationalInsights/workspaces",
                            "location": "[if(or(equals(parameters('applicationInsightsLocation'),'westcentralus'), equals(parameters('applicationInsightsLocation'),'eastus2euap'), equals(parameters('applicationInsightsLocation'),'centraluseuap')),'southcentralus',parameters('applicationInsightsLocation'))]",
                            "properties": {}
                        }
                    ]
                }
            }
        }


def get_default_log_analytics_name(subscription_id: str, location: str) -> str:
    logWorkspaceName = "DefaultWorkspace-%s-%s"%(subscription_id,get_la_region_code(location))
    return logWorkspaceName if len(logWorkspaceName) < 63 else logWorkspaceName[0,62]


def get_default_resource_group_name(location: str) -> str:
    return "DefaultResourceGroup-%s"%get_la_region_code(location)


def get_la_region_code(location: str) -> str:
    if location in ["westcentralus", "eastus2euap", "centraluseuap"]:
        return region_mapping["regions"]["southcentralus"]["laRegionCode"]
    try: 
        region = region_mapping["regions"][location.lower()]
        return region["laRegionCode"] if region["laRegionCode"]!="" else location
    except: 
        return location


region_mapping = {
    "regions": {
        "centralus": {
            "geo": "unitedstates",
            "pairedRegions": [
                "eastus2",
                "eastus"
            ],
            "laRegionCode": "CUS"
        },
        "eastus2": {
            "geo": "unitedstates",
            "pairedRegions": [
                "centralus",
                "eastus"
            ],
            "laRegionCode": "EUS2"
        },
        "eastus": {
            "geo": "unitedstates",
            "pairedRegions": [
                "westus"
            ],
            "laRegionCode": "EUS"
        },
        "northcentralus": {
            "geo": "unitedstates",
            "pairedRegions": [
                "southcentralus"
            ],
            "laRegionCode": "NCUS"
        },
        "southcentralus": {
            "geo": "unitedstates",
            "pairedRegions": [
                "northcentralus"
            ],
            "laRegionCode": "SCUS"
        },
        "westus2": {
            "geo": "unitedstates",
            "pairedRegions": [
                "westcentralus"
            ],
            "laRegionCode": "WUS2"
        },
        "westus3": {
            "geo": "unitedstates",
            "pairedRegions": [
                "westus2"
            ],
            "laRegionCode": "USW3"
        },
        "westcentralus": {
            "geo": "unitedstates",
            "pairedRegions": [
                "westus2"
            ],
            "laRegionCode": "WCUS"
        },
        "westus": {
            "geo": "unitedstates",
            "pairedRegions": [
                "eastus"
            ],
            "laRegionCode": "WUS"
        },
        "canadacentral": {
            "geo": "canada",
            "pairedRegions": [
                "canadaeast"
            ],
            "laRegionCode": "CCAN"
        },
        "canadaeast": {
            "geo": "canada",
            "pairedRegions": [
                "canadacentral"
            ],
            "laRegionCode": "ECAN"
        },
        "brazilsouth": {
            "geo": "brazil",
            "pairedRegions": [
                "southcentralus"
            ],
            "laRegionCode": "CQ"
        },
        "eastasia": {
            "geo": "asiapacific",
            "pairedRegions": [
                "southeastasia"
            ],
            "laRegionCode": "EA"
        },
        "southeastasia": {
            "geo": "asiapacific",
            "pairedRegions": [
                "eastasia"
            ],
            "laRegionCode": "SEA"
        },
        "australiacentral": {
            "geo": "australia",
            "pairedRegions": [
                "australiacentral2",
                "australiaeast"
            ],
            "laRegionCode": "CAU"
        },
        "australiacentral2": {
            "geo": "australia",
            "pairedRegions": [
                "australiacentral",
                "australiaeast"
            ],
            "laRegionCode": "CBR2"
        },
        "australiaeast": {
            "geo": "australia",
            "pairedRegions": [
                "australiasoutheast"
            ],
            "laRegionCode": "EAU"
        },
        "australiasoutheast": {
            "geo": "australia",
            "pairedRegions": [
                "australiaeast"
            ],
            "laRegionCode": "SEAU"
        },
        "chinaeast": {
            "geo": "china",
            "pairedRegions": [
                "chinanorth",
                "chinaeast2"
            ],
            "laRegionCode": ""
        },
        "chinanorth": {
            "geo": "china",
            "pairedRegions": [
                "chinaeast",
                "chinaeast2"
            ],
            "laRegionCode": ""
        },
        "chinaeast2": {
            "geo": "china",
            "pairedRegions": [
                "chinanorth2"
            ],
            "laRegionCode": "CNE2"
        },
        "chinanorth2": {
            "geo": "china",
            "pairedRegions": [
                "chinaeast2"
            ],
            "laRegionCode": ""
        },
        "chinaeast3": {
            "geo": "china",
            "pairedRegions": [
                "chinanorth3"
            ],
            "laRegionCode": "CNE3"
        },
        "chinanorth3": {
            "geo": "china",
            "pairedRegions": [
                "chinaeast3"
            ],
            "laRegionCode": "CNN3"
        },
        "centralindia": {
            "geo": "india",
            "pairedRegions": [
                "southindia"
            ],
            "laRegionCode": "CID"
        },
        "southindia": {
            "geo": "india",
            "pairedRegions": [
                "centralindia"
            ],
            "laRegionCode": ""
        },
        "westindia": {
            "geo": "india",
            "pairedRegions": [
                "southindia",
                "centralindia"
            ],
            "laRegionCode": ""
        },
        "jioindiacentral": {
            "geo": "india",
            "pairedRegions": [],
            "laRegionCode": "JINC"
        },
        "jioindiawest": {
            "geo": "india",
            "pairedRegions": [],
            "laRegionCode": "JINW"
        },
        "japaneast": {
            "geo": "japan",
            "pairedRegions": [
                "japanwest"
            ],
            "laRegionCode": "EJP"
        },
        "japanwest": {
            "geo": "japan",
            "pairedRegions": [
                "japaneast"
            ],
            "laRegionCode": "OS"
        },
        "koreacentral": {
            "geo": "korea",
            "pairedRegions": [
                "koreasouth"
            ],
            "laRegionCode": "SE"
        },
        "koreasouth": {
            "geo": "korea",
            "pairedRegions": [
                "koreacentral"
            ],
            "laRegionCode": ""
        },
        "northeurope": {
            "geo": "europe",
            "pairedRegions": [
                "westeurope"
            ],
            "laRegionCode": "NEU"
        },
        "westeurope": {
            "geo": "europe",
            "pairedRegions": [
                "northeurope"
            ],
            "laRegionCode": "WEU"
        },
        "francecentral": {
            "geo": "france",
            "pairedRegions": [
                "francesouth"
            ],
            "laRegionCode": "PAR"
        },
        "francesouth": {
            "geo": "france",
            "pairedRegions": [
                "francecentral"
            ],
            "laRegionCode": ""
        },
        "uksouth": {
            "geo": "unitedkingdom",
            "pairedRegions": [
                "ukwest"
            ],
            "laRegionCode": "SUK"
        },
        "ukwest": {
            "geo": "unitedkingdom",
            "pairedRegions": [
                "uksouth"
            ],
            "laRegionCode": "WUK"
        },
        "germanycentral": {
            "geo": "germany",
            "pairedRegions": [
                "germanynortheast"
            ],
            "laRegionCode": ""
        },
        "germanynortheast": {
            "geo": "germany",
            "pairedRegions": [
                "germanycentral"
            ],
            "laRegionCode": ""
        },
        "germanywestcentral": {
            "geo": "germany",
            "pairedRegions": [],
            "laRegionCode": "DEWC"
        },
        "germanynorth": {
            "geo": "germany",
            "pairedRegions": [],
            "laRegionCode": ""
        },
        "switzerlandwest": {
            "geo": "switzerland",
            "pairedRegions": [],
            "laRegionCode": "CHW"
        },
        "switzerlandnorth": {
            "geo": "switzerland",
            "pairedRegions": [],
            "laRegionCode": "CHN"
        },
        "swedencentral": {
            "geo": "sweden",
            "pairedRegions": [],
            "laRegionCode": "SEC"
        },
        "swedensouth": {
            "geo": "sweden",
            "pairedRegions": [],
            "laRegionCode": "SES"
        },
        "norwaywest": {
            "geo": "norway",
            "pairedRegions": [],
            "laRegionCode": ""
        },
        "norwayeast": {
            "geo": "norway",
            "pairedRegions": [],
            "laRegionCode": "NOE"
        },
        "southafricanorth": {
            "geo": "africa",
            "pairedRegions": [],
            "laRegionCode": "JNB"
        },
        "southafricawest": {
            "geo": "africa",
            "pairedRegions": [],
            "laRegionCode": ""
        },
        "uaenorth": {
            "geo": "unitedarabemirates",
            "pairedRegions": [],
            "laRegionCode": "UAEN"
        },
        "uaecentral": {
            "geo": "unitedarabemirates",
            "pairedRegions": [],
            "laRegionCode": "AUH"
        },
        "qatarcentral": {
            "geo": "qatar",
            "pairedRegions": [],
            "laRegionCode": "QAC"
        },
        "usdodcentral": {
            "geo": "azuregovernment",
            "pairedRegions": [
                "usdodeast",
                "usgovvirginia"
            ],
            "laRegionCode": ""
        },
        "usdodeast": {
            "geo": "azuregovernment",
            "pairedRegions": [
                "usdodcentral",
                "usgovvirginia"
            ],
            "laRegionCode": ""
        },
        "usgovarizona": {
            "geo": "azuregovernment",
            "pairedRegions": [
                "usgovtexas",
                "usgovvirginia"
            ],
            "laRegionCode": "PHX"
        },
        "usgoviowa": {
            "geo": "azuregovernment",
            "pairedRegions": [
                "usgovvirginia"
            ],
            "laRegionCode": ""
        },
        "usgovtexas": {
            "geo": "azuregovernment",
            "pairedRegions": [
                "usgovarizona",
                "usgovvirginia"
            ],
            "laRegionCode": ""
        },
        "usgovvirginia": {
            "geo": "azuregovernment",
            "pairedRegions": [
                "usgovtexas"
            ],
            "laRegionCode": "USBN1"
        },
        "ussecwest": {
            "geo": "azuregovernment",
            "pairedRegions": [
                "usseceast"
            ],
            "laRegionCode": "RXW"
        },
        "usseceast": {
            "geo": "azuregovernment",
            "pairedRegions": [
                "ussecwest"
            ],
            "laRegionCode": "RXE"
        },
        "usnatwest": {
            "geo": "azuregovernment",
            "pairedRegions": [
                "usnateast"
            ],
            "laRegionCode": "EXW"
        },
        "usnateast": {
            "geo": "azuregovernment",
            "pairedRegions": [
                "usnatwest"
            ],
            "laRegionCode": "EXE"
        }
    }
}
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import uuid
import random
import logging

from azure.ai.ml._vendor.azure_resources._resource_management_client import ResourceManagementClient
from azure.ai.ml.constants import ArmConstants
from azure.identity import ChainedTokenCredential
from azure.ai.ml._azure_environments import _get_base_url_from_metadata


module_logger = logging.getLogger(__name__)


def get_name_for_dependent_resource(workspace_name: str, resource_type: str) -> str:
    alphabets_str = ""
    for char in workspace_name.lower():
        if char.isalpha() or char.isdigit():
            alphabets_str = alphabets_str + char
    rand_str = str(uuid.uuid4()).replace("-", "")
    resource_name = alphabets_str[:8] + resource_type[:8] + rand_str
    return resource_name[:24]


def get_deployment_name(name: str):
    random.seed(version=2)
    return f"{name}-{random.randint(1, 10000000)}"


def get_resource_group_location(
    credentials: ChainedTokenCredential, subscription_id: str, resource_group_name: str
) -> str:
    client = ResourceManagementClient(
        credential=credentials,
        subscription_id=subscription_id,
        base_url=_get_base_url_from_metadata(),
        api_version=ArmConstants.AZURE_MGMT_RESOURCE_API_VERSION,
    )
    rg = client.resource_groups.get(resource_group_name)
    return rg.location


def delete_resource_by_arm_id(
    credentials: ChainedTokenCredential, subscription_id: str, arm_id: str, api_version: str
) -> None:
    if arm_id:
        client = ResourceManagementClient(
            credential=credentials,
            subscription_id=subscription_id,
            base_url=_get_base_url_from_metadata(),
            api_version=ArmConstants.AZURE_MGMT_RESOURCE_API_VERSION,
        )
        client.resources.begin_delete_by_id(arm_id, api_version)


def get_resource_and_group_name(armstr: str) -> str:
    return armstr.split("/")[-1], armstr.split("/")[-5]


def get_endpoint_parts(arm_id: str, subnet_arm_id: str) -> ():
    arm_id_parts = arm_id.split("/")
    subnet_id_parts = subnet_arm_id.split("/")
    conn_name = arm_id_parts[-1]
    subscription_id = arm_id_parts[2]
    resource_group = arm_id_parts[4]
    vnet_name = subnet_id_parts[-3]
    subnet_name = subnet_id_parts[-1]
    return conn_name, subscription_id, resource_group, vnet_name, subnet_name

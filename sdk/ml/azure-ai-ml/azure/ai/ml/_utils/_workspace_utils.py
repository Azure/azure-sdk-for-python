# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import random
import uuid
from typing import Any

from azure.ai.ml._azure_environments import _get_base_url_from_metadata, _resource_to_scopes
from azure.ai.ml._vendor.azure_resources._resource_management_client import ResourceManagementClient
from azure.ai.ml._vendor.azure_resources.models import GenericResource
from azure.ai.ml.constants._common import ArmConstants
from azure.core.credentials import TokenCredential

module_logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------
# THROWAWAY SHIM (remove once the shared arm_ml_service client declares these workspace properties).
#
# allowRoleAssignmentOnRG and networkAcls are valid on the 2024-10-01-preview wire contract but were
# marked @removed at api-version 2025-12-01 in the TypeSpec. The shared arm_ml_service client is
# generated at 2025-12-01, so its Workspace / WorkspaceUpdateParameters hybrid models do not declare
# these properties and reject them as constructor kwargs. The hybrid models flatten everything under a
# `properties` envelope on the wire, so we round-trip the removed properties through that envelope.
# ------------------------------------------------------------------------------------------------
def set_removed_workspace_property(rest_obj: Any, wire_key: str, value: Any) -> None:
    """Place a property the arm_ml_service model no longer declares onto the flattened wire envelope.

    :param rest_obj: A hybrid arm_ml_service Workspace / WorkspaceUpdateParameters model.
    :type rest_obj: Any
    :param wire_key: The camelCase wire key (e.g. "allowRoleAssignmentOnRG", "networkAcls").
    :type wire_key: str
    :param value: The value to serialize. Nested models must already be converted via ``as_dict()``.
    :type value: Any
    """
    if value is None:
        return
    properties = rest_obj.get("properties") or {}
    properties[wire_key] = value
    rest_obj["properties"] = properties


def get_removed_workspace_property(rest_obj: Any, wire_key: str) -> Any:
    """Read a property the arm_ml_service model no longer declares from the flattened wire envelope.

    :param rest_obj: A hybrid arm_ml_service Workspace model.
    :type rest_obj: Any
    :param wire_key: The camelCase wire key (e.g. "allowRoleAssignmentOnRG", "networkAcls").
    :type wire_key: str
    :return: The raw value from the wire envelope, or None if absent.
    :rtype: Any
    """
    getter = getattr(rest_obj, "get", None)
    if not callable(getter):
        return None
    properties = rest_obj.get("properties")
    if not properties:
        return None
    return properties.get(wire_key)


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


def get_resource_group_location(credentials: TokenCredential, subscription_id: str, resource_group_name: str) -> str:
    arm_hostname = _get_base_url_from_metadata()
    client = ResourceManagementClient(
        credential=credentials,
        subscription_id=subscription_id,
        base_url=arm_hostname,
        api_version=ArmConstants.AZURE_MGMT_RESOURCE_API_VERSION,
        credential_scopes=_resource_to_scopes(arm_hostname),
    )
    rg = client.resource_groups.get(resource_group_name)
    return rg.location


def get_generic_arm_resource_by_arm_id(
    credentials: TokenCredential,
    subscription_id: str,
    arm_id: str,
    api_version: str,
) -> GenericResource:
    if arm_id:
        arm_hostname = _get_base_url_from_metadata()
        client = ResourceManagementClient(
            credential=credentials,
            subscription_id=subscription_id,
            base_url=arm_hostname,
            api_version=ArmConstants.AZURE_MGMT_RESOURCE_API_VERSION,
            credential_scopes=_resource_to_scopes(arm_hostname),
        )
        return client.resources.get_by_id(arm_id, api_version)
    return None


def delete_resource_by_arm_id(
    credentials: TokenCredential,
    subscription_id: str,
    arm_id: str,
    api_version: str,
) -> None:
    if arm_id:
        arm_hostname = _get_base_url_from_metadata()
        client = ResourceManagementClient(
            credential=credentials,
            subscription_id=subscription_id,
            base_url=arm_hostname,
            api_version=ArmConstants.AZURE_MGMT_RESOURCE_API_VERSION,
            credential_scopes=_resource_to_scopes(arm_hostname),
        )
        client.resources.begin_delete_by_id(arm_id, api_version)


def get_resource_and_group_name(armstr: str) -> str:
    return armstr.split("/")[-1], armstr.split("/")[-5]


def get_sub_id_resource_and_group_name(armstr: str) -> str:
    return armstr.split("/")[-7], armstr.split("/")[-1], armstr.split("/")[-5]


def get_endpoint_parts(arm_id: str, subnet_arm_id: str) -> ():
    arm_id_parts = arm_id.split("/")
    subnet_id_parts = subnet_arm_id.split("/")
    conn_name = arm_id_parts[-1]
    subscription_id = arm_id_parts[2]
    resource_group = arm_id_parts[4]
    vnet_name = subnet_id_parts[-3]
    subnet_name = subnet_id_parts[-1]
    return conn_name, subscription_id, resource_group, vnet_name, subnet_name

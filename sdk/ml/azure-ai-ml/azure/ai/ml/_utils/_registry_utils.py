# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from azure.ai.ml._restclient.registry_discovery import AzureMachineLearningWorkspaces as ServiceClientRegistryDiscovery
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview import AzureMachineLearningWorkspaces
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview.models import (
    TemporaryDataReferenceRequestDto,
    BlobReferenceSASRequestDto,
)
from azure.ai.ml.constants import REGISTRY_ASSET_ID
from azure.core.exceptions import HttpResponseError

module_logger = logging.getLogger(__name__)

MFE_PATH_PREFIX = "mferp/managementfrontend"


def _get_registry_discovery_uri(
    service_client_registry_discovery_client: ServiceClientRegistryDiscovery,
    registry_name: str,
) -> str:
    response = (
        service_client_registry_discovery_client.registry_management_non_workspace.registry_management_non_workspace(
            registry_name
        )
    )
    return f"{response.primary_region_resource_provider_uri}{MFE_PATH_PREFIX}"


def get_registry_service_client(
    subscription_id: str,
    credential: str,
    registry_name: str,
    service_client_registry_discovery_client: ServiceClientRegistryDiscovery,
    **kwargs,
) -> AzureMachineLearningWorkspaces:
    base_url = _get_registry_discovery_uri(service_client_registry_discovery_client, registry_name)
    service_client_10_2021_dataplanepreview = AzureMachineLearningWorkspaces(
        subscription_id=subscription_id,
        credential=credential,
        base_url=base_url,
        **kwargs,
    )
    return service_client_10_2021_dataplanepreview


def get_sas_uri_for_registry_asset(service_client, name, version, resource_group, registry, body) -> str:
    """Get sas_uri for registry asset

    :param service_client: Service client
    :type service_client: AzureMachineLearningWorkspaces
    :param name: Asset name
    :type name: str
    :param version: Asset version
    :type version: str
    :param resource_group: Resource group
    :type resource_group: str
    :param registry: Registry name
    :type registry: str
    :param body: Request body
    :type body: TemporaryDataReferenceRequestDto
    :rtype: str
    """
    sas_uri = None
    try:
        res = service_client.temporary_data_references.create_or_get_temporary_data_reference(
            name=name,
            version=version,
            resource_group_name=resource_group,
            registry_name=registry,
            body=body,
        )
        sas_uri = res.blob_reference_for_consumption.credential["sasUri"]
    except HttpResponseError as e:
        if e.status_code == 400:
            module_logger.debug("Skipping file upload, reason:  %s", str(e.reason))
    return sas_uri


def get_asset_body_for_registry_storage(
    registry_name: str, asset_type: str, asset_name: str, asset_version: str
) -> TemporaryDataReferenceRequestDto:
    """
    :param registry_name: Registry name.
    :type registry_name: str
    :param asset_type: Asset type.
    :type asset_type: str
    :param asset_name: Asset name.
    :type asset_name: str
    :param asset_version: Asset version.
    :type asset_version: str
    :rtype: TemporaryDataReferenceRequestDto
    """
    body = TemporaryDataReferenceRequestDto(
        asset_id=REGISTRY_ASSET_ID.format(registry_name, asset_type, asset_name, asset_version),
        temporary_data_reference_type="TemporaryBlobReference",
    )
    return body


def get_storage_details_for_registry_assets(
    service_client: AzureMachineLearningWorkspaces,
    asset_type: str,
    asset_name: str,
    asset_version: str,
    rg_name: str,
    reg_name: str,
    uri: str,
) -> str:
    """
    :param service_client: AzureMachineLearningWorkspaces service client.
    :type service_client: AzureMachineLearningWorkspaces
    :param asset_type: Asset type.
    :type asset_type: str
    :param asset_name: Asset name.
    :type asset_name: str
    :param asset_version: Asset version.
    :type asset_version: str
    :param rg_name: Resource group name.
    :type rg_name: str
    :param reg_name: Registry name
    :type reg_name: str
    :param uri: asset uri
    :type uri: str
    :rtype: str
    """
    body = BlobReferenceSASRequestDto(
        asset_id=REGISTRY_ASSET_ID.format(reg_name, asset_type, asset_name, asset_version),
        blob_uri=uri,
    )
    sas_uri = service_client.data_references.get_blob_reference_sas(
        name=asset_name, version=asset_version, resource_group_name=rg_name, registry_name=reg_name, body=body
    )
    return sas_uri.blob_reference_for_consumption.credential["sasUri"]

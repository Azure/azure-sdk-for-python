# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview import AzureMachineLearningWorkspaces
from azure.ai.ml._restclient.registry_discovery import AzureMachineLearningWorkspaces as ServiceClientRegistryDiscovery
from azure.ai.ml.constants import REGISTRY_ASSET_ID
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview.models import TemporaryDataReferenceRequestDto
from azure.core.exceptions import HttpResponseError

module_logger = logging.getLogger(__name__)

MFE_PATH_PREFIX = "mferp/managementfrontend"


def _get_registry_discovery_uri(
    service_client_registry_discovery_client: ServiceClientRegistryDiscovery, registry_name: str
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
    registry_name, asset_type, asset_name, asset_version
) -> TemporaryDataReferenceRequestDto:
    body = TemporaryDataReferenceRequestDto(
        asset_id=REGISTRY_ASSET_ID.format(registry_name, asset_type, asset_name, asset_version),
        temporary_data_reference_type="TemporaryBlobReference",
    )
    return body

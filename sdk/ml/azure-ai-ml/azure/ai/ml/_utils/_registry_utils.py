# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Optional, Tuple

from typing_extensions import Literal

from azure.ai.ml._azure_environments import _get_default_cloud_name, _get_registry_discovery_endpoint_from_metadata
from azure.ai.ml._restclient.arm_ml_service import MachineLearningServicesMgmtClient
from azure.ai.ml._restclient.arm_ml_service._utils.model_base import SdkJSONEncoder
from azure.ai.ml._restclient.model_dataplane import ModelDataplaneClient as ServiceClientModelDataPlane
from azure.ai.ml._restclient.registry_discovery import RegistryDiscoveryClient as ServiceClientRegistryDiscovery
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview import AzureMachineLearningWorkspaces
from azure.ai.ml.constants._common import REGISTRY_ASSET_ID
from azure.ai.ml.exceptions import MlException
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller
from azure.core.rest import HttpRequest
from azure.mgmt.core.polling.arm_polling import ARMPolling

import json

module_logger = logging.getLogger(__name__)

MFE_PATH_PREFIX = "mferp/managementfrontend"

# API version pinned for the registry data-plane (MFE discovery endpoint). The registry client is a hybrid
# arm_ml_service client constructed against the discovered MFE ``base_url`` (NOT the ARM management plane) so that
# every request stays byte-identical to the legacy v2021_10 msrest client: same URL templates, same api-version.
REGISTRY_DATAPLANE_API_VERSION = "2021-10-01-dataplanepreview"


class RegistryDiscovery:
    def __init__(
        self,
        credential: str,
        registry_name: str,
        service_client_registry_discovery_client: ServiceClientRegistryDiscovery,
        **kwargs,
    ):
        self.credential = credential
        self.registry_name = registry_name
        self.service_client_registry_discovery_client = service_client_registry_discovery_client
        self.kwargs = kwargs
        self._resource_group = None
        self._subscription_id = None
        self._base_url = None
        self.workspace_region = kwargs.get("workspace_location", None)

    def _get_registry_details(self) -> str:
        response = self.service_client_registry_discovery_client.registry_management_non_workspace.get_registry_management_non_workspace(  # pylint: disable=line-too-long
            self.registry_name
        )
        if self.workspace_region:
            _check_region_fqdn(self.workspace_region, response)
            self._base_url = f"https://cert-{self.workspace_region}.experiments.azureml.net/{MFE_PATH_PREFIX}"
        else:
            self._base_url = f"{response.primary_region_resource_provider_uri}{MFE_PATH_PREFIX}"
        self._subscription_id = response.subscription_id
        self._resource_group = response.resource_group

    def get_registry_service_client(self) -> AzureMachineLearningWorkspaces:
        self._get_registry_details()
        self.kwargs.pop("subscription_id", None)
        self.kwargs.pop("resource_group", None)
        service_client_10_2021_dataplanepreview = AzureMachineLearningWorkspaces(
            subscription_id=self._subscription_id,
            resource_group=self._resource_group,
            credential=self.credential,
            base_url=self._base_url,
            **self.kwargs,
        )
        service_model_client_10_2021_dataplanepreview = ServiceClientModelDataPlane(
            credential=self.credential,
            subscription_id=self._subscription_id,
            base_url=self._base_url,
            **self.kwargs,
        )
        return service_client_10_2021_dataplanepreview, service_model_client_10_2021_dataplanepreview

    def get_registry_arm_service_client(self) -> MachineLearningServicesMgmtClient:
        """Build a hybrid arm_ml_service client bound to the discovered registry MFE endpoint.

        The client is pinned to the registry data-plane api-version and the MFE ``base_url`` so that requests issued
        via ``send_request`` are byte-identical to the legacy ``v2021_10_01_dataplanepreview`` msrest client (same host,
        same URL templates, same api-version). Registry operations are driven through hand-built ``HttpRequest`` objects
        rather than the arm-plane registry operation groups (which would target ``management.azure.com``).

        :return: The registry data-plane hybrid client.
        :rtype: ~azure.ai.ml._restclient.arm_ml_service.MachineLearningServicesMgmtClient
        """
        if self._base_url is None:
            self._get_registry_details()
        kwargs = dict(self.kwargs)
        kwargs.pop("subscription_id", None)
        kwargs.pop("resource_group", None)
        kwargs.pop("base_url", None)
        kwargs.pop("workspace_location", None)
        return MachineLearningServicesMgmtClient(
            credential=self.credential,
            subscription_id=self._subscription_id,
            base_url=self._base_url,
            api_version=REGISTRY_DATAPLANE_API_VERSION,
            **kwargs,
        )

    @property
    def subscription_id(self) -> str:
        """The subscription id of the registry.

        :return: Subscription Id
        :rtype: str
        """
        return self._subscription_id

    @property
    def resource_group(self) -> str:
        """The resource group of the registry.

        :return: Resource Group
        :rtype: str
        """
        return self._resource_group


def get_sas_uri_for_registry_asset(service_client, name, version, resource_group, registry, body) -> str:
    """Get sas_uri for registry asset.

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
    :type body: dict
    :rtype: str
    """
    sas_uri = None
    # Byte-identical to the legacy v2021_10 msrest ``temporary_data_references.create_or_get_temporary_data_reference``
    # (same MFE endpoint + api-version); the client is the hybrid arm client bound to the discovered registry base_url.
    subscription_id = service_client._config.subscription_id
    request = HttpRequest(
        "PUT",
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
        f"/providers/Microsoft.MachineLearningServices/registries/{registry}"
        f"/tempdatarefs/{name}/versions/{version}",
        params={"api-version": REGISTRY_DATAPLANE_API_VERSION},
        headers={"Accept": "application/json"},
        json=body,
    )
    try:
        response = service_client.send_request(request)
        response.raise_for_status()
        res = response.json()
        sas_uri = res["blobReferenceForConsumption"]["credential"]["sasUri"]
    except HttpResponseError as e:
        # "Asset already exists" exception is thrown from service with error code 409, that we need to ignore
        if e.status_code == 409:
            module_logger.debug("Skipping file upload, reason:  %s", str(e.reason))
        else:
            raise e
    return sas_uri


def get_registry_versioned_asset(
    service_client, asset_plural: str, name, version, resource_group, registry_name
) -> dict:
    """Byte-identical registry versioned-asset GET (same MFE endpoint + api-version as the legacy v2021_10 client).

    :param service_client: The hybrid arm client bound to the registry MFE endpoint.
    :param asset_plural: The plural asset segment of the URL (e.g. ``codes``, ``models``, ``data``, ``environments``).
    :type asset_plural: str
    :param name: Asset name.
    :param version: Asset version.
    :param resource_group: Resource group name.
    :param registry_name: Registry name.
    :return: The raw camelCase response body.
    :rtype: dict
    """
    subscription_id = service_client._config.subscription_id
    request = HttpRequest(
        "GET",
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
        f"/providers/Microsoft.MachineLearningServices/registries/{registry_name}"
        f"/{asset_plural}/{name}/versions/{version}",
        params={"api-version": REGISTRY_DATAPLANE_API_VERSION},
        headers={"Accept": "application/json"},
    )
    response = service_client.send_request(request)
    if response.status_code == 404:
        raise ResourceNotFoundError(response=response)
    response.raise_for_status()
    return response.json()


def get_registry_container_asset(service_client, asset_plural: str, name, resource_group, registry_name) -> dict:
    """Byte-identical registry container GET (same MFE endpoint + api-version as the legacy v2021_10 client).

    :param service_client: The hybrid arm client bound to the registry MFE endpoint.
    :param asset_plural: The plural asset segment of the URL (e.g. ``codes``, ``models``, ``data``, ``environments``).
    :type asset_plural: str
    :param name: Container name.
    :param resource_group: Resource group name.
    :param registry_name: Registry name.
    :return: The raw camelCase response body.
    :rtype: dict
    """
    subscription_id = service_client._config.subscription_id
    request = HttpRequest(
        "GET",
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
        f"/providers/Microsoft.MachineLearningServices/registries/{registry_name}"
        f"/{asset_plural}/{name}",
        params={"api-version": REGISTRY_DATAPLANE_API_VERSION},
        headers={"Accept": "application/json"},
    )
    response = service_client.send_request(request)
    if response.status_code == 404:
        raise ResourceNotFoundError(response=response)
    response.raise_for_status()
    return response.json()


def list_registry_assets(
    service_client,
    asset_plural: str,
    name,
    resource_group,
    registry_name,
    arm_cls,
    from_rest_fn,
    list_view_type=None,
    properties=None,
    order_by=None,
    top=None,
) -> ItemPaged:
    """Byte-identical registry versioned-asset / container list (same MFE endpoint + api-version + paging contract).

    :param service_client: The hybrid arm client bound to the registry MFE endpoint.
    :param asset_plural: The plural asset segment of the URL (e.g. ``codes``, ``models``, ``data``, ``environments``).
    :type asset_plural: str
    :param name: Container name for a versions list, or ``None`` for a containers list.
    :param resource_group: Resource group name.
    :param registry_name: Registry name.
    :param arm_cls: The arm hybrid model class to deserialize each response item into.
    :param from_rest_fn: Callable mapping a deserialized arm model to an SDK entity.
    :param list_view_type: Optional ``listViewType`` query value.
    :param properties: Optional ``properties`` filter query value.
    :return: An iterator of SDK entities.
    :rtype: ~azure.core.paging.ItemPaged
    """
    subscription_id = service_client._config.subscription_id
    prefix = (
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
        f"/providers/Microsoft.MachineLearningServices/registries/{registry_name}/{asset_plural}"
    )
    url_path = f"{prefix}/{name}/versions" if name else prefix
    params = {"api-version": REGISTRY_DATAPLANE_API_VERSION}
    if list_view_type is not None:
        params["listViewType"] = list_view_type
    if properties is not None:
        params["properties"] = properties
    if order_by is not None:
        params["$orderBy"] = order_by
    if top is not None:
        params["$top"] = top

    def get_next(continuation_token=None):
        if continuation_token:
            request = HttpRequest("GET", continuation_token, headers={"Accept": "application/json"})
        else:
            request = HttpRequest("GET", url_path, params=params, headers={"Accept": "application/json"})
        response = service_client.send_request(request)
        response.raise_for_status()
        return response

    def extract_data(response):
        body = response.json()
        items = [from_rest_fn(arm_cls._deserialize(obj, [])) for obj in body.get("value", [])]
        return body.get("nextLink") or None, iter(items)

    return ItemPaged(get_next, extract_data)


def begin_create_or_update_registry_versioned_asset(
    service_client,
    asset_plural: str,
    name,
    version,
    resource_group,
    registry_name,
    body,
    *,
    polling_cls=ARMPolling,
    polling_interval=None,
    wait=True,
):
    """Byte-identical registry versioned-asset create-or-update LRO (same MFE endpoint + api-version + wire body).

    Mirrors the arm ``begin_create_or_update`` machinery (initial PUT via the pipeline + ``LROPoller``/``ARMPolling``)
    but pins the URL template + api-version to the legacy v2021_10 registry data-plane contract.

    :param service_client: The hybrid arm client bound to the registry MFE endpoint.
    :param asset_plural: The plural asset segment of the URL (e.g. ``codes``, ``models``, ``data``, ``environments``).
    :type asset_plural: str
    :param name: Asset name.
    :param version: Asset version.
    :param resource_group: Resource group name.
    :param registry_name: Registry name.
    :param body: The arm hybrid version model to serialize as the request body.
    :keyword polling_cls: The polling method class (defaults to ``ARMPolling``; pass ``AzureMLPolling`` to match callers
        that stream progress).
    :keyword polling_interval: Optional poll interval override (defaults to the client config's polling interval).
    :keyword wait: When ``True`` (default) the LRO is awaited and the final body dict is returned; when ``False`` the
        ``LROPoller`` is returned so the caller can drive it (e.g. via ``polling_wait``).
    :return: The raw camelCase final response body, or the ``LROPoller`` when ``wait`` is ``False``.
    :rtype: dict or ~azure.core.polling.LROPoller
    """
    subscription_id = service_client._config.subscription_id
    content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)
    request = HttpRequest(
        "PUT",
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
        f"/providers/Microsoft.MachineLearningServices/registries/{registry_name}"
        f"/{asset_plural}/{name}/versions/{version}",
        params={"api-version": REGISTRY_DATAPLANE_API_VERSION},
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        content=content,
    )
    path_format_arguments = {
        "endpoint": service_client._serialize.url(
            "self._config.base_url", service_client._config.base_url, "str", skip_quote=True
        ),
    }
    request.url = service_client._client.format_url(request.url, **path_format_arguments)
    raw_result = service_client._client._pipeline.run(request, stream=True)
    response = raw_result.http_response
    response.read()
    if response.status_code not in [200, 201]:
        response.raise_for_status()

    def get_long_running_output(pipeline_response):
        return pipeline_response.http_response.json()

    interval = polling_interval if polling_interval is not None else service_client._config.polling_interval
    polling_method = polling_cls(interval, path_format_arguments=path_format_arguments)
    poller = LROPoller(service_client._client, raw_result, get_long_running_output, polling_method)
    if wait:
        return poller.result()
    return poller


def begin_import_registry_asset(
    service_client, resource_group, registry_name, body, *, polling_cls=ARMPolling, polling_interval=None, wait=True
):
    """Byte-identical registry asset import LRO (``resource_management_asset_reference.begin_import_method``).

    POSTs to ``.../registries/{registry}/import`` against the discovered MFE endpoint + registry data-plane api-version.

    :param service_client: The hybrid arm client bound to the registry MFE endpoint.
    :param resource_group: Resource group name.
    :param registry_name: Registry name.
    :param body: The camelCase import request wire dict.
    :keyword polling_cls: The polling method class (defaults to ``ARMPolling``).
    :keyword polling_interval: Optional poll interval override.
    :keyword wait: When ``True`` (default) the LRO is awaited and the final body (or ``None``) is returned; when
        ``False`` the ``LROPoller`` is returned.
    :return: The raw camelCase final response body (or ``None``), or the ``LROPoller`` when ``wait`` is ``False``.
    :rtype: dict or None or ~azure.core.polling.LROPoller
    """
    subscription_id = service_client._config.subscription_id
    request = HttpRequest(
        "POST",
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
        f"/providers/Microsoft.MachineLearningServices/registries/{registry_name}/import",
        params={"api-version": REGISTRY_DATAPLANE_API_VERSION},
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json=body,
    )
    path_format_arguments = {
        "endpoint": service_client._serialize.url(
            "self._config.base_url", service_client._config.base_url, "str", skip_quote=True
        ),
    }
    request.url = service_client._client.format_url(request.url, **path_format_arguments)
    raw_result = service_client._client._pipeline.run(request, stream=True)
    response = raw_result.http_response
    response.read()
    if response.status_code not in [200, 201, 202]:
        response.raise_for_status()

    def get_long_running_output(pipeline_response):
        http_response = pipeline_response.http_response
        return http_response.json() if http_response.text() else None

    interval = polling_interval if polling_interval is not None else service_client._config.polling_interval
    polling_method = polling_cls(interval, path_format_arguments=path_format_arguments)
    poller = LROPoller(service_client._client, raw_result, get_long_running_output, polling_method)
    if wait:
        return poller.result()
    return poller


def get_asset_body_for_registry_storage(
    registry_name: str, asset_type: str, asset_name: str, asset_version: str
) -> dict:
    """Get Asset body for registry.

    :param registry_name: Registry name.
    :type registry_name: str
    :param asset_type: Asset type.
    :type asset_type: str
    :param asset_name: Asset name.
    :type asset_name: str
    :param asset_version: Asset version.
    :type asset_version: str
    :return: The temporary data reference request body (camelCase wire dict).
    :rtype: dict
    """
    body = {
        "assetId": REGISTRY_ASSET_ID.format(registry_name, asset_type, asset_name, asset_version),
        "temporaryDataReferenceType": "TemporaryBlobReference",
    }
    return body


def get_storage_details_for_registry_assets(
    service_client: MachineLearningServicesMgmtClient,
    asset_type: str,
    asset_name: str,
    asset_version: str,
    rg_name: str,
    reg_name: str,
    uri: str,
) -> Tuple[str, Literal["NoCredentials", "SAS"]]:
    """Get storage details for registry assets.

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
    :return: A 2-tuple of a URI and a string. Either:
      * A blob uri and "NoCredentials"
      * A sas URI and "SAS"
    :rtype: Tuple[str, Literal["NoCredentials", "SAS"]]
    """
    # Byte-identical to the legacy v2021_10 msrest ``data_references.get_blob_reference_sas`` (same MFE endpoint +
    # api-version). NOTE: the ``credential_type == "no_credentials"`` comparison is preserved verbatim from the legacy
    # code path; the wire value is actually "NoCredentials", so this branch never matches (behavior kept identical).
    subscription_id = service_client._config.subscription_id
    body = {
        "assetId": REGISTRY_ASSET_ID.format(reg_name, asset_type, asset_name, asset_version),
        "blobUri": uri,
    }
    request = HttpRequest(
        "POST",
        f"/subscriptions/{subscription_id}/resourceGroups/{rg_name}"
        f"/providers/Microsoft.MachineLearningServices/registries/{reg_name}"
        f"/datarefs/{asset_name}/versions/{asset_version}",
        params={"api-version": REGISTRY_DATAPLANE_API_VERSION},
        headers={"Accept": "application/json"},
        json=body,
    )
    response = service_client.send_request(request)
    response.raise_for_status()
    sas_uri = response.json()
    blob_reference_for_consumption = sas_uri["blobReferenceForConsumption"]
    credential = blob_reference_for_consumption["credential"]
    if credential["credentialType"] == "no_credentials":
        return blob_reference_for_consumption["blobUri"], "NoCredentials"

    return (
        credential["sasUri"],
        "SAS",
    )


def get_registry_client(credential, registry_name, workspace_location: Optional[str] = None, **kwargs):
    base_url = _get_registry_discovery_endpoint_from_metadata(_get_default_cloud_name())
    kwargs.pop("base_url", None)

    service_client_registry_discovery_client = ServiceClientRegistryDiscovery(
        credential=credential, base_url=base_url, **kwargs
    )
    if workspace_location:
        workspace_kwargs = {"workspace_location": workspace_location}
        kwargs.update(workspace_kwargs)

    registry_discovery = RegistryDiscovery(
        credential, registry_name, service_client_registry_discovery_client, **kwargs
    )
    service_client_10_2021_dataplanepreview, service_model_client_10_2021_dataplanepreview = (
        registry_discovery.get_registry_service_client()
    )
    # Byte-identical hybrid client bound to the same discovered MFE endpoint + registry data-plane api-version.
    # Registry consumers are being migrated off the msrest client above to this client's ``send_request``.
    service_client_registry_arm = registry_discovery.get_registry_arm_service_client()
    subscription_id = registry_discovery.subscription_id
    resource_group_name = registry_discovery.resource_group
    return (
        service_client_10_2021_dataplanepreview,
        resource_group_name,
        subscription_id,
        service_model_client_10_2021_dataplanepreview,
        service_client_registry_arm,
    )


def _check_region_fqdn(workspace_region, response):
    if workspace_region in response["registryFqdns"].keys():
        return
    regions = list(response["registryFqdns"].keys())
    msg = f"Workspace region {workspace_region} not supported by the \
            registry {response.registry_name} regions {regions}"
    raise MlException(message=msg, no_personal_data_message=msg)

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Metadata to interact with different Azure clouds."""

import logging
import os
from typing import Dict, List, Optional

from azure.ai.ml._utils.utils import _get_mfe_url_override
from azure.ai.ml.constants._common import AZUREML_CLOUD_ENV_NAME, ArmConstants
from azure.ai.ml.exceptions import MlException
from azure.core.rest import HttpRequest
from azure.mgmt.core import ARMPipelineClient

module_logger = logging.getLogger(__name__)


class AzureEnvironments:
    ENV_DEFAULT = "AzureCloud"
    ENV_US_GOVERNMENT = "AzureUSGovernment"
    ENV_CHINA = "AzureChinaCloud"


class EndpointURLS:  # pylint: disable=too-few-public-methods
    AZURE_PORTAL_ENDPOINT = "azure_portal"
    RESOURCE_MANAGER_ENDPOINT = "resource_manager"
    ACTIVE_DIRECTORY_ENDPOINT = "active_directory"
    AML_RESOURCE_ID = "aml_resource_id"
    STORAGE_ENDPOINT = "storage_endpoint"
    REGISTRY_DISCOVERY_ENDPOINT = "registry_discovery_endpoint"


class CloudArgumentKeys:
    CLOUD_METADATA = "cloud_metadata"


_environments = {
    AzureEnvironments.ENV_DEFAULT: {
        EndpointURLS.AZURE_PORTAL_ENDPOINT: "https://portal.azure.com/",
        EndpointURLS.RESOURCE_MANAGER_ENDPOINT: "https://management.azure.com/",
        EndpointURLS.ACTIVE_DIRECTORY_ENDPOINT: "https://login.microsoftonline.com/",
        EndpointURLS.AML_RESOURCE_ID: "https://ml.azure.com/",
        EndpointURLS.STORAGE_ENDPOINT: "core.windows.net",
        EndpointURLS.REGISTRY_DISCOVERY_ENDPOINT: "https://eastus.api.azureml.ms/",
    },
    AzureEnvironments.ENV_CHINA: {
        EndpointURLS.AZURE_PORTAL_ENDPOINT: "https://portal.azure.cn/",
        EndpointURLS.RESOURCE_MANAGER_ENDPOINT: "https://management.chinacloudapi.cn/",
        EndpointURLS.ACTIVE_DIRECTORY_ENDPOINT: "https://login.chinacloudapi.cn/",
        EndpointURLS.AML_RESOURCE_ID: "https://ml.azure.cn/",
        EndpointURLS.STORAGE_ENDPOINT: "core.chinacloudapi.cn",
        EndpointURLS.REGISTRY_DISCOVERY_ENDPOINT: "https://chinaeast2.api.ml.azure.cn/",
    },
    AzureEnvironments.ENV_US_GOVERNMENT: {
        EndpointURLS.AZURE_PORTAL_ENDPOINT: "https://portal.azure.us/",
        EndpointURLS.RESOURCE_MANAGER_ENDPOINT: "https://management.usgovcloudapi.net/",
        EndpointURLS.ACTIVE_DIRECTORY_ENDPOINT: "https://login.microsoftonline.us/",
        EndpointURLS.AML_RESOURCE_ID: "https://ml.azure.us/",
        EndpointURLS.STORAGE_ENDPOINT: "core.usgovcloudapi.net",
        EndpointURLS.REGISTRY_DISCOVERY_ENDPOINT: "https://usgovarizona.api.ml.azure.us/",
    },
}


def _get_cloud(cloud: str) -> Dict[str, str]:
    if cloud in _environments:
        return _environments[cloud]
    arm_url = os.environ.get(ArmConstants.METADATA_URL_ENV_NAME, ArmConstants.DEFAULT_URL)
    arm_clouds = _get_clouds_by_metadata_url(arm_url)
    try:
        new_cloud = arm_clouds[cloud]
        _environments.update(new_cloud)  # type: ignore[arg-type]
        return new_cloud
    except KeyError as e:
        msg = 'Unknown cloud environment "{0}".'.format(cloud)
        raise MlException(message=msg, no_personal_data_message=msg) from e


def _get_default_cloud_name() -> str:
    """
    :return: Configured cloud, defaults to 'AzureCloud' if
    AZUREML_CURRENT_CLOUD and ARM_CLOUD_METADATA_URL are not set to dynamically retrieve cloud info.
    AZUREML_CURRENT_CLOUD is also set by the SDK based on ARM_CLOUD_METADATA_URL.
    :rtype: str
    """
    current_cloud_env = os.getenv(AZUREML_CLOUD_ENV_NAME)
    if current_cloud_env is not None:
        return current_cloud_env
    arm_metadata_url = os.getenv(ArmConstants.METADATA_URL_ENV_NAME)
    if arm_metadata_url is not None:
        clouds = _get_clouds_by_metadata_url(arm_metadata_url)  # prefer ARM metadata url when set
        for cloud_name in clouds:  # pylint: disable=consider-using-dict-items
            if clouds[cloud_name][EndpointURLS.RESOURCE_MANAGER_ENDPOINT] in arm_metadata_url:
                _set_cloud(cloud_name)
                return cloud_name
    return AzureEnvironments.ENV_DEFAULT


def _get_cloud_details(cloud_name: Optional[str] = None) -> Dict[str, str]:
    """Returns a Cloud endpoints object for the specified Azure Cloud.

    :param cloud_name: cloud name
    :type cloud_name: str
    :return: azure environment endpoint.
    :rtype: Dict[str, str]
    """
    if cloud_name is None:
        cloud_name = _get_default_cloud_name()
        module_logger.debug(
            "Using the default cloud configuration: '%s'.",
            cloud_name,
        )
    return _get_cloud(cloud_name)


def _set_cloud(cloud_name: Optional[str] = None):
    """Sets the current cloud.

    :param cloud_name: cloud name
    :type cloud_name: str
    """
    if cloud_name is not None:
        try:
            _get_cloud(cloud_name)
        except Exception as e:
            msg = 'Unknown cloud environment supplied: "{0}".'.format(cloud_name)
            raise MlException(message=msg, no_personal_data_message=msg) from e
    else:
        cloud_name = _get_default_cloud_name()
    os.environ[AZUREML_CLOUD_ENV_NAME] = cloud_name


def _get_base_url_from_metadata(cloud_name: Optional[str] = None, is_local_mfe: bool = False) -> str:
    """Retrieve the base url for a cloud from the metadata in SDK.

    :param cloud_name: cloud name
    :type cloud_name: Optional[str]
    :param is_local_mfe: Whether is local Management Front End. Defaults to False.
    :type is_local_mfe: bool
    :return: base url for a cloud
    :rtype: str
    """
    base_url = None
    if is_local_mfe:
        base_url = _get_mfe_url_override()
    if base_url is None:
        cloud_details = _get_cloud_details(cloud_name)
        base_url = str(cloud_details.get(EndpointURLS.RESOURCE_MANAGER_ENDPOINT)).strip("/")
    return base_url


def _get_aml_resource_id_from_metadata(cloud_name: Optional[str] = None) -> str:
    """Retrieve the aml_resource_id for a cloud from the metadata in SDK.

    :param cloud_name: cloud name
    :type cloud_name: str
    :return: aml_resource_id for a cloud
    :rtype: str
    """
    cloud_details = _get_cloud_details(cloud_name)
    aml_resource_id = str(cloud_details.get(EndpointURLS.AML_RESOURCE_ID)).strip("/")
    return aml_resource_id


def _get_active_directory_url_from_metadata(cloud_name: Optional[str] = None) -> str:
    """Retrieve the active_directory_url for a cloud from the metadata in SDK.

    :param cloud_name: cloud name
    :type cloud_name: str
    :return: active_directory for a cloud
    :rtype: str
    """
    cloud_details = _get_cloud_details(cloud_name)
    active_directory_url = str(cloud_details.get(EndpointURLS.ACTIVE_DIRECTORY_ENDPOINT)).strip("/")
    return active_directory_url


def _get_storage_endpoint_from_metadata(cloud_name: Optional[str] = None) -> str:
    """Retrieve the storage_endpoint for a cloud from the metadata in SDK.

    :param cloud_name: cloud name
    :type cloud_name: str
    :return: storage_endpoint for a cloud
    :rtype: str
    """
    cloud_details = _get_cloud_details(cloud_name)
    storage_endpoint = cloud_details.get(EndpointURLS.STORAGE_ENDPOINT)
    return str(storage_endpoint)


def _get_azure_portal_id_from_metadata(cloud_name: Optional[str] = None) -> str:
    """Retrieve the azure_portal_id for a cloud from the metadata in SDK.

    :param cloud_name: cloud name
    :type cloud_name: str
    :return: azure_portal_id for a cloud
    :rtype: str
    """
    cloud_details = _get_cloud_details(cloud_name)
    azure_portal_id = cloud_details.get(EndpointURLS.AZURE_PORTAL_ENDPOINT)
    return str(azure_portal_id)


def _get_cloud_information_from_metadata(cloud_name: Optional[str] = None, **kwargs) -> Dict:
    """Retrieve the cloud information from the metadata in SDK.

    :param cloud_name: cloud name
    :type cloud_name: str
    :return: A dictionary of additional configuration parameters required for passing in cloud information.
    :rtype: Dict
    """
    cloud_details = _get_cloud_details(cloud_name)
    credential_scopes = _resource_to_scopes(
        cloud_details.get(EndpointURLS.RESOURCE_MANAGER_ENDPOINT).strip("/")  # type: ignore[union-attr]
    )

    # Update the kwargs with the cloud information
    client_kwargs: Dict = {"cloud": cloud_name}
    if credential_scopes is not None:
        client_kwargs["credential_scopes"] = credential_scopes
    kwargs.update(client_kwargs)
    return kwargs


def _get_registry_discovery_endpoint_from_metadata(cloud_name: Optional[str] = None) -> str:
    """Retrieve the registry_discovery_endpoint for a cloud from the metadata in SDK.

    :param cloud_name: cloud name
    :type cloud_name: str
    :return: registry_discovery_endpoint for a cloud
    :rtype: str
    """
    cloud_details = _get_cloud_details(cloud_name)
    registry_discovery_endpoint = cloud_details.get(EndpointURLS.REGISTRY_DISCOVERY_ENDPOINT)
    return str(registry_discovery_endpoint)


def _resource_to_scopes(resource: str) -> List[str]:
    """Convert the resource ID to scopes by appending the /.default suffix and return a list. For example:
    'https://management.core.windows.net/' ->

    ['https://management.core.windows.net//.default']

    :param resource: The resource ID
    :type resource: str
    :return: A list of scopes
    :rtype: List[str]
    """
    scope = resource + "/.default"
    return [scope]


def _get_registry_discovery_url(cloud: dict, cloud_suffix: str = "") -> str:
    """Get or generate the registry discovery url.

    :param cloud: configuration of the cloud to get the registry_discovery_url from
    :type cloud: dict
    :param cloud_suffix: the suffix to use for the cloud, in the case that the registry_discovery_url
        must be generated
    :type cloud_suffix: str
    :return: string of discovery url
    :rtype: str
    """
    cloud_name = cloud["name"]
    if cloud_name in _environments:
        return _environments[cloud_name][EndpointURLS.REGISTRY_DISCOVERY_ENDPOINT]
    registry_discovery_from_env = os.getenv(ArmConstants.REGISTRY_ENV_URL)
    if registry_discovery_from_env is not None:
        return registry_discovery_from_env
    registry_discovery_region = os.environ.get(
        ArmConstants.REGISTRY_DISCOVERY_REGION_ENV_NAME,
        ArmConstants.REGISTRY_DISCOVERY_DEFAULT_REGION,
    )
    return f"https://{cloud_name.lower()}{registry_discovery_region}.api.ml.azure.{cloud_suffix}/"


def _get_clouds_by_metadata_url(metadata_url: str) -> Dict[str, Dict[str, str]]:
    """Get all the clouds by the specified metadata url.

    :param metadata_url: The metadata url
    :type metadata_url: str
    :return: A dictionary of cloud name to various relevant endpoints/uris
    :rtype: Dict[str, Dict[str, str]]
    """
    try:
        module_logger.debug("Start : Loading cloud metadata from the url specified by %s", metadata_url)
        client = ARMPipelineClient(base_url=metadata_url, policies=[])
        HttpRequest("GET", metadata_url)
        with client.send_request(HttpRequest("GET", metadata_url)) as meta_response:
            arm_cloud_dict = meta_response.json()
            cli_cloud_dict = _convert_arm_to_cli(arm_cloud_dict)
            module_logger.debug(
                "Finish : Loading cloud metadata from the url specified by %s",
                metadata_url,
            )
            return cli_cloud_dict
    except Exception as ex:  # pylint: disable=broad-except
        module_logger.warning(
            "Error: Azure ML was unable to load cloud metadata from the url specified by %s. %s. "
            "This may be due to a misconfiguration of networking controls. Azure Machine Learning Python "
            "SDK requires outbound access to Azure Resource Manager. Please contact your networking team "
            "to configure outbound access to Azure Resource Manager on both Network Security Group and "
            "Firewall. For more details on required configurations, see "
            "https://docs.microsoft.com/azure/machine-learning/how-to-access-azureml-behind-firewall.",
            metadata_url,
            ex,
        )
        return {}


def _convert_arm_to_cli(arm_cloud_metadata) -> Dict[str, Dict[str, str]]:
    cli_cloud_metadata_dict = {}
    if isinstance(arm_cloud_metadata, dict):
        arm_cloud_metadata = [arm_cloud_metadata]

    for cloud in arm_cloud_metadata:
        try:
            cloud_name = cloud["name"]
            portal_endpoint = cloud["portal"]
            cloud_suffix = ".".join(portal_endpoint.split(".")[2:]).replace("/", "")
            registry_discovery_url = _get_registry_discovery_url(cloud, cloud_suffix)
            cli_cloud_metadata_dict[cloud_name] = {
                EndpointURLS.AZURE_PORTAL_ENDPOINT: cloud["portal"],
                EndpointURLS.RESOURCE_MANAGER_ENDPOINT: cloud["resourceManager"],
                EndpointURLS.ACTIVE_DIRECTORY_ENDPOINT: cloud["authentication"]["loginEndpoint"],
                EndpointURLS.AML_RESOURCE_ID: "https://ml.azure.{}".format(cloud_suffix),
                EndpointURLS.STORAGE_ENDPOINT: cloud["suffixes"]["storage"],
                EndpointURLS.REGISTRY_DISCOVERY_ENDPOINT: registry_discovery_url,
            }
        except KeyError as ex:
            module_logger.warning("Property on cloud not found in arm cloud metadata: %s", ex)
            continue
    return cli_cloud_metadata_dict


def _add_cloud_to_environments(kwargs):
    cloud_name = kwargs["cloud"]
    if cloud_name in _environments:
        raise AttributeError(f"Cannot overwrite existing cloud: {cloud_name}")
    cloud_metadata = kwargs[CloudArgumentKeys.CLOUD_METADATA]
    if cloud_metadata is None:
        raise LookupError(f"{CloudArgumentKeys.CLOUD_METADATA} not present in kwargs, no environment to add!")
    _environments[kwargs["cloud"]] = {
        EndpointURLS.AZURE_PORTAL_ENDPOINT: cloud_metadata[EndpointURLS.AZURE_PORTAL_ENDPOINT],
        EndpointURLS.RESOURCE_MANAGER_ENDPOINT: cloud_metadata[EndpointURLS.RESOURCE_MANAGER_ENDPOINT],
        EndpointURLS.ACTIVE_DIRECTORY_ENDPOINT: cloud_metadata[EndpointURLS.ACTIVE_DIRECTORY_ENDPOINT],
        EndpointURLS.AML_RESOURCE_ID: cloud_metadata[EndpointURLS.AML_RESOURCE_ID],
        EndpointURLS.STORAGE_ENDPOINT: cloud_metadata[EndpointURLS.STORAGE_ENDPOINT],
        EndpointURLS.REGISTRY_DISCOVERY_ENDPOINT: cloud_metadata[EndpointURLS.REGISTRY_DISCOVERY_ENDPOINT],
    }

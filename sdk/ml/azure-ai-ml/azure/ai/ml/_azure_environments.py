# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Metadata to interact with different Azure clouds."""

import logging
import os
from typing import Any, Dict, List, Optional

from azure.ai.ml._utils.utils import _get_mfe_url_override
from azure.ai.ml.constants._common import AZUREML_CLOUD_ENV_NAME
from azure.ai.ml.constants._common import ArmConstants
from azure.core.rest import HttpRequest
from azure.mgmt.core import ARMPipelineClient


module_logger = logging.getLogger(__name__)


class AzureEnvironments:
    """Constants representing the name of each Azure Cloud type."""

    ENV_DEFAULT = "AzureCloud"
    ENV_US_GOVERNMENT = "AzureUSGovernment"
    ENV_CHINA = "AzureChinaCloud"


class EndpointURLS:  # pylint: disable=too-few-public-methods,no-init
    """Constants representing the aliases of each endpoint URL."""

    AZURE_PORTAL_ENDPOINT = "azure_portal"
    RESOURCE_MANAGER_ENDPOINT = "resource_manager"
    ACTIVE_DIRECTORY_ENDPOINT = "active_directory"
    AML_RESOURCE_ID = "aml_resource_id"
    STORAGE_ENDPOINT = "storage_endpoint"
    REGISTRY_DISCOVERY_ENDPOINT = "registry_discovery_endpoint"


class CloudArgumentKeys:
    """Constants representing cloud arguments."""

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


def _get_cloud_environment_info(cloud: Optional(str)) -> Dict[EndpointURLS, str]:
    """Retrieve cloud environment information.

    :param cloud: Azure Cloud type name. Should be a member of AzureEnvironments or a cloud type retrievable from
    metadata urls. If no argument is provided, AzureEnvironments.ENV_DEFAULT will be used.
    :type cloud: Optional(str)
    :raises Exception: If the provided cloud is not a member of AzureEnvironments and cannot be retrieved from metadata urls.
    :return: The resource ID and all endpoint URLs for the cloud type.
    :rtype: Dict[EndpointURLS, str]
    """
    if cloud is None:
        module_logger.debug(
            "Using the default cloud configuration: '%s'.",
            AzureEnvironments.ENV_DEFAULT,
        )
        cloud = _get_default_cloud_name()

    if cloud in _environments:
        return _environments[cloud]
    arm_url = os.environ.get(ArmConstants.METADATA_URL_ENV_NAME, ArmConstants.DEFAULT_URL)
    arm_clouds = _get_cloud_environment_infos_by_metadata_url(arm_url)
    try:
        new_cloud = arm_clouds[cloud]
        _environments.update(new_cloud)
        return new_cloud
    except KeyError:
        raise Exception('Unknown cloud environment "{0}".'.format(cloud))


def _get_default_cloud_name() -> str:
    """Return default cloud name.

    :return: Default cloud name set by AzureEnvironments.ENV_DEFAULT
    :rtype: str
    """
    return os.getenv(AZUREML_CLOUD_ENV_NAME, AzureEnvironments.ENV_DEFAULT)


def _set_cloud(cloud: str = AzureEnvironments.ENV_DEFAULT) -> None:
    """Set the AZUREML_CLOUD_ENV_NAME environment variable to the given cloud.

    :param cloud: Cloud type name, defaults to AzureEnvironments.ENV_DEFAULT.
    :type cloud: str, optional
    :raises Exception: If provided cloud type name is unknown.
    """
    if cloud is not None:
        try:
            _get_cloud_environment_info(cloud)
        except Exception:
            raise Exception('Unknown cloud environment supplied: "{0}".'.format(cloud))
    else:
        cloud = _get_default_cloud_name()
    os.environ[AZUREML_CLOUD_ENV_NAME] = cloud


def _get_base_url_from_metadata(cloud_name: Optional[str] = None, is_local_mfe: Optional[bool] = False) -> str:
    """Retrieve a cloud's base url from SDK metadata.

    :param cloud_name: Cloud name. If no argument is provided, AzureEnvironments.ENV_DEFAULT will be used.
    :type cloud_name: Optional[str]
    :param is_local_mfe: , defaults to False  #TODO: What exactly is this parameter?
    :type is_local_mfe: Optional[bool]
    :return: Cloud base url
    :rtype: str
    """
    base_url = None
    if is_local_mfe:
        base_url = _get_mfe_url_override()
    if base_url is None:
        cloud_details = _get_cloud_environment_info(cloud_name)
        base_url = cloud_details.get(EndpointURLS.RESOURCE_MANAGER_ENDPOINT).strip("/")
    return base_url


def _get_aml_resource_id_from_metadata(cloud_name: Optional[str] = None) -> str:
    """Retrieve a cloud's AzureML resource ID from SDK metadata.

    :param cloud_name: Cloud name. If no argument is provided, AzureEnvironments.ENV_DEFAULT will be used.
    :type cloud_name: Optional[str]
    :return: The cloud's AzureML resource ID
    :rtype: str
    """
    cloud_details = _get_cloud_environment_info(cloud_name)
    aml_resource_id = cloud_details.get(EndpointURLS.AML_RESOURCE_ID).strip("/")
    return aml_resource_id


def _get_active_directory_url_from_metadata(cloud_name: Optional[str] = None) -> str:
    """Retrieve a cloud's Active Directory URL from SDK metadata.

    :param cloud_name: Cloud name. If no argument is provided, AzureEnvironments.ENV_DEFAULT will be used.
    :type cloud_name: Optional[str]
    :return: The cloud's Active Directory URL
    :rtype: str
    """
    cloud_details = _get_cloud_environment_info(cloud_name)
    active_directory_url = cloud_details.get(EndpointURLS.ACTIVE_DIRECTORY_ENDPOINT).strip("/")
    return active_directory_url


def _get_storage_endpoint_from_metadata(cloud_name: Optional[str] = None) -> str:
    """Retrieve a cloud's storage endpoint from SDK metadata.

    :param cloud_name: Cloud name. If no argument is provided, AzureEnvironments.ENV_DEFAULT will be used.
    :type cloud_name: Optional[str]
    :return: The cloud's storage endpoint
    :rtype: str
    """
    cloud_details = _get_cloud_environment_info(cloud_name)
    storage_endpoint = cloud_details.get(EndpointURLS.STORAGE_ENDPOINT)
    return storage_endpoint


def _get_azure_portal_id_from_metadata(cloud_name: Optional[str] = None) -> str:
    """Retrieve a cloud's Azure Portal ID from SDK metadata.

    :param cloud_name: Cloud name. If no argument is provided, AzureEnvironments.ENV_DEFAULT will be used.
    :type cloud_name: Optional[str]
    :return: The cloud's Azure Portal ID
    :rtype: str
    """
    cloud_details = _get_cloud_environment_info(cloud_name)
    azure_portal_id = cloud_details.get(EndpointURLS.AZURE_PORTAL_ENDPOINT)
    return azure_portal_id


def _get_cloud_environment_info_from_metadata(cloud_name: Optional[str] = None, **kwargs) -> Dict[str, str]:
    """Retrieve cloud environment information from SDK metadata.

    :param cloud_name: Cloud name. If no argument is provided, AzureEnvironments.ENV_DEFAULT will be used.
    :type cloud_name: Optional[str]
    :return: A dictionary of additional configuration parameters required for passing in cloud information.
    :rtype: Dict[str, str]
    """
    cloud_details = _get_cloud_environment_info(cloud_name)
    credential_scopes = _convert_resource_to_scopes(
        cloud_details.get(EndpointURLS.RESOURCE_MANAGER_ENDPOINT).strip("/")
    )

    # Update the kwargs with the cloud information
    client_kwargs = {"cloud": cloud_name}
    if credential_scopes is not None:
        client_kwargs["credential_scopes"] = credential_scopes
    kwargs.update(client_kwargs)
    return kwargs


def _get_registry_discovery_endpoint_from_metadata(cloud_name: Optional[str] = None):
    """Retrieve a cloud's registry discovery endpoint from SDK metadata.

    :param cloud_name: Cloud name. If no argument is provided, AzureEnvironments.ENV_DEFAULT will be used.
    :type cloud_name: Optional[str]
    :return: The cloud's registry discover endpoint.
    :rtype: str
    """
    cloud_details = _get_cloud_environment_info(cloud_name)
    registry_discovery_endpoint = cloud_details.get(EndpointURLS.REGISTRY_DISCOVERY_ENDPOINT)
    return registry_discovery_endpoint


def _convert_resource_to_scopes(resource: str) -> List[str]:
    """Convert the resource ID to scopes by appending the /.default suffix and return a list.

    For example:
    'https://management.core.windows.net/' -> ['https://management.core.windows.net//.default']

    :param resource: The resource ID
    :type resource: str
    :return: A list containing the scope
    :rtype: List[str]
    """
    scope = resource + "/.default"
    return [scope]


def _get_registry_discovery_url(cloud: Dict[str, str], cloud_suffix: Optional[str] = None) -> str:
    """Retrieve registry discovery URL from cloud metadata.

    :param cloud: Cloud metadata json response
    :type cloud: Dict[str, str]
    :param cloud_suffix: Cloud suffix, defaults to None
    :type cloud_suffix: Optional[str]
    :return: The cloud's registry discovery URL
    :rtype: str
    """
    cloud_name = cloud["name"]
    if cloud_name in _environments:
        return _environments[cloud_name].registry_url

    registry_discovery_region = os.environ.get(
        ArmConstants.REGISTRY_DISCOVERY_REGION_ENV_NAME,
        ArmConstants.REGISTRY_DISCOVERY_DEFAULT_REGION,
    )
    registry_discovery_region_default = "https://{}{}.api.azureml.{}/".format(
        cloud_name.lower(), registry_discovery_region, cloud_suffix
    )
    return os.environ.get(ArmConstants.REGISTRY_ENV_URL, registry_discovery_region_default)


def _get_cloud_environment_infos_by_metadata_url(metadata_url: str) -> Dict[str, Dict[str, str]]:
    """Get the environment information for all clouds specified by the metadata url.

    :param metadata_url: SDK metadata URL
    :type metadata_url: str
    :return: All relevant clouds and their environment information.
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


def _convert_arm_to_cli(arm_cloud_metadata: Any[List[Dict[str, str]], Dict[str, str]]) -> Dict[str, str]:
    """Convert JSON ARM cloud metadata responses to CLI-friendly strings.

    :param arm_cloud_metadata: ARM cloud metadata responses
    :type arm_cloud_metadata: Any[List[Dict[str, str]], Dict[str, str]]
    :return: Cloud metadata
    :rtype: Dict[str, str]
    """
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


def _add_cloud_to_environments(kwargs) -> None:
    """Add a cloud name to the _environments variable.

    :param kwargs: All cloud information.
    :type kwargs: Dict[str, str]
    :raises AttributeError: If cloud name already exists in _environments
    :raises LookupError: If the cloud name's metadata is not present in kwargs
    """
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

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Metadata to interact with different Azure clouds."""

import configparser
import logging
import os
import sys
from typing import Dict, Optional

from azure.ai.ml._utils.utils import _get_mfe_url_override
from azure.ai.ml.constants._common import AZUREML_CLOUD_ENV_NAME
from azure.ai.ml.constants._common import ArmConstants

module_logger = logging.getLogger(__name__)


class AzureEnvironments:
    ENV_DEFAULT = "AzureCloud"
    ENV_US_GOVERNMENT = "AzureUSGovernment"
    ENV_CHINA = "AzureChinaCloud"


class EndpointURLS:  # pylint: disable=too-few-public-methods,no-init
    AZURE_PORTAL_ENDPOINT = "azure_portal"
    RESOURCE_MANAGER_ENDPOINT = "resource_manager"
    ACTIVE_DIRECTORY_ENDPOINT = "active_directory"
    AML_RESOURCE_ID = "aml_resource_id"
    STORAGE_ENDPOINT = "storage_endpoint"
    REGISTRY_DISCOVERY_ENDPOINT = "registry_discovery_endpoint"


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


def _get_default_cloud_name():
    """Return AzureCloud as the default cloud."""
    return os.getenv(AZUREML_CLOUD_ENV_NAME, AzureEnvironments.ENV_DEFAULT)


def _get_cloud_details(cloud: str = AzureEnvironments.ENV_DEFAULT):
    """Returns a Cloud endpoints object for the specified Azure Cloud.

    :param cloud: cloud name
    :return: azure environment endpoint.
    """
    if cloud is None:
        module_logger.debug(
            "Using the default cloud configuration: '%s'.",
            AzureEnvironments.ENV_DEFAULT,
        )
        cloud = _get_default_cloud_name()
    try:
        all_clouds = _get_all_clouds()
        azure_environment = all_clouds[cloud]
        module_logger.debug("Using the cloud configuration: '%s'.", azure_environment)
    except KeyError:
        raise Exception('Unknown cloud environment "{0}".'.format(cloud))
    return azure_environment


def _set_cloud(cloud: str = AzureEnvironments.ENV_DEFAULT):
    if cloud is not None:
        if cloud not in _get_all_clouds():
            raise Exception('Unknown cloud environment supplied: "{0}".'.format(cloud))
    else:
        cloud = _get_default_cloud_name()
    os.environ[AZUREML_CLOUD_ENV_NAME] = cloud


def _get_base_url_from_metadata(cloud_name: Optional[str] = None, is_local_mfe: bool = False):
    """Retrieve the base url for a cloud from the metadata in SDK.

    :param cloud_name: cloud name
    :return: base url for a cloud
    """
    base_url = None
    if is_local_mfe:
        base_url = _get_mfe_url_override()

    if base_url is None:
        cloud_details = _get_cloud_details(cloud_name)
        base_url = cloud_details.get(EndpointURLS.RESOURCE_MANAGER_ENDPOINT).strip("/")
    return base_url


def _get_aml_resource_id_from_metadata(cloud_name: Optional[str] = None):
    """Retrieve the aml_resource_id for a cloud from the metadata in SDK.

    :param cloud_name: cloud name
    :return: aml_resource_id for a cloud
    """
    cloud_details = _get_cloud_details(cloud_name)
    aml_resource_id = cloud_details.get(EndpointURLS.AML_RESOURCE_ID).strip("/")
    return aml_resource_id


def _get_active_directory_url_from_metadata(cloud_name: Optional[str] = None):
    """Retrieve the active_directory_url for a cloud from the metadata in SDK.

    :param cloud_name: cloud name
    :return: active_directory for a cloud
    """
    cloud_details = _get_cloud_details(cloud_name)
    active_directory_url = cloud_details.get(EndpointURLS.ACTIVE_DIRECTORY_ENDPOINT).strip("/")
    return active_directory_url


def _get_storage_endpoint_from_metadata(cloud_name: Optional[str] = None):
    """Retrieve the storage_endpoint for a cloud from the metadata in SDK.

    :param cloud_name: cloud name
    :return: storage_endpoint for a cloud
    """
    cloud_details = _get_cloud_details(cloud_name)
    storage_endpoint = cloud_details.get(EndpointURLS.STORAGE_ENDPOINT)
    return storage_endpoint


def _get_azure_portal_id_from_metadata(cloud_name: Optional[str] = None):
    """Retrieve the azure_portal_id for a cloud from the metadata in SDK.

    :param cloud_name: cloud name
    :return: azure_portal_id for a cloud
    """
    cloud_details = _get_cloud_details(cloud_name)
    azure_portal_id = cloud_details.get(EndpointURLS.AZURE_PORTAL_ENDPOINT)
    return azure_portal_id


def _get_cloud_information_from_metadata(cloud_name: Optional[str] = None, **kwargs) -> Dict:
    """Retrieve the cloud information from the metadata in SDK.

    :param cloud_name: cloud name
    :return: A dictionary of additional configuration parameters required for passing in cloud information.
    """
    cloud_details = _get_cloud_details(cloud_name)
    credential_scopes = _resource_to_scopes(cloud_details.get(EndpointURLS.RESOURCE_MANAGER_ENDPOINT).strip("/"))

    # Update the kwargs with the cloud information
    client_kwargs = {"cloud": cloud_name}
    if credential_scopes is not None:
        client_kwargs["credential_scopes"] = credential_scopes
    kwargs.update(client_kwargs)
    return kwargs


def _get_registry_discovery_endpoint_from_metadata(cloud_name: Optional[str] = None):
    """Retrieve the registry_discovery_endpoint for a cloud from the metadata in SDK.

    :param cloud_name: cloud name
    :return: registry_discovery_endpoint for a cloud
    """
    cloud_details = _get_cloud_details(cloud_name)
    registry_discovery_endpoint = cloud_details.get(EndpointURLS.REGISTRY_DISCOVERY_ENDPOINT)
    return registry_discovery_endpoint


def _resource_to_scopes(resource):
    """Convert the resource ID to scopes by appending the /.default suffix and
    return a list. For example: 'https://management.core.windows.net/' ->
    ['https://management.core.windows.net//.default']

    :param resource: The resource ID
    :return: A list of scopes
    """
    scope = resource + "/.default"
    return [scope]

def _get_clouds_by_metadata_url(metadata_url, timeout=ArmConstants.DEFAULT_TIMEOUT):
    """Get all the clouds by the specified metadata url

        :return: list of the clouds
    """
    try:
        import requests
        module_logger.debug('Start : Loading cloud metatdata from the url specified by {0}'.format(metadata_url))
        with requests.get(metadata_url, timeout=timeout) as meta_response:
            arm_cloud_dict = meta_response.json()
            cli_cloud_dict = _convert_arm_to_cli(arm_cloud_dict)
            module_logger.debug('Finish : Loading cloud metatdata from the url specified by {0}'.format(metadata_url))
            return cli_cloud_dict
    except Exception as ex:  # pylint: disable=broad-except
        module_logger.warning("Error: Azure ML was unable to load cloud metadata from the url specified by {0}. {1}. "
                        "This may be due to a misconfiguration of networking controls. Azure Machine Learning Python SDK "
                        "requires outbound access to Azure Resource Manager. Please contact your networking team to configure "
                        "outbound access to Azure Resource Manager on both Network Security Group and Firewall. "
                        "For more details on required configurations, see "
                        "https://docs.microsoft.com/azure/machine-learning/how-to-access-azureml-behind-firewall.".format(
            metadata_url, ex))
        return {}

def _convert_arm_to_cli(arm_cloud_metadata):
    cli_cloud_metadata_dict = {}
    if isinstance(arm_cloud_metadata, dict):
        arm_cloud_metadata = [arm_cloud_metadata]
    for cloud in arm_cloud_metadata:
        try:
            cli_cloud_metadata_dict[cloud['name']] = {
                EndpointURLS.AZURE_PORTAL_ENDPOINT: cloud["portal"],
                EndpointURLS.RESOURCE_MANAGER_ENDPOINT: cloud["resourceManager"],
                EndpointURLS.ACTIVE_DIRECTORY_ENDPOINT: cloud["authentication"]["loginEndpoint"],
                EndpointURLS.AML_RESOURCE_ID: cloud["resourceManager"],
                EndpointURLS.STORAGE_ENDPOINT: cloud["suffixes"]["storage"]
            }
        except KeyError as ex:
            continue
    return cli_cloud_metadata_dict

def _get_all_clouds():
    # Start with the hard coded list of clouds in this file
    all_clouds = {}
    all_clouds.update(_environments)
    # Get configs from the config file
    config = configparser.ConfigParser()
    for section in config.sections():
        all_clouds[section] = dict(config.items(section))
    # Now do the metadata URL
    arm_url = os.environ.get(ArmConstants.METADATA_URL_ENV_NAME,ArmConstants.DEFAULT_URL)
    all_clouds.update(_get_clouds_by_metadata_url(arm_url))
    # Send them all along with the hardcoded environments
    return all_clouds


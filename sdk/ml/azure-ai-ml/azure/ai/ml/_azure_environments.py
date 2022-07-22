# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Metadata to interact with different Azure clouds
"""

from typing import Dict
from azure.ai.ml.constants import AZUREML_CLOUD_ENV_NAME
from azure.ai.ml._utils.utils import _get_mfe_url_override
import os
import logging

module_logger = logging.getLogger(__name__)


class AZURE_ENVIRONMENTS:
    ENV_DEFAULT = "AzureCloud"
    ENV_US_GOVERNMENT = "AzureUSGovernment"
    ENV_CHINA = "AzureChinaCloud"


class ENDPOINT_URLS:  # pylint: disable=too-few-public-methods,old-style-class,no-init
    AZURE_PORTAL_ENDPOINT = "azure_portal"
    RESOURCE_MANAGER_ENDPOINT = "resource_manager"
    ACTIVE_DIRECTORY_ENDPOINT = "active_directory"
    AML_RESOURCE_ID = "aml_resource_id"
    STORAGE_ENDPOINT = "storage_endpoint"


_environments = {
    AZURE_ENVIRONMENTS.ENV_DEFAULT: {
        ENDPOINT_URLS.AZURE_PORTAL_ENDPOINT: "https://portal.azure.com/",
        ENDPOINT_URLS.RESOURCE_MANAGER_ENDPOINT: "https://management.azure.com/",
        ENDPOINT_URLS.ACTIVE_DIRECTORY_ENDPOINT: "https://login.microsoftonline.com/",
        ENDPOINT_URLS.AML_RESOURCE_ID: "https://ml.azure.com/",
        ENDPOINT_URLS.STORAGE_ENDPOINT: "core.windows.net",
    },
    AZURE_ENVIRONMENTS.ENV_CHINA: {
        ENDPOINT_URLS.AZURE_PORTAL_ENDPOINT: "https://portal.azure.cn/",
        ENDPOINT_URLS.RESOURCE_MANAGER_ENDPOINT: "https://management.chinacloudapi.cn/",
        ENDPOINT_URLS.ACTIVE_DIRECTORY_ENDPOINT: "https://login.chinacloudapi.cn/",
        ENDPOINT_URLS.AML_RESOURCE_ID: "https://ml.azure.cn/",
        ENDPOINT_URLS.STORAGE_ENDPOINT: "core.chinacloudapi.cn",
    },
    AZURE_ENVIRONMENTS.ENV_US_GOVERNMENT: {
        ENDPOINT_URLS.AZURE_PORTAL_ENDPOINT: "https://portal.azure.us/",
        ENDPOINT_URLS.RESOURCE_MANAGER_ENDPOINT: "https://management.usgovcloudapi.net/",
        ENDPOINT_URLS.ACTIVE_DIRECTORY_ENDPOINT: "https://login.microsoftonline.us/",
        ENDPOINT_URLS.AML_RESOURCE_ID: "https://ml.azure.us/",
        ENDPOINT_URLS.STORAGE_ENDPOINT: "core.usgovcloudapi.net",
    },
}


def _get_default_cloud_name():
    """Return AzureCloud as the default cloud"""
    return os.getenv(AZUREML_CLOUD_ENV_NAME, AZURE_ENVIRONMENTS.ENV_DEFAULT)


def _get_cloud_details(cloud: str = AZURE_ENVIRONMENTS.ENV_DEFAULT):
    """Returns a Cloud endpoints object for the specified Azure Cloud

    :param cloud: cloud name
    :return: azure environment endpoint.
    """
    if cloud is None:
        module_logger.debug("Using the default cloud configuration: '%s'.", AZURE_ENVIRONMENTS.ENV_DEFAULT)
        cloud = _get_default_cloud_name()
    try:
        azure_environment = _environments[cloud]
        module_logger.debug("Using the cloud configuration: '%s'.", azure_environment)
    except KeyError:
        raise Exception('Unknown cloud environment "{0}".'.format(cloud))
    return azure_environment


def _set_cloud(cloud: str = AZURE_ENVIRONMENTS.ENV_DEFAULT):
    if cloud is not None:
        if cloud not in _environments:
            raise Exception('Unknown cloud environment supplied: "{0}".'.format(cloud))
    else:
        cloud = _get_default_cloud_name()
    os.environ[AZUREML_CLOUD_ENV_NAME] = cloud


def _get_base_url_from_metadata(cloud_name: str = None, is_local_mfe: bool = False):
    """Retrieve the base url for a cloud from the metadata in SDK.

    :param cloud_name: cloud name
    :return: base url for a cloud
    """
    base_url = None
    if is_local_mfe:
        base_url = _get_mfe_url_override()

    if base_url is None:
        cloud_details = _get_cloud_details(cloud_name)
        base_url = cloud_details.get(ENDPOINT_URLS.RESOURCE_MANAGER_ENDPOINT).strip("/")
    return base_url


def _get_aml_resource_id_from_metadata(cloud_name: str = None):
    """Retrieve the aml_resource_id for a cloud from the metadata in SDK.

    :param cloud_name: cloud name
    :return: aml_resource_id for a cloud
    """
    cloud_details = _get_cloud_details(cloud_name)
    aml_resource_id = cloud_details.get(ENDPOINT_URLS.AML_RESOURCE_ID).strip("/")
    return aml_resource_id


def _get_active_directory_url_from_metadata(cloud_name: str = None):
    """Retrieve the active_directory_url for a cloud from the metadata in SDK.

    :param cloud_name: cloud name
    :return: active_directory for a cloud
    """
    cloud_details = _get_cloud_details(cloud_name)
    active_directory_url = cloud_details.get(ENDPOINT_URLS.ACTIVE_DIRECTORY_ENDPOINT).strip("/")
    return active_directory_url


def _get_storage_endpoint_from_metadata(cloud_name: str = None):
    """Retrieve the storage_endpoint for a cloud from the metadata in SDK.

    :param cloud_name: cloud name
    :return: storage_endpoint for a cloud
    """
    cloud_details = _get_cloud_details(cloud_name)
    storage_endpoint = cloud_details.get(ENDPOINT_URLS.STORAGE_ENDPOINT)
    return storage_endpoint


def _get_azure_portal_id_from_metadata(cloud_name: str = None):
    """Retrieve the azure_portal_id for a cloud from the metadata in SDK.

    :param cloud_name: cloud name
    :return: azure_portal_id for a cloud
    """
    cloud_details = _get_cloud_details(cloud_name)
    azure_portal_id = cloud_details.get(ENDPOINT_URLS.AZURE_PORTAL_ENDPOINT)
    return azure_portal_id


def _get_cloud_information_from_metadata(cloud_name: str = None, **kwargs) -> Dict:
    """Retrieve the cloud information from the metadata in SDK.

    :param cloud_name: cloud name
    :return: A dictionary of additional configuration parameters required for passing in cloud information.
    """
    cloud_details = _get_cloud_details(cloud_name)
    credential_scopes = _resource_to_scopes(cloud_details.get(ENDPOINT_URLS.RESOURCE_MANAGER_ENDPOINT).strip("/"))

    # Update the kwargs with the cloud information
    client_kwargs = {"cloud": cloud_name}
    if credential_scopes is not None:
        client_kwargs["credential_scopes"] = credential_scopes
    kwargs.update(client_kwargs)
    return kwargs


def _resource_to_scopes(resource):
    """Convert the resource ID to scopes by appending the /.default suffix and return a list.
    For example: 'https://management.core.windows.net/' -> ['https://management.core.windows.net//.default']

    :param resource: The resource ID
    :return: A list of scopes
    """
    scope = resource + "/.default"
    return [scope]

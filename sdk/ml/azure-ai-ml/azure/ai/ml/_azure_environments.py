# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Metadata to interact with different Azure clouds
"""

from azure.ai.ml.constants import AZUREML_CLOUD_ENV_NAME
import os
import logging

module_logger = logging.getLogger(__name__)


class AZURE_ENVIRONMENTS:
    ENV_DEFAULT = "AzureCloud"
    ENV_US_GOVERNMENT = "AzureUSGovernment"
    ENV_CHINA = "AzureChinaCloud"
    ENV_GERMAN = "AzureGermanCloud"
    ENV_USNAT = "USNat"
    ENV_USSEC = "USSec"


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
    AZURE_ENVIRONMENTS.ENV_GERMAN: {
        ENDPOINT_URLS.AZURE_PORTAL_ENDPOINT: "https://portal.azure.de/",
        ENDPOINT_URLS.RESOURCE_MANAGER_ENDPOINT: "https://management.microsoftazure.de/",
        ENDPOINT_URLS.ACTIVE_DIRECTORY_ENDPOINT: "https://login.microsoftonline.de/",
        ENDPOINT_URLS.AML_RESOURCE_ID: "https://ml.azure.de",
        ENDPOINT_URLS.STORAGE_ENDPOINT: "core.cloudapi.de",
    },
    AZURE_ENVIRONMENTS.ENV_USNAT: {
        ENDPOINT_URLS.AZURE_PORTAL_ENDPOINT: "https://portal.azure.eaglex.ic.gov/",
        ENDPOINT_URLS.RESOURCE_MANAGER_ENDPOINT: "https://management.azure.eaglex.ic.gov/",
        ENDPOINT_URLS.ACTIVE_DIRECTORY_ENDPOINT: "https://login.microsoftonline.eaglex.ic.gov/",
        ENDPOINT_URLS.AML_RESOURCE_ID: "https://ml.azure.eaglex.ic.gov",
        ENDPOINT_URLS.STORAGE_ENDPOINT: "core.eaglex.ic.gov",
    },
    AZURE_ENVIRONMENTS.ENV_USSEC: {
        ENDPOINT_URLS.AZURE_PORTAL_ENDPOINT: "https://portal.azure.scloud/",
        ENDPOINT_URLS.RESOURCE_MANAGER_ENDPOINT: "https://management.azure.microsoft.scloud/",
        ENDPOINT_URLS.ACTIVE_DIRECTORY_ENDPOINT: "https://login.microsoftonline.microsoft.scloud/",
        ENDPOINT_URLS.AML_RESOURCE_ID: "https://ml.azure.microsoft.scloud",
        ENDPOINT_URLS.STORAGE_ENDPOINT: "core.microsoft.scloud",
    },
}


def _get_default_cloud_name():
    """Return AzureCloud as the default cloud"""
    return os.getenv(AZUREML_CLOUD_ENV_NAME, AZURE_ENVIRONMENTS.ENV_DEFAULT)


def _get_cloud_details(cloud=None):
    if cloud is None:
        module_logger.debug("Using the default cloud configuration: '%s'.", AZURE_ENVIRONMENTS.ENV_DEFAULT)
        cloud = _get_default_cloud_name()
    try:
        azure_environment = _environments[cloud]
        module_logger.debug("Using the cloud configuration: '%s'.", azure_environment)
    except KeyError:
        raise Exception('Unknown cloud environment "{0}".'.format(cloud))
    return azure_environment


def _set_cloud(cloud=None):
    if cloud is not None:
        if cloud not in _environments:
            raise Exception('Unknown cloud environment supplied: "{0}".'.format(cloud))
    else:
        cloud = _get_default_cloud_name()
    os.environ[AZUREML_CLOUD_ENV_NAME] = cloud


def resource_to_scopes(resource):
    """Convert the resource ID to scopes by appending the /.default suffix and return a list.
    For example: 'https://management.core.windows.net/' -> ['https://management.core.windows.net//.default']

    :param resource: The resource ID
    :return: A list of scopes
    """
    scope = resource + "/.default"
    return [scope]

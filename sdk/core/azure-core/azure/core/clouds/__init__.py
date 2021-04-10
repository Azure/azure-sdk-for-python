# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------

# This file contains long URLs/strings etc. Not too much value in warning about long lines.
# pylint: disable=C0301

"""Cloud configuration metadata management.

Example:
>>> from azure.core.settings import settings
>>> settings.cloud_configuration = 'AzureGermanCloud'
>>> settings.cloud_configuration()['portal']['endpoint']
'https://portal.microsoftazure.de'

>>> # Load metada from metadata endpoint
>>> import requests
>>> metadata = requests.get('https://management.azure.com/metadata/endpoints?api-version=2019-05-01').json()
>>> govcloud = [config for config in metadata if config['name'] == 'AzureUSGovernment'][0]
>>> settings.cloud_configuration = CloudConfig.from_metadata_dict(govcloud)
>>> settings.cloud_configuration()['portal']['endpoint']
'https://portal.azure.us'
"""


import typing

__all__ = ["well_known", "CloudConfiguration"]

_raw_data = [
    {
        "portal": "https://portal.azure.cn",
        "authentication": {
            "loginEndpoint": "https://login.chinacloudapi.cn",
            "audiences": [
                "https://management.core.chinacloudapi.cn",
                "https://management.chinacloudapi.cn",
            ],
            "tenant": "common",
            "identityProvider": "AAD",
        },
        "media": "https://rest.media.chinacloudapi.cn",
        "graphAudience": "https://graph.chinacloudapi.cn",
        "graph": "https://graph.chinacloudapi.cn",
        "name": "AzureChinaCloud",
        "suffixes": {
            "acrLoginServer": "azurecr.cn",
            "sqlServerHostname": "database.chinacloudapi.cn",
            "keyVaultDns": "vault.azure.cn",
            "storage": "core.chinacloudapi.cn",
            "azureFrontDoorEndpointSuffix": "",
        },
        "batch": "https://batch.chinacloudapi.cn",
        "resourceManager": "https://management.chinacloudapi.cn",
        "vmImageAliasDoc": "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-compute/quickstart-templates/aliases.json",
        "sqlManagement": "https://management.core.chinacloudapi.cn:8443",
        "gallery": "https://gallery.chinacloudapi.cn",
    },
    {
        "portal": "https://portal.azure.us",
        "authentication": {
            "loginEndpoint": "https://login.microsoftonline.us",
            "audiences": [
                "https://management.core.usgovcloudapi.net",
                "https://management.usgovcloudapi.net",
            ],
            "tenant": "common",
            "identityProvider": "AAD",
        },
        "media": "https://rest.media.usgovcloudapi.net",
        "graphAudience": "https://graph.windows.net",
        "graph": "https://graph.windows.net",
        "name": "AzureUSGovernment",
        "suffixes": {
            "acrLoginServer": "azurecr.us",
            "sqlServerHostname": "database.usgovcloudapi.net",
            "keyVaultDns": "vault.usgovcloudapi.net",
            "storage": "core.usgovcloudapi.net",
            "azureFrontDoorEndpointSuffix": "",
        },
        "batch": "https://batch.core.usgovcloudapi.net",
        "resourceManager": "https://management.usgovcloudapi.net",
        "vmImageAliasDoc": "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-compute/quickstart-templates/aliases.json",
        "sqlManagement": "https://management.core.usgovcloudapi.net:8443",
        "gallery": "https://gallery.usgovcloudapi.net",
    },
    {
        "portal": "https://portal.microsoftazure.de",
        "authentication": {
            "loginEndpoint": "https://login.microsoftonline.de",
            "audiences": [
                "https://management.core.cloudapi.de",
                "https://management.microsoftazure.de",
            ],
            "tenant": "common",
            "identityProvider": "AAD",
        },
        "media": "https://rest.media.cloudapi.de",
        "graphAudience": "https://graph.cloudapi.de",
        "graph": "https://graph.cloudapi.de",
        "name": "AzureGermanCloud",
        "suffixes": {
            "sqlServerHostname": "database.cloudapi.de",
            "keyVaultDns": "vault.microsoftazure.de",
            "storage": "core.cloudapi.de",
            "azureFrontDoorEndpointSuffix": "",
        },
        "batch": "https://batch.cloudapi.de",
        "resourceManager": "https://management.microsoftazure.de",
        "vmImageAliasDoc": "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-compute/quickstart-templates/aliases.json",
        "sqlManagement": "https://management.core.cloudapi.de:8443",
        "gallery": "https://gallery.cloudapi.de",
    },
    {
        "portal": "https://portal.azure.com",
        "authentication": {
            "loginEndpoint": "https://login.microsoftonline.com/",
            "audiences": [
                "https://management.core.windows.net/",
                "https://management.azure.com/",
            ],
            "tenant": "common",
            "identityProvider": "AAD",
        },
        "media": "https://rest.media.azure.net",
        "graphAudience": "https://graph.windows.net/",
        "graph": "https://graph.windows.net/",
        "name": "AzureCloud",
        "suffixes": {
            "azureDataLakeStoreFileSystem": "azuredatalakestore.net",
            "acrLoginServer": "azurecr.io",
            "sqlServerHostname": "database.windows.net",
            "azureDataLakeAnalyticsCatalogAndJob": "azuredatalakeanalytics.net",
            "keyVaultDns": "vault.azure.net",
            "storage": "core.windows.net",
            "azureFrontDoorEndpointSuffix": "azurefd.net",
        },
        "batch": "https://batch.core.windows.net/",
        "resourceManager": "https://management.azure.com/",
        "vmImageAliasDoc": "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-compute/quickstart-templates/aliases.json",
        "activeDirectoryDataLake": "https://datalake.azure.net/",
        "sqlManagement": "https://management.core.windows.net:8443/",
        "gallery": "https://gallery.azure.com/",
    },
]


class CloudConfiguration(dict):
    """Configuration for a specific cloud instance"""

    @classmethod
    def from_metadata_dict(cls, data, **kwargs):
        """Load cloud configuration entry in format as returned from azure resource manager metadata
        endpoint (e.g. https://management.azure.com/metadata/endpoints)

        :param data: One entry in metadata returned.
        :type data: ~dict
        :keyword api_version: Api Version (format) used to retrieve the data. Default value: 2019-05-01.
        :type api_version: ~str
        :rtype: ~CloudConfig
        """
        if kwargs.pop("api_version", "2019-05-01") != "2019-05-01":
            raise ValueError('Unknown API version - supported value is: "2019-05-01"')

        transformed_data = {
            "global": {
                "authentication": {
                    "endpoint": data.get("authentication", {}).get("loginEndpoint", None),
                    "audiences": data.get("authentication", {}).get("audiences", []),
                },
            },
            "batch": {"endpoint": data.get("endpoint", None)},
            "containerRegistry": {"suffix": data.get("acrLoginServer", None)},
            "dataLakeStorageFileSystem": {
                "suffix": data.get("suffixes", {}).get("azureDataLakeStoreFileSystem")
            },
            "dataLakeAnalyticsCatalogAndJob": {
                "suffix": data.get("suffixes", {}).get(
                    "azureDataLakeAnalyticsCatalogAndJob"
                )
            },
            "gallery": {"endpoint": data.get("gallery", None)},
            "graph": {
                "endpoint": data.get("graph", None),
                "authentication": {
                    "audiences": [data["graphAudience"]]
                    if data.get("graphAudience", None)
                    else []
                },
            },
            "keyVault": {"suffix": data.get("suffixes", {}).get("keyVaultDns")},
            "media": {"endpoint": data.get("media", None)},
            "portal": {"endpoint": data.get("portal", None)},
            "resourceManager": {
                "endpoint": data.get("resourceManager", None),
            },
            "sql": {"suffix": data.get("suffixes", {}).get("sqlServerHostname")},
            "sqlManagement": {"endpoint": data.get("sqlManagement", None)},
            "storage": {"suffix": data.get("suffixes", {}).get("storage", None)},
        }
        return cls(transformed_data)


well_known = {item["name"]: CloudConfiguration.from_metadata_dict(item) for item in _raw_data}

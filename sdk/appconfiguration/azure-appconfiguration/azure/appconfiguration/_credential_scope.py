# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

# Azure Configuration audience URLs
DEFAULT_SCOPE_SUFFIX = ".default"
_AZURE_PUBLIC_CLOUD_SCOPE = "https://appconfig.azure.com/"
_AZURE_US_GOVERNMENT_SCOPE = "https://appconfig.azure.us/"
_AZURE_CHINA_SCOPE = "https://appconfig.azure.cn/"


# Endpoint suffixes for cloud detection
_US_GOVERNMENT_SUFFIX_LEGACY = "azconfig.azure.us"  # cspell:disable-line
_US_GOVERNMENT_SUFFIX = "appconfig.azure.us"
_CHINA_SUFFIX_LEGACY = "azconfig.azure.cn"  # cspell:disable-line
_CHINA_SUFFIX = "appconfig.azure.cn"


def get_audience(endpoint: str) -> str:
    """
    Gets the default scope for the given endpoint.

    :param endpoint: The endpoint to get the default scope for.
    :type endpoint: str
    :return: The default scope for the given endpoint.
    :rtype: str
    """
    # Normalize endpoint by stripping trailing slashes and converting to lowercase for suffix checks
    normalized_endpoint = endpoint.rstrip("/").lower()
    if normalized_endpoint.endswith(_US_GOVERNMENT_SUFFIX_LEGACY) or normalized_endpoint.endswith(
        _US_GOVERNMENT_SUFFIX
    ):
        return _AZURE_US_GOVERNMENT_SCOPE
    if normalized_endpoint.endswith(_CHINA_SUFFIX_LEGACY) or normalized_endpoint.endswith(_CHINA_SUFFIX):
        return _AZURE_CHINA_SCOPE
    return _AZURE_PUBLIC_CLOUD_SCOPE

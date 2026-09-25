# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from urllib.parse import urlparse

DEFAULT_SCOPE_SUFFIX = ".default"
_AZURE_PUBLIC_CLOUD_AUDIENCE = "https://appconfig.azure.com/"
_STAGING_DOMAIN = "appconfig-staging.azure.com"


def get_audience(endpoint: str) -> str:
    """
    Infers the audience from the endpoint hostname, falling back to Azure Public Cloud.

    :param endpoint: The endpoint to get the default audience for.
    :type endpoint: str
    :return: The default audience for the given endpoint.
    :rtype: str
    """
    hostname = urlparse(endpoint).hostname or ""
    if hostname.endswith(f".{_STAGING_DOMAIN}"):
        return f"https://{_STAGING_DOMAIN}/"

    labels = hostname.split(".")
    for index in range(len(labels) - 1, -1, -1):
        if labels[index] in ("appconfig", "azconfig"):
            return f"https://{'.'.join(labels[index:])}/"

    return _AZURE_PUBLIC_CLOUD_AUDIENCE

# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

"""
FILE: sample_utilities.py
DESCRIPTION:
    This file include some utility functions for samples to use:
    - get_authority(): get authority of the ConfigurationClient
    - get_audience(): get audience of the ConfigurationClient
    - get_credential(): get credential of the ConfigurationClient
    It is not a file expected to run independently.
"""

import os
from azure.identity import AzureAuthorityHosts, ClientSecretCredential, DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential


def get_authority(endpoint):
    # cSpell:ignore azconfig
    if ".azconfig.io" in endpoint:
        return AzureAuthorityHosts.AZURE_PUBLIC_CLOUD
    if ".azconfig.azure.cn" in endpoint:
        return AzureAuthorityHosts.AZURE_CHINA
    if ".azconfig.azure.us" in endpoint:
        return AzureAuthorityHosts.AZURE_GOVERNMENT
    raise ValueError(f"Endpoint ({endpoint}) could not be understood")


def get_audience(authority):
    if authority == AzureAuthorityHosts.AZURE_PUBLIC_CLOUD:
        return "https://management.azure.com"
    if authority == AzureAuthorityHosts.AZURE_CHINA:
        return "https://management.chinacloudapi.cn"
    if authority == AzureAuthorityHosts.AZURE_GOVERNMENT:
        return "https://management.usgovcloudapi.net"


def get_credential(authority, **kwargs):
    if authority != AzureAuthorityHosts.AZURE_PUBLIC_CLOUD:
        return ClientSecretCredential(
            tenant_id=os.environ.get("AZURE_TENANT_ID"),
            client_id=os.environ.get("AZURE_CLIENT_ID"),
            client_secret=os.environ.get("AZURE_CLIENT_SECRET"),
            authority=authority,
        )
    is_async = kwargs.pop("is_async", False)
    if is_async:
        return AsyncDefaultAzureCredential(**kwargs)
    return DefaultAzureCredential(**kwargs)

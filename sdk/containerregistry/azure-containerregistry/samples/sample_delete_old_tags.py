# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_delete_old_tags.py

DESCRIPTION:
    These samples demonstrates deleting the three oldest tags for each repository

USAGE:
    python sample_delete_old_tags.py

    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account
"""

from dotenv import find_dotenv, load_dotenv
import os

from azure.identity import AzureAuthorityHosts


class DeleteOperations(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]

    def get_authority(self, endpoint):
        if ".azurecr.io" in endpoint:
            return AzureAuthorityHosts.AZURE_PUBLIC_CLOUD
        if ".azurecr.cn" in endpoint:
            return AzureAuthorityHosts.AZURE_CHINA
        if ".azurecr.us" in endpoint:
            return AzureAuthorityHosts.AZURE_GOVERNMENT
        raise ValueError("Endpoint ({}) could not be understood".format(endpoint))

    def get_credential_scopes(self, authority):
        if authority == AzureAuthorityHosts.AZURE_PUBLIC_CLOUD:
            return "https://management.core.windows.net/.default"
        if authority == AzureAuthorityHosts.AZURE_CHINA:
            return "https://management.chinacloudapi.cn/.default"
        if authority == AzureAuthorityHosts.AZURE_GOVERNMENT:
            return "https://management.usgovcloudapi.net/.default"

    def delete_old_tags(self):
        from azure.containerregistry import ContainerRegistryClient, TagOrder
        from azure.identity import DefaultAzureCredential

        # [START list_repository_names]
        account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
        authority = self.get_authority(account_url)
        credential = DefaultAzureCredential(authority=authority)
        credential_scopes = self.get_credential_scopes(authority)

        client = ContainerRegistryClient(account_url, credential, credential_scopes=credential_scopes)

        for repository in client.list_repository_names():
            print(repository)
            # [END list_repository_names]

            # [START list_tag_properties]
            # Keep the three most recent tags, delete everything else
            tag_count = 0
            tags = client.list_tag_properties(repository, order_by=TagOrder.LAST_UPDATE_TIME_DESCENDING)
            for tag in tags[3:]:
                client.delete_tag(repository, tag.name)
            # [END list_tag_properties]

        client.close()

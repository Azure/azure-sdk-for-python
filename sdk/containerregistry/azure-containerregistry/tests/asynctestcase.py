# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os

from azure.containerregistry.aio import (
    ContainerRegistryClient,
)

from azure.core.credentials import AccessToken
from azure.identity.aio import DefaultAzureCredential, ClientSecretCredential
from azure.identity import AzureAuthorityHosts

from testcase import ContainerRegistryTestClass

logger = logging.getLogger()

class AsyncFakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """

    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    async def get_token(self, *args):
        return self.token


class AsyncContainerRegistryTestClass(ContainerRegistryTestClass):
    def __init__(self, method_name):
        super(AsyncContainerRegistryTestClass, self).__init__(method_name)

    def get_credential(self, authority=None, **kwargs):
        if self.is_live:
            if authority != AzureAuthorityHosts.AZURE_PUBLIC_CLOUD:
                return ClientSecretCredential(
                    tenant_id=os.environ["CONTAINERREGISTRY_TENANT_ID"],
                    client_id=os.environ["CONTAINERREGISTRY_CLIENT_ID"],
                    client_secret=os.environ["CONTAINERREGISTRY_CLIENT_SECRET"],
                    authority=authority
                )
            return DefaultAzureCredential(**kwargs)
        return AsyncFakeTokenCredential()

    def create_registry_client(self, endpoint, **kwargs):
        return ContainerRegistryClient(
            endpoint=endpoint,
            credential=self.get_credential(),
            **kwargs,
        )

    def create_registry_client(self, endpoint, **kwargs):
        authority = get_authority(endpoint)
        authorization_scope = get_authorization_scope(authority)
        credential = self.get_credential(authority=authority)
        return ContainerRegistryClient(endpoint=endpoint, credential=credential, authentication_scope=authorization_scope, **kwargs)

    def create_anon_client(self, endpoint, **kwargs):
        return ContainerRegistryClient(endpoint=endpoint, credential=None, **kwargs)


def get_authority(endpoint):
    if ".azurecr.io" in endpoint:
        logger.warning("Public cloud Authority:")
        return AzureAuthorityHosts.AZURE_PUBLIC_CLOUD
    if ".azurecr.cn" in endpoint:
        logger.warning("China Authority:")
        return AzureAuthorityHosts.AZURE_CHINA
    if ".azurecr.us" in endpoint:
        logger.warning("US Gov Authority:")
        return AzureAuthorityHosts.AZURE_GOVERNMENT
    raise ValueError("Endpoint ({}) could not be understood".format(endpoint))


def get_authorization_scope(authority):
    if authority == AzureAuthorityHosts.AZURE_PUBLIC_CLOUD:
        logger.warning("Public auth scope")
        return "https://management.core.windows.net/.default"
    if authority == AzureAuthorityHosts.AZURE_CHINA:
        logger.warning("China scope")
        return "https://management.chinacloudapi.cn/.default"
    if authority == AzureAuthorityHosts.AZURE_GOVERNMENT:
        logger.warning("US Gov scope")
        return "https://management.usgovcloudapi.net/.default"

def get_base_url(authority):
    if authority == AzureAuthorityHosts.AZURE_PUBLIC_CLOUD:
        logger.warning("Public auth scope")
        return AZURE_PUBLIC_CLOUD
    if authority == AzureAuthorityHosts.AZURE_CHINA:
        logger.warning("China scope")
        return AZURE_CHINA_CLOUD
    if authority == AzureAuthorityHosts.AZURE_GOVERNMENT:
        logger.warning("US Gov scope")
        return AZURE_US_GOV_CLOUD
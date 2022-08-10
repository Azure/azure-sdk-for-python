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

from testcase import ContainerRegistryTestClass, get_audience, get_authority

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
        authority = get_authority(endpoint)
        audience = kwargs.pop("audience", None)
        if not audience:
            audience = get_audience(authority)
        credential = self.get_credential(authority=authority)
        return ContainerRegistryClient(endpoint=endpoint, credential=credential, audience=audience, **kwargs)

    def create_anon_client(self, endpoint, **kwargs):
        authority = get_authority(endpoint)
        audience = get_audience(authority)
        return ContainerRegistryClient(endpoint=endpoint, credential=None, audience=audience, **kwargs)

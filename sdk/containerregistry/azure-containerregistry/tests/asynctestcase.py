# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os

from azure.containerregistry.aio import ContainerRegistryClient

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
    
    async def upload_oci_manifest_prerequisites(self, repo, client):
        layer = "654b93f61054e4ce90ed203bb8d556a6200d5f906cf3eca0620738d6dc18cbed"
        config = "config.json"
        base_path = os.path.join(self.get_test_directory(), "data", "oci_artifact")
        # upload config
        await client.upload_blob(repo, open(os.path.join(base_path, config), "rb"))
        # upload layers
        await client.upload_blob(repo, open(os.path.join(base_path, layer), "rb"))

    async def upload_docker_manifest_prerequisites(self, repo, client):
        layer = "2db29710123e3e53a794f2694094b9b4338aa9ee5c40b930cb8063a1be392c54"
        config = "config.json"
        base_path = os.path.join(self.get_test_directory(), "data", "docker_artifact")
        # upload config
        await client.upload_blob(repo, open(os.path.join(base_path, config), "rb"))
        # upload layers
        await client.upload_blob(repo, open(os.path.join(base_path, layer), "rb"))

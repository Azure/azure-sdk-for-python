# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.containerregistry.aio import (
    # ContainerRepository,
    ContainerRegistryClient,
)

from azure.core.credentials import AccessToken
from azure.identity.aio import DefaultAzureCredential

from testcase import ContainerRegistryTestClass


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

    def get_credential(self):
        if self.is_live:
            return DefaultAzureCredential()
        return AsyncFakeTokenCredential()

    def create_registry_client(self, endpoint, **kwargs):
        return ContainerRegistryClient(
            endpoint=endpoint,
            credential=self.get_credential(),
            **kwargs,
        )

    def create_container_repository(self, endpoint, name, **kwargs):
        return ContainerRepository(
            endpoint=endpoint,
            name=name,
            credential=self.get_credential(),
            **kwargs,
        )

    def create_anon_client(self, endpoint, **kwargs):
        return ContainerRegistryClient(endpoint=endpoint, credential=None, **kwargs)

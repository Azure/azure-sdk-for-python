# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os

from azure.containerregistry.aio import ContainerRegistryClient
from azure.containerregistry._helpers import _get_authority,_get_audience, _get_credential

from azure.core.credentials import AccessToken

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
    def get_credential(self, authority=None, **kwargs):
        if self.is_live:
            _get_credential(is_async=True)
        return AsyncFakeTokenCredential()

    def create_registry_client(self, endpoint, **kwargs):
        authority = _get_authority(endpoint)
        audience = kwargs.pop("audience", None)
        if not audience:
            audience = _get_audience(authority)
        credential = self.get_credential(authority=authority)
        return ContainerRegistryClient(endpoint=endpoint, credential=credential, audience=audience, **kwargs)

    def create_anon_client(self, endpoint, **kwargs):
        authority = _get_authority(endpoint)
        audience = _get_audience(authority)
        return ContainerRegistryClient(endpoint=endpoint, credential=None, audience=audience, **kwargs)

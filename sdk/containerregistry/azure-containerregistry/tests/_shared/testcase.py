# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.containerregistry import (
    ContainerRepositoryClient,
    ContainerRegistryClient,
    ContainerRegistryUserCredential,
)

class ContainerRegistryTestClass(object):
    def create_registry_client(self, endpoint):
        return ContainerRegistryClient(
            endpoint=endpoint,
            credential=ContainerRegistryUserCredential(
                username=os.environ["CONTAINERREGISTRY_USERNAME"],
                password=os.environ["CONTAINERREGISTRY_PASSWORD"],
            ),
        )

    def create_repository_client(self, endpoint, name):
        return ContainerRepositoryClient(
            endpoint=endpoint,
            repository=name,
            credential=ContainerRegistryUserCredential(
                username=os.environ["CONTAINERREGISTRY_USERNAME"],
                password=os.environ["CONTAINERREGISTRY_PASSWORD"],
            ),
        )

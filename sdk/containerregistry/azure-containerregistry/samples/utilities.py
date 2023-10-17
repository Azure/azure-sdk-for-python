# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: utilities.py

DESCRIPTION:
    This file include some utility functions for samples to use:
    - load_registry(): to create repository "library/hello-world" and import images with different tags.
    - get_authority(): get authority of the ContainerRegistryClient
    - get_audience(): get audience of the ContainerRegistryClient
    - get_credential(): get credential of the ContainerRegistryClient
    It is not a file expected to run independently.
"""
import json
import os
from io import BytesIO
from azure.containerregistry import ContainerRegistryClient
from azure.identity import AzureAuthorityHosts, ClientSecretCredential
from azure.identity.aio import ClientSecretCredential as AsyncClientSecretCredential


def load_registry(endpoint):
    print("loading registry...")
    repo = "library/hello-world"
    tags = ["latest", "v1", "v2", "v3"]
    try:
        _import_images(endpoint, repo, tags)
    except Exception as e:
        raise


def _import_images(endpoint, repository, tags):
    authority = get_authority(endpoint)
    credential = ClientSecretCredential(
        tenant_id=os.environ["CONTAINERREGISTRY_TENANT_ID"],
        client_id=os.environ["CONTAINERREGISTRY_CLIENT_ID"],
        client_secret=os.environ["CONTAINERREGISTRY_CLIENT_SECRET"],
        authority=authority,
    )
    with ContainerRegistryClient(endpoint, credential) as client:
        # Upload a layer
        layer = BytesIO(b"Sample layer")
        layer_digest, layer_size = client.upload_blob(repository, layer)
        # Upload a config
        config = BytesIO(json.dumps({"sample config": "content"}).encode())
        config_digest, config_size = client.upload_blob(repository, config)
        docker_manifest = {
            "config": {
                "digest": config_digest,
                "mediaType": "application/vnd.docker.container.image.v1+json",
                "size": config_size,
            },
            "layers": [
                {
                    "digest": layer_digest,
                    "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
                    "size": layer_size,
                }
            ],
            "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
            "schemaVersion": 2,
        }
        for tag in tags:
            client.set_manifest(
                repository, docker_manifest, tag=tag, media_type="application/vnd.docker.distribution.manifest.v2+json"
            )


def get_authority(endpoint):
    if ".azurecr.io" in endpoint:
        return AzureAuthorityHosts.AZURE_PUBLIC_CLOUD
    if ".azurecr.cn" in endpoint:
        return AzureAuthorityHosts.AZURE_CHINA
    if ".azurecr.us" in endpoint:
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
    is_async = kwargs.pop("is_async", False)
    if is_async:
        return AsyncClientSecretCredential(
            tenant_id=os.environ["CONTAINERREGISTRY_TENANT_ID"],
            client_id=os.environ["CONTAINERREGISTRY_CLIENT_ID"],
            client_secret=os.environ["CONTAINERREGISTRY_CLIENT_SECRET"],
            authority=authority,
        )
    return ClientSecretCredential(
        tenant_id=os.environ["CONTAINERREGISTRY_TENANT_ID"],
        client_id=os.environ["CONTAINERREGISTRY_CLIENT_ID"],
        client_secret=os.environ["CONTAINERREGISTRY_CLIENT_SECRET"],
        authority=authority,
    )

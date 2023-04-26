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
    - load_registry(): to create some repositories and import images with different tags in each repository.
    - get_authority(): get authority of the ContainerRegistryClient
    - get_audience(): get audience of the ContainerRegistryClient
    - get_credential(): get credential of the ContainerRegistryClient
    It is not a file expected to run independently.
"""
import os
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt.containerregistry.models import ImportImageParameters, ImportSource, ImportMode
from azure.identity import AzureAuthorityHosts, ClientSecretCredential
from azure.identity.aio import ClientSecretCredential as AsyncClientSecretCredential

def load_registry():
    authority = get_authority(os.environ.get("CONTAINERREGISTRY_ENDPOINT"))
    repos = [
        "library/hello-world",
        "library/alpine",
        "library/busybox",
    ]
    tags = [
        [
            "library/hello-world:latest",
            "library/hello-world:v1",
            "library/hello-world:v2",
            "library/hello-world:v3",
            "library/hello-world:v4",
        ],
        ["library/alpine"],
        ["library/busybox"],
    ]
    for repo, tag in zip(repos, tags):
        try:
            _import_image(authority, repo, tag)
        except Exception as e:
            print(e)

def _import_image(authority, repository, tags):
    credential = ClientSecretCredential(
        tenant_id=os.environ.get("CONTAINERREGISTRY_TENANT_ID"),
        client_id=os.environ.get("CONTAINERREGISTRY_CLIENT_ID"),
        client_secret=os.environ.get("CONTAINERREGISTRY_CLIENT_SECRET"),
        authority=authority
    )
    sub_id = os.environ.get("CONTAINERREGISTRY_SUBSCRIPTION_ID")
    audience = get_audience(authority)
    scope = [audience + "/.default"]
    mgmt_client = ContainerRegistryManagementClient(
        credential,
        sub_id,
        api_version="2019-05-01",
        base_url=audience,
        credential_scopes=scope
    )
    registry_uri = "registry.hub.docker.com"
    rg_name = os.environ.get("CONTAINERREGISTRY_RESOURCE_GROUP")
    registry_name = os.environ.get("CONTAINERREGISTRY_REGISTRY_NAME")

    import_source = ImportSource(source_image=repository, registry_uri=registry_uri)

    import_params = ImportImageParameters(mode=ImportMode.Force, source=import_source, target_tags=tags)

    result = mgmt_client.registries.begin_import_image(
        rg_name,
        registry_name,
        parameters=import_params,
    )
    
    result.wait()

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
            tenant_id=os.environ.get("CONTAINERREGISTRY_TENANT_ID"),
            client_id=os.environ.get("CONTAINERREGISTRY_CLIENT_ID"),
            client_secret=os.environ.get("CONTAINERREGISTRY_CLIENT_SECRET"),
            authority=authority
        )
    return ClientSecretCredential(
        tenant_id=os.environ.get("CONTAINERREGISTRY_TENANT_ID"),
        client_id=os.environ.get("CONTAINERREGISTRY_CLIENT_ID"),
        client_secret=os.environ.get("CONTAINERREGISTRY_CLIENT_SECRET"),
        authority=authority
    )

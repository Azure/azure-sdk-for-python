# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from azure.containerregistry._helpers import _get_authority, _get_audience
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt.containerregistry.models import ImportImageParameters, ImportSource, ImportMode
from azure.identity import ClientSecretCredential

def load_registry():
    authority = _get_authority(os.environ.get("CONTAINERREGISTRY_ENDPOINT"))
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
            import_image(authority, repo, tag)
        except Exception as e:
            print(e)

def import_image(authority, repository, tags):
    credential = ClientSecretCredential(
        tenant_id=os.environ["CONTAINERREGISTRY_TENANT_ID"],
        client_id=os.environ["CONTAINERREGISTRY_CLIENT_ID"],
        client_secret=os.environ["CONTAINERREGISTRY_CLIENT_SECRET"],
        authority=authority
    )
    sub_id = os.environ["CONTAINERREGISTRY_SUBSCRIPTION_ID"]
    audience = _get_audience(authority)
    scope = [audience + "/.default"]
    mgmt_client = ContainerRegistryManagementClient(
        credential, sub_id, api_version="2019-05-01", base_url=audience, credential_scopes=scope
    )
    registry_uri = "registry.hub.docker.com"
    rg_name = os.environ["CONTAINERREGISTRY_RESOURCE_GROUP"]
    registry_name = os.environ["CONTAINERREGISTRY_REGISTRY_NAME"]

    import_source = ImportSource(source_image=repository, registry_uri=registry_uri)

    import_params = ImportImageParameters(mode=ImportMode.Force, source=import_source, target_tags=tags)

    result = mgmt_client.registries.begin_import_image(
        rg_name,
        registry_name,
        parameters=import_params,
    )

    while not result.done():
        pass

# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os
import pytest

from azure.containerregistry import ContainerRegistryClient
from azure.containerregistry._helpers import _is_tag

from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt.containerregistry.models import ImportImageParameters, ImportSource, ImportMode
from azure.identity import DefaultAzureCredential, AzureAuthorityHosts, ClientSecretCredential

from devtools_testutils import AzureRecordedTestCase, is_live, FakeTokenCredential

logger = logging.getLogger()


class ContainerRegistryTestClass(AzureRecordedTestCase):
    def import_image(self, endpoint, repository, tags, is_anonymous=False):
        # repository must be a docker hub repository
        # tags is a List of repository/tag combos in the format <repository>:<tag>
        if not self.is_live:
            return
        authority = get_authority(endpoint)
        import_image(authority, repository, tags, is_anonymous=is_anonymous)

    def get_credential(self, authority=None, **kwargs):
        if self.is_live:
            if authority != AzureAuthorityHosts.AZURE_PUBLIC_CLOUD:
                return ClientSecretCredential(
                    tenant_id=os.environ.get("CONTAINERREGISTRY_TENANT_ID"),
                    client_id=os.environ.get("CONTAINERREGISTRY_CLIENT_ID"),
                    client_secret=os.environ.get("CONTAINERREGISTRY_CLIENT_SECRET"),
                    authority=authority
                )
            return DefaultAzureCredential(**kwargs)
        return FakeTokenCredential()

    def create_registry_client(self, endpoint, **kwargs):
        authority = get_authority(endpoint)
        audience = kwargs.pop("audience", None)
        if not audience:
            audience = get_audience(authority)
        credential = self.get_credential(authority=authority)
        logger.warning(f"Authority: {authority} \nAuthorization scope: {audience}")
        return ContainerRegistryClient(endpoint=endpoint, credential=credential, audience=audience, **kwargs)

    def create_anon_client(self, endpoint, **kwargs):
        authority = get_authority(endpoint)
        audience = get_audience(authority)
        return ContainerRegistryClient(endpoint=endpoint, audience=audience, **kwargs)

    def set_all_properties(self, properties, value):
        properties.can_delete = value
        properties.can_read = value
        properties.can_write = value
        properties.can_list = value
        return properties

    def assert_all_properties(self, properties, value):
        assert properties.can_delete == value
        assert properties.can_read == value
        assert properties.can_write == value
        assert properties.can_list == value

    def create_fully_qualified_reference(self, registry, repository, digest):
        return f"{registry}/{repository}{':' if _is_tag(digest) else '@'}{digest.split(':')[-1]}"

    def is_public_endpoint(self, endpoint):
        return ".azurecr.io" in endpoint
    
    def upload_oci_manifest_prerequisites(self, repo, client):
        layer = "654b93f61054e4ce90ed203bb8d556a6200d5f906cf3eca0620738d6dc18cbed"
        config = "config.json"
        base_path = os.path.join(self.get_test_directory(), "data", "oci_artifact")
        # upload config
        client.upload_blob(repo, open(os.path.join(base_path, config), "rb"))
        # upload layers
        client.upload_blob(repo, open(os.path.join(base_path, layer), "rb"))
    
    def upload_docker_manifest_prerequisites(self, repo, client):
        layer = "2db29710123e3e53a794f2694094b9b4338aa9ee5c40b930cb8063a1be392c54"
        config = "config.json"
        base_path = os.path.join(self.get_test_directory(), "data", "docker_artifact")
        # upload config
        client.upload_blob(repo, open(os.path.join(base_path, config), "rb"))
        # upload layers
        client.upload_blob(repo, open(os.path.join(base_path, layer), "rb"))

    def get_test_directory(self):
        return os.path.join(os.getcwd(), "tests")


def get_authority(endpoint: str) -> str:
    if ".azurecr.io" in endpoint:
        logger.warning("Public cloud Authority")
        return AzureAuthorityHosts.AZURE_PUBLIC_CLOUD
    if ".azurecr.cn" in endpoint:
        logger.warning("China Authority")
        return AzureAuthorityHosts.AZURE_CHINA
    if ".azurecr.us" in endpoint:
        logger.warning("US Gov Authority")
        return AzureAuthorityHosts.AZURE_GOVERNMENT
    raise ValueError(f"Endpoint ({endpoint}) could not be understood")

def get_audience(authority: str) -> str:
    if authority == AzureAuthorityHosts.AZURE_PUBLIC_CLOUD:
        logger.warning("Public cloud auth audience")
        return "https://management.azure.com"
    if authority == AzureAuthorityHosts.AZURE_CHINA:
        logger.warning("China cloud auth audience")
        return "https://management.chinacloudapi.cn"
    if authority == AzureAuthorityHosts.AZURE_GOVERNMENT:
        logger.warning("US Gov cloud auth audience")
        return "https://management.usgovcloudapi.net"

def import_image(authority, repository, tags, is_anonymous=False):
    logger.warning(f"Import image authority: {authority}")
    if is_anonymous:
        registry_name = os.environ.get("CONTAINERREGISTRY_ANONREGISTRY_NAME")
    else:
        registry_name = os.environ.get("CONTAINERREGISTRY_REGISTRY_NAME")
    sub_id = os.environ.get("CONTAINERREGISTRY_SUBSCRIPTION_ID")
    tenant_id=os.environ.get("CONTAINERREGISTRY_TENANT_ID")
    client_id=os.environ.get("CONTAINERREGISTRY_CLIENT_ID")
    client_secret=os.environ.get("CONTAINERREGISTRY_CLIENT_SECRET")
    credential = ClientSecretCredential(
        tenant_id=tenant_id, client_id=client_id, client_secret=client_secret, authority=authority
    )
    audience = get_audience(authority)
    scope = [audience + "/.default"]
    mgmt_client = ContainerRegistryManagementClient(
        credential, sub_id, api_version="2019-05-01", base_url=audience, credential_scopes=scope
    )
    logger.warning(f"LOGGING: {sub_id}{tenant_id}")
    registry_uri = "registry.hub.docker.com"
    rg_name = os.environ.get("CONTAINERREGISTRY_RESOURCE_GROUP")

    import_source = ImportSource(source_image=repository, registry_uri=registry_uri)

    import_params = ImportImageParameters(mode=ImportMode.Force, source=import_source, target_tags=tags)

    result = mgmt_client.registries.begin_import_image(
        rg_name,
        registry_name,
        parameters=import_params,
    )

    result.wait()

@pytest.fixture(scope="session")
def load_registry():
    if not is_live():
        return
    authority = get_authority(os.environ.get("CONTAINERREGISTRY_ENDPOINT"))
    authority_anon = get_authority(os.environ.get("CONTAINERREGISTRY_ANONREGISTRY_ENDPOINT"))
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
            import_image(authority_anon, repo, tag, is_anonymous=True)
        except Exception as e:
            print(e)

# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os
import json
from io import BytesIO

from azure.containerregistry import ContainerRegistryClient
from azure.containerregistry._helpers import _is_tag
from azure.identity import AzureAuthorityHosts, ClientSecretCredential

from devtools_testutils import AzureRecordedTestCase, FakeTokenCredential, get_credential

logger = logging.getLogger()


class ContainerRegistryTestClass(AzureRecordedTestCase):
    def import_image(self, endpoint, repository, tags):
        # repository must be a docker hub repository
        # tags is a List of repository/tag combos in the format <repository>:<tag>
        if not self.is_live:
            return
        import_image(endpoint, repository, tags)

    def get_credential(self, authority=None, **kwargs):
        if self.is_live:
            return get_credential(authority=authority, **kwargs)
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


def is_public_endpoint(endpoint):
    return ".azurecr.io" in endpoint


def is_china_endpoint(endpoint):
    return ".azurecr.cn" in endpoint


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


def import_image(endpoint, repository, tags):
    authority = get_authority(endpoint)
    logger.warning(f"Import image authority: {authority}")
    credential = get_credential(authority=authority)

    with ContainerRegistryClient(endpoint, credential) as client:
        # Upload a layer
        layer = BytesIO(b"Sample layer")
        layer_digest, layer_size = client.upload_blob(repository, layer)
        logger.info(f"Uploaded layer: digest - {layer_digest}, size - {layer_size}")
        # Upload a config
        config = BytesIO(json.dumps({"sample config": "content"}).encode())
        config_digest, config_size = client.upload_blob(repository, config)
        logger.info(f"Uploaded config: digest - {config_digest}, size - {config_size}")
        # Upload images
        oci_manifest = {
            "config": {
                "mediaType": "application/vnd.oci.image.config.v1+json",
                "digest": config_digest,
                "sizeInBytes": config_size,
            },
            "schemaVersion": 2,
            "layers": [
                {
                    "mediaType": "application/vnd.oci.image.layer.v1.tar",
                    "digest": layer_digest,
                    "size": layer_size,
                    "annotations": {
                        "org.opencontainers.image.ref.name": "artifact.txt",
                    },
                },
            ],
        }
        for tag in tags:
            manifest_digest = client.set_manifest(repository, oci_manifest, tag=tag)
            logger.info(f"Uploaded manifest: digest - {manifest_digest}")

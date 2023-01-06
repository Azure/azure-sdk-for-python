# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os
import pytest

from azure.containerregistry import ContainerRegistryClient
from azure.containerregistry._helpers import _is_tag, _import_image, _get_audience, _get_authority, _get_credential
from azure.containerregistry._generated.models import Annotations, Descriptor, OCIManifest

from devtools_testutils import AzureRecordedTestCase, is_live, FakeTokenCredential, is_live_and_not_recording

REDACTED = "REDACTED"
logger = logging.getLogger()


class ContainerRegistryTestClass(AzureRecordedTestCase):
    def __init__(self) -> None:
        super().__init__()
        # Sleep to avoid resource deployment delay in live pipelines.
        if is_live_and_not_recording:
            self.sleep(10)
    
    def import_image(self, endpoint, repository, tags):
        # repository must be a docker hub repository
        # tags is a List of repository/tag combos in the format <repository>:<tag>
        if not self.is_live:
            return
        authority = _get_authority(endpoint)
        _import_image(authority, repository, tags)

    def get_credential(self, authority=None, **kwargs):
        if self.is_live:
            return _get_credential(authority, **kwargs)
        return FakeTokenCredential()

    def create_registry_client(self, endpoint, **kwargs):
        authority = _get_authority(endpoint)
        audience = kwargs.pop("audience", None)
        if not audience:
            audience = _get_audience(authority)
        credential = self.get_credential(authority=authority)
        logger.warning("Authority: {} \nAuthorization scope: {}".format(authority, audience))
        return ContainerRegistryClient(endpoint=endpoint, credential=credential, audience=audience, **kwargs)

    def create_anon_client(self, endpoint, **kwargs):
        authority = _get_authority(endpoint)
        audience = _get_audience(authority)
        return ContainerRegistryClient(endpoint=endpoint, credential=None, audience=audience, **kwargs)

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

    def assert_manifest(self, manifest, expected):
        assert manifest is not None
        assert manifest.schema_version == expected.schema_version
        assert manifest.config is not None
        assert_manifest_config_or_layer_properties(manifest.config, expected.config)
        assert manifest.layers is not None
        assert len(manifest.layers) == len(expected.layers)
        count = 0
        for layer in manifest.layers:
            assert_manifest_config_or_layer_properties(layer, expected.layers[count])
            count += 1

    def create_fully_qualified_reference(self, registry, repository, digest):
        return "{}/{}{}{}".format(
            registry,
            repository,
            ":" if _is_tag(digest) else "@",
            digest.split(":")[-1]
        )

    def is_public_endpoint(self, endpoint):
        return ".azurecr.io" in endpoint
    
    def create_oci_manifest(self):
        config1 = Descriptor(
            media_type="application/vnd.acme.rocket.config",
            digest="sha256:d25b42d3dbad5361ed2d909624d899e7254a822c9a632b582ebd3a44f9b0dbc8",
            size=171
        )
        config2 = Descriptor(
            media_type="application/vnd.oci.image.layer.v1.tar",
            digest="sha256:654b93f61054e4ce90ed203bb8d556a6200d5f906cf3eca0620738d6dc18cbed",
            size=28,
            annotations=Annotations(name="artifact.txt")
        )
        return OCIManifest(config=config1, schema_version=2, layers=[config2])
    
    def upload_manifest_prerequisites(self, repo, client):
        layer = "654b93f61054e4ce90ed203bb8d556a6200d5f906cf3eca0620738d6dc18cbed"
        config = "config.json"
        base_path = os.path.join(self.get_test_directory(), "data", "oci_artifact")
        # upload config
        client.upload_blob(repo, open(os.path.join(base_path, config), "rb"))
        # upload layers
        client.upload_blob(repo, open(os.path.join(base_path, layer), "rb"))

    def get_test_directory(self):
        return os.path.join(os.getcwd(), "tests")

@pytest.fixture(scope="session")
def load_registry():
    if not is_live():
        return
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
            _import_image(authority, repo, tag)
        except Exception as e:
            print(e)

def assert_manifest_config_or_layer_properties(value, expected):
    assert value.media_type == expected.media_type
    assert value.digest == expected.digest
    assert value.size == expected.size

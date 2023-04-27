# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_set_get_image.py

DESCRIPTION:
    This sample demonstrates setting and getting OCI and non-OCI images to a repository.

USAGE:
    python sample_set_get_image.py

    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account

    This sample assumes your registry has a repository "library/hello-world", run load_registry() if you don't have.
    Set the environment variables with your own values before running load_registry():
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account
    2) CONTAINERREGISTRY_TENANT_ID - The service principal's tenant ID
    3) CONTAINERREGISTRY_CLIENT_ID - The service principal's client ID
    4) CONTAINERREGISTRY_CLIENT_SECRET - The service principal's client secret
    5) CONTAINERREGISTRY_RESOURCE_GROUP - The resource group name
    6) CONTAINERREGISTRY_REGISTRY_NAME - The registry name
"""
import os
import json
from io import BytesIO
from dotenv import find_dotenv, load_dotenv
from azure.containerregistry import ContainerRegistryClient, ArtifactArchitecture, ArtifactOperatingSystem
from utilities import load_registry, get_authority, get_audience, get_credential


class SetGetImage(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.environ.get("CONTAINERREGISTRY_ENDPOINT")
        self.authority = get_authority(self.endpoint)
        self.audience = get_audience(self.authority)
        self.credential = get_credential(self.authority)

    def set_get_oci_image(self):
        repository_name = "sample-oci-image"
        layer = BytesIO(b"Sample layer")
        config = BytesIO(json.dumps(
            {
                "sample config": "content",
            }).encode())
        with ContainerRegistryClient(self.endpoint, self.credential, audience=self.audience) as client:
            # Upload a layer
            layer_digest, layer_size = client.upload_blob(repository_name, layer)
            # Upload a config
            config_digest, config_size = client.upload_blob(repository_name, config)
            # Create an oci image with config and layer info
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
            # Set the image
            manifest_digest = client.set_manifest(repository_name, oci_manifest)

            # Get the image
            get_manifest_result = client.get_manifest(repository_name, manifest_digest)
            received_manifest = get_manifest_result.manifest
            print(received_manifest)
            # Download and write out the layers
            for layer in received_manifest["layers"]:
                # Remove the "sha256:" prefix from digest
                layer_file_name = layer["digest"].split(":")[1]
                try:
                    stream = client.download_blob(repository_name, layer["digest"])
                    with open(layer_file_name, "wb") as layer_file:
                        for chunk in stream:
                            layer_file.write(chunk)
                except ValueError:
                    print(f"Downloaded layer digest value did not match. Deleting file {layer_file_name}.")
                    os.remove(layer_file_name)
            # Download and write out the config
            config_file_name = "config.json"
            try:
                stream = client.download_blob(repository_name, received_manifest["config"]["digest"])
                with open(config_file_name, "wb") as config_file:
                    for chunk in stream:
                        config_file.write(chunk)
            except ValueError:
                print(f"Downloaded config digest value did not match. Deleting file {config_file_name}.")
                os.remove(config_file_name)

            # Delete the layers
            for layer in received_manifest["layers"]:
                client.delete_blob(repository_name, layer["digest"])
            # Delete the config
            client.delete_blob(repository_name, received_manifest["config"]["digest"])
            # Delete the image
            client.delete_manifest(repository_name, manifest_digest)

    def set_get_docker_image(self):
        load_registry()
        repository_name = "library/hello-world"
        # create a Docker image object in Docker v2 Manifest List format
        manifest_list = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.docker.distribution.manifest.list.v2+json",
            "manifests": [
                {
                    "digest": "sha256:f54a58bc1aac5ea1a25d796ae155dc228b3f0e11d046ae276b39c4bf2f13d8c4",
                    "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
                    "platform": {
                        "architecture": ArtifactArchitecture.AMD64,
                        "os": ArtifactOperatingSystem.LINUX
                    }
                }
            ]
        }
        with ContainerRegistryClient(self.endpoint, self.credential, audience=self.audience) as client:
            # Set the image with one custom media type
            client.set_manifest(repository_name, manifest_list, tag="sample", media_type=manifest_list["mediaType"])

            # Get the image
            get_manifest_result = client.get_manifest(repository_name, "sample")
            received_manifest = get_manifest_result.manifest
            print(received_manifest)
            received_manifest_media_type = get_manifest_result.media_type
            print(received_manifest_media_type)


if __name__ == "__main__":
    sample = SetGetImage()
    sample.set_get_oci_image()
    sample.set_get_docker_image()

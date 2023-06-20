# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_set_get_image_async.py

DESCRIPTION:
    This sample demonstrates setting and getting OCI and non-OCI images to a repository.

USAGE:
    python sample_set_get_image_async.py

    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ANONREGISTRY_ENDPOINT - The URL of your Container Registry account for anonymous access

    This sample assumes your registry has a repository "library/hello-world", run load_registry() if you don't have.
    Set the environment variables with your own values before running load_registry():
    1) CONTAINERREGISTRY_ANONREGISTRY_ENDPOINT - The URL of your Container Registry account for anonymous access
    2) CONTAINERREGISTRY_TENANT_ID - The service principal's tenant ID
    3) CONTAINERREGISTRY_CLIENT_ID - The service principal's client ID
    4) CONTAINERREGISTRY_CLIENT_SECRET - The service principal's client secret
    5) CONTAINERREGISTRY_RESOURCE_GROUP - The resource group name
    6) CONTAINERREGISTRY_REGISTRY_NAME - The registry name
"""
import asyncio
import os
import json
from io import BytesIO
from dotenv import find_dotenv, load_dotenv
from azure.containerregistry import ArtifactArchitecture, ArtifactOperatingSystem, DigestValidationError
from azure.containerregistry.aio import ContainerRegistryClient
from utilities import load_registry, get_authority, get_credential


class SetGetImageAsync(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.environ.get("CONTAINERREGISTRY_ANONREGISTRY_ENDPOINT")
        self.authority = get_authority(self.endpoint)
        self.credential = get_credential(self.authority, is_async=True)

    async def set_get_oci_image(self):
        repository_name = "sample-oci-image-async"
        layer = BytesIO(b"Sample layer")
        config = BytesIO(json.dumps(
            {
                "sample config": "content",
            }).encode())
        async with ContainerRegistryClient(self.endpoint, self.credential) as client:
            # Upload a layer
            layer_digest, layer_size = await client.upload_blob(repository_name, layer)
            print(f"Uploaded layer: digest - {layer_digest}, size - {layer_size}")
            # Upload a config
            config_digest, config_size = await client.upload_blob(repository_name, config)
            print(f"Uploaded config: digest - {config_digest}, size - {config_size}")
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
            manifest_digest = await client.set_manifest(repository_name, oci_manifest, tag="latest")
            print(f"Uploaded manifest: digest - {manifest_digest}")
            # [END upload_blob_and_manifest]

            # [START download_blob_and_manifest]
            # Get the image
            get_manifest_result = await client.get_manifest(repository_name, "latest")
            received_manifest = get_manifest_result.manifest
            print(f"Got manifest:\n{received_manifest}")

            # Download and write out the layers
            for layer in received_manifest["layers"]:
                # Remove the "sha256:" prefix from digest
                layer_file_name = layer["digest"].split(":")[1]
                try:
                    stream = await client.download_blob(repository_name, layer["digest"])
                    with open(layer_file_name, "wb") as layer_file:
                        async for chunk in stream:
                            layer_file.write(chunk)
                except DigestValidationError:
                    print(f"Downloaded layer digest value did not match. Deleting file {layer_file_name}.")
                    os.remove(layer_file_name)
                print(f"Got layer: {layer_file_name}")
            # Download and write out the config
            config_file_name = "config.json"
            try:
                stream = await client.download_blob(repository_name, received_manifest["config"]["digest"])
                with open(config_file_name, "wb") as config_file:
                    async for chunk in stream:
                        config_file.write(chunk)
            except DigestValidationError:
                print(f"Downloaded config digest value did not match. Deleting file {config_file_name}.")
                os.remove(config_file_name)
            print(f"Got config: {config_file_name}")

            # Delete the layers
            for layer in received_manifest["layers"]:
                await client.delete_blob(repository_name, layer["digest"])
            # Delete the config
            await client.delete_blob(repository_name, received_manifest["config"]["digest"])
            
            # Delete the image
            await client.delete_manifest(repository_name, get_manifest_result.digest)

    async def set_get_docker_image(self):
        load_registry()
        repository_name = "library/hello-world"
        # create a Docker image object in Docker v2 Manifest List format
        manifest_list = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.docker.distribution.manifest.list.v2+json",
            "manifests": [
                {
                    "digest": "sha256:7e9b6e7ba2842c91cf49f3e214d04a7a496f8214356f41d81a6e6dcad11f11e3",
                    "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
                    "platform": {
                        "architecture": ArtifactArchitecture.AMD64,
                        "os": ArtifactOperatingSystem.LINUX
                    },
                    "size": 525
                }
            ]
        }
        async with ContainerRegistryClient(self.endpoint, self.credential) as client:
            # Set the image with one custom media type
            await client.set_manifest(repository_name, manifest_list, tag="sample", media_type=manifest_list["mediaType"])

            # Get the image
            get_manifest_result = await client.get_manifest(repository_name, "sample")
            received_manifest = get_manifest_result.manifest
            print(received_manifest)
            received_manifest_media_type = get_manifest_result.media_type
            print(received_manifest_media_type)


async def main():
    sample = SetGetImageAsync()
    await sample.set_get_oci_image()
    await sample.set_get_docker_image()


if __name__ == "__main__":
    asyncio.run(main())

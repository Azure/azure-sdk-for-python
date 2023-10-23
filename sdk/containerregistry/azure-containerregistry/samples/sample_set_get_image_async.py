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
"""
import asyncio
import os
import json
from io import BytesIO
from dotenv import find_dotenv, load_dotenv
from azure.containerregistry import DigestValidationError
from azure.containerregistry.aio import ContainerRegistryClient
from utilities import get_authority, get_credential


class SetGetImageAsync(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.environ["CONTAINERREGISTRY_ANONREGISTRY_ENDPOINT"]
        self.authority = get_authority(self.endpoint)
        self.credential = get_credential(self.authority, is_async=True)

    async def set_get_oci_image(self):
        repository_name = "sample-oci-image-async"
        sample_layer = BytesIO(b"Sample layer")
        config = BytesIO(
            json.dumps(
                {
                    "sample config": "content",
                }
            ).encode()
        )
        async with ContainerRegistryClient(self.endpoint, self.credential) as client:
            # Upload a layer
            layer_digest, layer_size = await client.upload_blob(repository_name, sample_layer)
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
        repository_name = "sample-docker-image"
        async with ContainerRegistryClient(self.endpoint, self.credential) as client:
            # Upload a layer
            sample_layer = BytesIO(b"Sample layer")
            layer_digest, layer_size = await client.upload_blob(repository_name, sample_layer)
            print(f"Uploaded layer: digest - {layer_digest}, size - {layer_size}")
            # Upload a config
            config = BytesIO(json.dumps({"sample config": "content"}).encode())
            config_digest, config_size = await client.upload_blob(repository_name, config)
            print(f"Uploaded config: digest - {config_digest}, size - {config_size}")
            # create a Docker image object in Docker v2 Manifest format
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
            # Set the image with one custom media type
            await client.set_manifest(
                repository_name, docker_manifest, tag="sample", media_type=str(docker_manifest["mediaType"])
            )

            # Get the image
            get_manifest_result = await client.get_manifest(repository_name, "sample")
            received_manifest = get_manifest_result.manifest
            print(received_manifest)
            received_manifest_media_type = get_manifest_result.media_type
            print(received_manifest_media_type)

            # Delete the image
            client.delete_manifest(repository_name, get_manifest_result.digest)


async def main():
    sample = SetGetImageAsync()
    await sample.set_get_oci_image()
    await sample.set_get_docker_image()


if __name__ == "__main__":
    asyncio.run(main())

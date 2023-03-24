# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_upload_download_manifest_async.py

DESCRIPTION:
    This sample demonstrates uploading and downloading an OCI and Docker manifest to a repository.

USAGE:
    python sample_upload_download_manifest_async.py

    This sample assumes your registry has a repository "library/hello-world",
    run load_registry() if you don't have.
    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account

    This sample assumes your registry has a repository "library/hello-world".
"""
import asyncio
import os
import json
from io import BytesIO
from dotenv import find_dotenv, load_dotenv
from azure.containerregistry import ArtifactArchitecture, ArtifactOperatingSystem, OciAnnotations, OciDescriptor, OciImageManifest
from azure.containerregistry.aio import ContainerRegistryClient
from utilities import load_registry, get_authority, get_audience, get_credential


class UploadDownloadManifest(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.environ.get("CONTAINERREGISTRY_ENDPOINT")
        self.authority = get_authority(self.endpoint)
        self.audience = get_audience(self.authority)
        self.credential = get_credential(self.authority)
        self.repository_name = "library/hello-world"
        load_registry()

    async def upload_download_oci_manifest(self):
        repository_name = "library/hello-world"
        layer = BytesIO(b"Sample layer")
        config = BytesIO(json.dumps(
            {
                "sample config": "content",
            }).encode())
        async with ContainerRegistryClient(self.endpoint, self.credential, audience=self.audience) as client:
            # Upload a layer
            layer_digest, layer_size = await client.upload_blob(repository_name, layer)
            # Upload a config
            config_digest, config_size = await client.upload_blob(repository_name, config)
            # Create a manifest with config and layer info
            manifest = OciImageManifest(
                config = OciDescriptor(
                    media_type="application/vnd.oci.image.config.v1+json",
                    digest=config_digest,
                    size=config_size
                ),
                schema_version=2,
                layers=[
                    OciDescriptor(
                        media_type="application/vnd.oci.image.layer.v1.tar",
                        digest=layer_digest,
                        size=layer_size,
                        annotations=OciAnnotations(name="artifact.txt")
                    )
                ]
            )
            # Upload the manifest
            digest = await client.upload_manifest(repository_name, manifest)

            # Download the manifest
            download_manifest_result = await client.download_manifest(repository_name, digest)
            downloaded_manifest = download_manifest_result.manifest
            download_manifest_stream = download_manifest_result.data
            print(b"".join(download_manifest_stream))
            # Download the layers
            async for layer in downloaded_manifest.layers:
                async with await client.download_blob(repository_name, layer.digest) as layer_stream:
                    print(b"".join(layer_stream))
            # Download the config
            async with await client.download_blob(repository_name, downloaded_manifest.config.digest) as config_stream:
                print(b"".join(config_stream))

            # Delete the layers
            async for layer in downloaded_manifest.layers:
                await client.delete_blob(repository_name, layer.digest)
            # Delete the config
            await client.delete_blob(repository_name, downloaded_manifest.config.digest)
            # Delete the manifest
            await client.delete_manifest(repository_name, download_manifest_result.digest)
    
    async def upload_download_docker_manifest(self):
        # create a Docker manifest object in Docker v2 Manifest List format
        manifest_list = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.docker.distribution.manifest.list.v2+json",
            "manifests": [
                {
                    "digest": "sha256:f54a58bc1aac5ea1a25d796ae155dc228b3f0e11d046ae276b39c4bf2f13d8c4",
                    "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
                    "platform": {
                        "architecture": ArtifactArchitecture.AMD64,
                        "os": ArtifactOperatingSystem.LINUX,
                    }
                }
            ]
        }
        manifest_bytes = json.dumps(manifest_list).encode()
        async with ContainerRegistryClient(self.endpoint, self.credential, audience=self.audience) as client:
            # Upload the manifest with one custom media type
            async client.upload_manifest(self.repository_name, BytesIO(manifest_bytes), tag="sample", media_type="application/vnd.docker.distribution.manifest.list.v2+json")
            
            # Download the manifest with one custom media types
            download_manifest_result = async client.download_manifest(self.repository_name, "sample", media_types="application/vnd.docker.distribution.manifest.list.v2+json")
            download_manifest_stream = download_manifest_result.data
            download_manifest_media_type = download_manifest_result.media_type
            print(b"".join(download_manifest_stream))
            print(download_manifest_media_type)

            # Download the manifest with multiple custom media types
            download_manifest_result = async client.download_manifest(self.repository_name, "sample", media_types=["application/vnd.docker.distribution.manifest.list.v2+json", "application/vnd.oci.image.index.v1+json"])
            download_manifest_stream = download_manifest_result.data
            download_manifest_media_type = download_manifest_result.media_type
            print(b"".join(download_manifest_stream))
            print(download_manifest_media_type)


async def main():
    sample = UploadDownloadManifest()
    await sample.upload_download_oci_manifest()
    await sample.upload_download_docker_manifest()


if __name__ == "__main__":
    asyncio.run(main())

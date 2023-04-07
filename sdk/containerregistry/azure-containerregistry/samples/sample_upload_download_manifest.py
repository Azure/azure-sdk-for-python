# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_upload_download_manifest.py

DESCRIPTION:
    This sample demonstrates uploading and downloading an OCI manifest to a repository.

USAGE:
    python sample_upload_download_manifest.py

    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account
"""
import os
import json
from io import BytesIO
from dotenv import find_dotenv, load_dotenv
from azure.containerregistry import ContainerRegistryClient
from azure.containerregistry._generated.models import Annotations, Descriptor, OCIManifest
from utilities import get_authority, get_audience, get_credential


class UploadDownloadManifest(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.environ.get("CONTAINERREGISTRY_ENDPOINT")
        self.authority = get_authority(self.endpoint)
        self.audience = get_audience(self.authority)
        self.credential = get_credential(self.authority)

    def upload_download_manifest(self):
        repository_name = "library/hello-world"
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
            # Create a manifest with config and layer info
            manifest = OCIManifest(
                config = Descriptor(
                    media_type="application/vnd.oci.image.config.v1+json",
                    digest=config_digest,
                    size=config_size
                ),
                schema_version=2,
                layers=[
                    Descriptor(
                        media_type="application/vnd.oci.image.layer.v1.tar",
                        digest=layer_digest,
                        size=layer_size,
                        annotations=Annotations(name="artifact.txt")
                    )
                ]
            )
            # Upload the manifest
            digest = client.upload_manifest(repository_name, manifest)

            # Download the manifest
            download_manifest_result = client.download_manifest(repository_name, digest)
            downloaded_manifest = download_manifest_result.manifest
            download_manifest_stream = download_manifest_result.data
            print(b"".join(download_manifest_stream))
            # Download and write out the layers
            for layer in downloaded_manifest.layers:
                # Remove the "sha256:" prefix from digest
                layer_file_name = layer.digest.split(":")[1]
                try:
                    with client.download_blob(repository_name, layer.digest) as stream:
                        with open(layer_file_name, "wb") as layer_file:
                            for chunk in stream:
                                layer_file.write(chunk)
                except ValueError:
                    print(f"Downloaded layer digest value did not match. Deleting file {layer_file_name}.")
                    os.remove(layer_file_name)
            # Download and write out the config
            config_file_name = "config.json"
            try:
                with client.download_blob(repository_name, downloaded_manifest.config.digest) as stream:
                    with open(config_file_name, "wb") as config_file:
                        for chunk in stream:
                            config_file.write(chunk)
            except ValueError:
                print(f"Downloaded config digest value did not match. Deleting file {config_file_name}.")
                os.remove(config_file_name)

            # Delete the layers
            for layer in downloaded_manifest.layers:
                client.delete_blob(repository_name, layer.digest)
            # Delete the config
            client.delete_blob(repository_name, downloaded_manifest.config.digest)
            # Delete the manifest
            client.delete_manifest(repository_name, download_manifest_result.digest)


if __name__ == "__main__":
    sample = UploadDownloadManifest()
    sample.upload_download_manifest()

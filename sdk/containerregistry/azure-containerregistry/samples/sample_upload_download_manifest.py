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

    This sample assumes your registry has a repository "library/hello-world",
    run load_registry() if you don't have.
    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account

    This sample assumes your registry has a repository "library/hello-world".
"""
import os
import json
from io import BytesIO
from dotenv import find_dotenv, load_dotenv
from azure.containerregistry import ContainerRegistryClient
from azure.containerregistry._generated.models import Annotations, Descriptor, OCIManifest
from utilities import load_registry, get_authority, get_audience, get_credential


class UploadDownloadManifest(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.environ.get("CONTAINERREGISTRY_ENDPOINT")
        self.authority = get_authority(self.endpoint)
        self.audience = get_audience(self.authority)
        self.credential = get_credential(self.authority)
        load_registry()

    def upload_download_manifest(self):
        repository_name = "library/hello-world"
        layer = BytesIO(b"Sample layer")
        config = BytesIO(json.dumps(
            {
                "sample config": "content",
            }).encode())
        with ContainerRegistryClient(self.endpoint, self.credential, audience=self.audience) as client:
            
            
            # Upload a layer
            layer_digest = client.upload_blob(repository_name, layer)
            # Upload a config
            config_digest = client.upload_blob(repository_name, config)
            # Create a manifest with config and layer info
            manifest = OCIManifest(
                config = Descriptor(
                    media_type="application/vnd.oci.image.config.v1+json",
                    digest=config_digest,
                    size=len(config.getbuffer())
                ),
                schema_version=2,
                layers=[
                    Descriptor(
                        media_type="application/vnd.oci.image.layer.v1.tar",
                        digest=layer_digest,
                        size=len(layer.getbuffer()),
                        annotations=Annotations(name="artifact.txt")
                    )
                ]
            )

            digest = client.upload_manifest(repository_name, manifest)
            download_result = client.download_manifest(repository_name, digest)
            print(download_result.data.read())        


if __name__ == "__main__":
    sample = UploadDownloadManifest()
    sample.upload_download_manifest()

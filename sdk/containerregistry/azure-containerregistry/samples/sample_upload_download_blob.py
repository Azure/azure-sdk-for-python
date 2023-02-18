# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_upload_download_blob.py

DESCRIPTION:
    This sample demonstrates uploading and downloading an OCI artifact blob to and from a repository.

USAGE:
    python sample_upload_download_blob.py

    This sample assumes your registry has a repository "library/hello-world",
    run load_registry() if you don't have.
    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account

    This sample assumes your registry has a repository "library/hello-world".
"""
import os
from io import BytesIO
from dotenv import find_dotenv, load_dotenv
from azure.containerregistry import ContainerRegistryClient
from utilities import load_registry, get_authority, get_audience, get_credential


class UploadDownloadBlob(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.environ.get("CONTAINERREGISTRY_ENDPOINT")
        self.authority = get_authority(self.endpoint)
        self.audience = get_audience(self.authority)
        self.credential = get_credential(self.authority)

    def upload_download_blob(self):
        load_registry()
        repository_name = "library/hello-world"
        blob_content = BytesIO(b"Hello world!")
        with ContainerRegistryClient(self.endpoint, self.credential, audience=self.audience) as client:
            digest = client.upload_blob(repository_name, blob_content)
            download_result = client.download_blob(repository_name, digest)
            print(download_result.data.read())


if __name__ == "__main__":
    sample = UploadDownloadBlob()
    sample.upload_download_blob()

# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to register a local
    model with a Microsoft Foundry project WITHOUT relying on the
    `models_create` helper or the `azcopy` CLI. It hand-rolls the spec's
    three-step upload-first sequence using only the generated `.beta.models`
    operations and `azure-storage-blob`:

      1) `pending_upload(...)` -- the service provisions a project-managed
         blob container and returns a SAS URI.
      2) Upload the local weight files directly to that SAS container using
         `azure.storage.blob.ContainerClient`.
      3) `create_async(...)` -- commit the registration. The service returns
         202 Accepted and finalizes the ModelVersion asynchronously, so we
         poll `get(...)` until the new version is observable.

    This is useful when `azcopy` is not available, or when callers want to
    integrate the upload step with their own progress reporting / retry logic.

USAGE:
    python sample_models_pending_upload.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity azure-storage-blob python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as
       found in the overview page of your Microsoft Foundry project.
    2) MODEL_NAME - Optional. The name of the model to register. Defaults to
       "sample-model-pending-upload".
    3) MODEL_VERSION - Optional. The version of the model to register.
       Defaults to "1".
    4) DATA_FOLDER - Optional. The folder containing the local weight files
       to upload. Defaults to a temp folder created with two tiny dummy files.
"""

import os
import pathlib
import tempfile
import time

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import ContainerClient

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    FoundryModelWeightType,
    ModelPendingUploadRequest,
    ModelVersion,
    PendingUploadType,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ.get("MODEL_NAME", "sample-model-pending-upload")
model_version = os.environ.get("MODEL_VERSION", "1")

# Construct the path to the local folder of weight files used in this sample.
data_folder = os.environ.get("DATA_FOLDER")
if not data_folder:
    data_folder = tempfile.mkdtemp(prefix="sample-model-")
    (pathlib.Path(data_folder) / "weights.bin").write_bytes(b"hello-foundry-model")
    (pathlib.Path(data_folder) / "config.json").write_text('{"sample": true}')
source_dir = pathlib.Path(data_folder)

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    print(f"Step 1/3: pending_upload(name=`{model_name}`, version=`{model_version}`)")
    pending = project_client.beta.models.pending_upload(
        name=model_name,
        version=model_version,
        body=ModelPendingUploadRequest(
            pending_upload_type=PendingUploadType.TEMPORARY_BLOB_REFERENCE,
        ),
    )
    # The wire payload uses the datastore-style `blobReferenceForConsumption`
    # shape on some Foundry deployments and the SDK-modeled `blobReference`
    # shape on others. Tolerate both.
    payload = pending.as_dict()
    blob_ref = payload.get("blobReferenceForConsumption") or payload.get("blobReference") or {}
    sas_uri = (blob_ref.get("credential") or {}).get("sasUri")
    container_blob_uri = blob_ref.get("blobUri")
    if not sas_uri or not container_blob_uri:
        raise RuntimeError(f"pending_upload response missing SAS / blob URI: {payload!r}")
    print(f"  blob_uri = {container_blob_uri}")
    print(f"  sas_uri  = {sas_uri.split('?', 1)[0]}?<sas-redacted>")

    print(f"Step 2/3: upload contents of `{source_dir}` to the SAS container")
    container_client = ContainerClient.from_container_url(sas_uri)
    files = [p for p in source_dir.rglob("*") if p.is_file()]
    for f in files:
        rel = f.relative_to(source_dir).as_posix()
        with f.open("rb") as fp:
            container_client.upload_blob(name=rel, data=fp, overwrite=True)
        print(f"  uploaded {rel} ({f.stat().st_size} bytes)")

    print(f"Step 3/3: create_async(name=`{model_name}`, version=`{model_version}`)")
    project_client.beta.models.create_async(
        name=model_name,
        version=model_version,
        body=ModelVersion(
            blob_uri=container_blob_uri,
            weight_type=FoundryModelWeightType.FULL_WEIGHT,
            description="Sample model registered from sample_models_pending_upload.py",
            tags={"source": "sample_models_pending_upload.py"},
        ),
    )

    # `create_async` returns 202 Accepted; poll `get` until the committed
    # ModelVersion is observable.
    print(f"Polling get(`{model_name}`, `{model_version}`) until the ModelVersion is committed...")
    deadline = time.monotonic() + 300.0
    model = None
    while True:
        try:
            model = project_client.beta.models.get(name=model_name, version=model_version)
            break
        except ResourceNotFoundError:
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    f"Model `{model_name}`@`{model_version}` did not appear within 300s after create_async."
                )
            time.sleep(2.0)
    print(model)

    print(f"Delete the model version created above (`{model_name}`@`{model_version}`):")
    project_client.beta.models.delete(name=model_name, version=model_version)

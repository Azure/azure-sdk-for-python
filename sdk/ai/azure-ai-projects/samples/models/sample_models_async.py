# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an asynchronous AIProjectClient, this sample demonstrates how to
    register a local model with a Microsoft Foundry project and exercise the
    asynchronous `.beta.models` operations: `pending_upload`, `create_async`,
    `get`, `list_versions`, `list`, `get_credentials`, `update`, and `delete`.

    The async client does not expose the `models_create` convenience helper
    (which shells out to the synchronous `azcopy` CLI). This sample instead
    drives the spec's three-step upload-first sequence directly:

      1) `pending_upload(...)` -- the service provisions a project-managed
         blob container and returns a SAS URI.
      2) Upload the local weight files to that SAS container using
         `azure.storage.blob.aio.ContainerClient`.
      3) `create_async(...)` -- commit the registration. The service returns
         202 Accepted and finalizes the ModelVersion asynchronously, so we
         poll `get(...)` until the new version is observable.

USAGE:
    python sample_models_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity azure-storage-blob aiohttp python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as
       found in the overview page of your Microsoft Foundry project.
    2) MODEL_NAME - Optional. The name of the model to register. Defaults to
       "sample-model-async".
    3) MODEL_VERSION - Optional. The version of the model to register.
       Defaults to "1".
    4) DATA_FOLDER - Optional. The folder containing the local weight files
       to upload. Defaults to a temp folder created with two tiny dummy files.
"""

import asyncio
import os
import pathlib
import tempfile
import time

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import ContainerClient

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    FoundryModelWeightType,
    ModelCredentialRequest,
    ModelPendingUploadRequest,
    ModelVersion,
    PendingUploadType,
    UpdateModelVersionRequest,
)

load_dotenv()


async def main() -> None:

    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model_name = os.environ.get("MODEL_NAME", "sample-model-async")
    model_version = os.environ.get("MODEL_VERSION", "1")

    # Construct the path to the local folder of weight files used in this sample.
    data_folder = os.environ.get("DATA_FOLDER")
    if not data_folder:
        data_folder = tempfile.mkdtemp(prefix="sample-model-async-")
        (pathlib.Path(data_folder) / "weights.bin").write_bytes(b"hello-foundry-model")
        (pathlib.Path(data_folder) / "config.json").write_text('{"sample": true}')
    source_dir = pathlib.Path(data_folder)

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):

        print(f"Step 1/3: pending_upload(name=`{model_name}`, version=`{model_version}`)")
        pending = await project_client.beta.models.pending_upload(
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
        async with ContainerClient.from_container_url(sas_uri) as container_client:
            for f in [p for p in source_dir.rglob("*") if p.is_file()]:
                rel = f.relative_to(source_dir).as_posix()
                with f.open("rb") as fp:
                    await container_client.upload_blob(name=rel, data=fp, overwrite=True)
                print(f"  uploaded {rel} ({f.stat().st_size} bytes)")

        print(f"Step 3/3: create_async(name=`{model_name}`, version=`{model_version}`)")
        await project_client.beta.models.create_async(
            name=model_name,
            version=model_version,
            body=ModelVersion(
                blob_uri=container_blob_uri,
                weight_type=FoundryModelWeightType.FULL_WEIGHT,
                description="Sample model registered from sample_models_async.py",
                tags={"source": "sample_models_async.py"},
            ),
        )

        # `create_async` returns 202 Accepted; poll `get` until the committed
        # ModelVersion is observable.
        print(f"Polling get(`{model_name}`, `{model_version}`) until the ModelVersion is committed...")
        deadline = time.monotonic() + 300.0
        model: ModelVersion
        while True:
            try:
                model = await project_client.beta.models.get(name=model_name, version=model_version)
                break
            except ResourceNotFoundError:
                if time.monotonic() >= deadline:
                    raise RuntimeError(
                        f"Model `{model_name}`@`{model_version}` did not appear within 300s after create_async."
                    )
                await asyncio.sleep(2.0)
        print(model)

        print(f"List all versions of model `{model_name}`:")
        async for mv in project_client.beta.models.list_versions(name=model_name):
            print(f"  - {mv.version}")

        print("List the latest version of every registered model in this project:")
        async for mv in project_client.beta.models.list():
            print(f"  - {mv.name}@{mv.version}")

        print(f"Get blob credentials for `{model_name}`@`{model_version}`:")
        creds = await project_client.beta.models.get_credentials(
            name=model_name,
            version=model_version,
            body=ModelCredentialRequest(blob_uri=model.blob_uri),
        )
        print(creds)

        print(f"Update description and tags on `{model_name}`@`{model_version}`:")
        updated = await project_client.beta.models.update(
            name=model_name,
            version=model_version,
            body=UpdateModelVersionRequest(
                description="Updated description",
                tags={"source": "sample_models_async.py", "updated": "true"},
            ),
        )
        print(updated)

        print(f"Delete the model version created above (`{model_name}`@`{model_version}`):")
        await project_client.beta.models.delete(name=model_name, version=model_version)


if __name__ == "__main__":
    asyncio.run(main())

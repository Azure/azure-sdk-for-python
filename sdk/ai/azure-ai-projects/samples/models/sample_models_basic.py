# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `.beta.models` operations to register a local model with a Microsoft Foundry
    project, list and inspect model versions, retrieve storage credentials,
    update version metadata, and delete a model version.

    The recommended entry point is the patched helper
    `project_client.beta.models.create(...)`, which packs the spec's
    three required steps (`pending_upload` -> `azcopy copy` -> `pending_create_version`)
    into a single call and polls until the new ModelVersion is observable.

USAGE:
    python sample_models_basic.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity python-dotenv

    AzCopy must also be installed and on PATH (used by `create` to
    upload weight files):

        winget install --id Microsoft.Azure.AZCopy.10 -e

    See https://aka.ms/downloadazcopy for other platforms.

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as
       found in the overview page of your Microsoft Foundry project.
    2) MODEL_NAME - Optional. The name of the model to register. Defaults to
       "sample-model".
    3) MODEL_VERSION - Optional. The version of the model to register.
       Defaults to "1".
    4) DATA_FOLDER - Optional. The folder containing the local weight files
       to upload. Defaults to a temp folder created with two tiny dummy files.
"""

import os
import pathlib
import tempfile

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    FoundryModelWeightType,
    ModelCredentialRequest,
    UpdateModelVersionRequest,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ.get("MODEL_NAME", "sample-model")
model_version = os.environ.get("MODEL_VERSION", "1")

# Construct the path to the local folder of weight files used in this sample.
data_folder = os.environ.get("DATA_FOLDER")
if not data_folder:
    data_folder = tempfile.mkdtemp(prefix="sample-model-")
    (pathlib.Path(data_folder) / "weights.bin").write_bytes(b"hello-foundry-model")
    (pathlib.Path(data_folder) / "config.json").write_text('{"sample": true}')

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    print(
        f"Register a local model named `{model_name}` version `{model_version}` "
        f"by uploading the contents of `{data_folder}` via `create`."
    )
    model = project_client.beta.models.create(
        name=model_name,
        version=model_version,
        source=data_folder,
        weight_type=FoundryModelWeightType.FULL_WEIGHT,
        description="Sample model registered from sample_models_basic.py",
        tags={"source": "sample_models_basic.py"},
    )
    print(f"Created (name: {model.name}, version: {model.version}, blob_uri: {model.blob_uri})")

    print(f"Get a specific model version `{model_name}`@`{model_version}`:")
    fetched = project_client.beta.models.get(name=model_name, version=model_version)
    print(f"Fetched (name: {fetched.name}, version: {fetched.version}, blob_uri: {fetched.blob_uri})")

    print(f"List all versions of model `{model_name}`:")
    for mv in project_client.beta.models.list_versions(name=model_name):
        print(f"  - {mv.version}")

    print("List the latest version of every registered model in this project:")
    for mv in project_client.beta.models.list():
        print(f"  - {mv.name}@{mv.version}")

    print(f"Get blob credentials for `{model_name}`@`{model_version}`:")
    creds = project_client.beta.models.get_credentials(
        name=model_name,
        version=model_version,
        credential_request=ModelCredentialRequest(blob_uri=model.blob_uri),
    )
    print(f"Credentials (type: {type(creds).__name__})")

    print(f"Update description and tags on `{model_name}`@`{model_version}`:")
    updated = project_client.beta.models.update(
        name=model_name,
        version=model_version,
        model_version_update=UpdateModelVersionRequest(
            description="Updated description",
            tags={"source": "sample_models_basic.py", "updated": "true"},
        ),
    )
    print(f"Updated (name: {updated.name}, version: {updated.version}, description: {updated.description})")

    print(f"Delete the model version created above (`{model_name}`@`{model_version}`):")
    project_client.beta.models.delete(name=model_name, version=model_version)
